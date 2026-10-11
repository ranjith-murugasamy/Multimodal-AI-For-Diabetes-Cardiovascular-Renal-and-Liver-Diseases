"""Reproducible baseline experiment for the four E-XMAI disease areas.

Compares LightGBM, CatBoost and Random Forest on four public OpenML tabular
datasets (one per disease area) using repeated stratified cross-validation, and
computes SHAP summaries for the LightGBM model. All preprocessing is fitted
inside the training folds. Nothing is tuned on held-out data and the decision
threshold is fixed at 0.5.

Usage:  .venv/bin/python scripts/run_experiments.py
Output: output/results/experiment_results.json, per_fold_metrics.csv,
        shap_top_features.csv, figures in output/results/figures/
"""
from __future__ import annotations

import json
import time
import warnings
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "results"
FIG = OUT / "figures"
SEED = 20261011
N_SPLITS, N_REPEATS = 5, 5

# disease area -> (OpenML data id, positive-class label, columns to drop)
DATASETS = {
    "Diabetes": dict(data_id=37, positive="tested_positive", name="Pima Indians Diabetes", drop=[]),
    "Cardiovascular": dict(data_id=53, positive="present", name="Statlog (Heart)", drop=[]),
    "Renal": dict(data_id=42972, positive="ckd", name="Chronic Kidney Disease", drop=["id"]),
    "Liver": dict(data_id=1480, positive="1", name="ILPD (Indian Liver Patient)", drop=[]),
}


# OpenML column codes -> descriptive names (ILPD order: UCI 'ILPD' documentation)
RENAMES = {
    37: {"preg": "pregnancies", "plas": "glucose", "pres": "diastolic_bp", "skin": "skin_fold",
         "insu": "insulin", "mass": "bmi", "pedi": "pedigree_function"},
    1480: {"V1": "age", "V2": "gender", "V3": "total_bilirubin", "V4": "direct_bilirubin",
           "V5": "alk_phosphatase", "V6": "sgpt_alt", "V7": "sgot_ast", "V8": "total_protein",
           "V9": "albumin", "V10": "albumin_globulin_ratio"},
    42972: {"bp": "blood_pressure", "sg": "specific_gravity", "al": "albumin", "su": "sugar",
            "bgr": "blood_glucose", "bu": "blood_urea", "sc": "serum_creatinine", "sod": "sodium",
            "pot": "potassium", "hemo": "hemoglobin", "pcv": "packed_cell_volume",
            "wc": "wbc_count", "rc": "rbc_count", "htn": "hypertension", "dm": "diabetes_mellitus",
            "cad": "coronary_artery_disease", "pe": "pedal_edema", "ane": "anemia"},
}


def load(spec: dict) -> tuple[pd.DataFrame, np.ndarray]:
    if spec["data_id"] == 42972:
        frame = fetch_openml(data_id=42972, as_frame=True, parser="auto", target_column=None).frame
        target = frame.pop("classification").astype(str).str.strip().str.strip("'")
        target = target.replace({"ckdt": "ckd"})
    else:
        bunch = fetch_openml(data_id=spec["data_id"], as_frame=True, parser="auto")
        frame, target = bunch.data.copy(), bunch.target.astype(str)
    frame = frame.drop(columns=spec["drop"]).rename(columns=RENAMES.get(spec["data_id"], {}))
    for col in frame.columns:
        if frame[col].dtype == object or str(frame[col].dtype) in ("str", "string", "category"):
            cleaned = frame[col].astype(str).str.strip().str.strip("'").replace({"?": np.nan, "nan": np.nan, "": np.nan})
            numeric = pd.to_numeric(cleaned, errors="coerce")
            frame[col] = numeric if numeric.notna().sum() >= 0.9 * cleaned.notna().sum() else cleaned
    y = (target.values == spec["positive"]).astype(int)
    return frame.reset_index(drop=True), y


def preprocessor(frame: pd.DataFrame) -> ColumnTransformer:
    cat = [c for c in frame.columns if frame[c].dtype == object or str(frame[c].dtype) in ("str", "string", "category")]
    num = [c for c in frame.columns if c not in cat]
    steps = [("num", SimpleImputer(strategy="median"), num)]
    if cat:
        steps.append(
            (
                "cat",
                Pipeline(
                    [
                        ("imp", SimpleImputer(strategy="most_frequent")),
                        ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                cat,
            )
        )
    return ColumnTransformer(steps, verbose_feature_names_out=False)


def models(seed: int) -> dict:
    return {
        "LightGBM": LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=15,
                                   min_child_samples=10, random_state=seed, verbose=-1),
        "CatBoost": CatBoostClassifier(iterations=300, learning_rate=0.05, depth=4,
                                       random_seed=seed, verbose=0, allow_writing_files=False),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=seed, n_jobs=1),
    }


def metrics(y, prob) -> dict:
    pred = (prob >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "accuracy": accuracy_score(y, pred),
        "sensitivity": tp / (tp + fn) if tp + fn else np.nan,
        "specificity": tn / (tn + fp) if tn + fp else np.nan,
        "f1": f1_score(y, pred, zero_division=0),
        "auroc": roc_auc_score(y, prob),
        "auprc": average_precision_score(y, prob),
        "brier": brier_score_loss(y, prob),
    }


def corrected_t(diff: np.ndarray, n_train: int, n_test: int) -> tuple[float, float]:
    """Nadeau & Bengio corrected resampled t-test on paired per-fold differences."""
    k = len(diff)
    var = diff.var(ddof=1)
    if var == 0:
        return 0.0, 1.0
    t = diff.mean() / np.sqrt((1 / k + n_test / n_train) * var)
    return float(t), float(2 * stats.t.sf(abs(t), k - 1))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    rows, shap_rows, summary, tests, dataset_info = [], [], {}, [], {}
    shap_stability = {}
    started = time.time()

    for disease, spec in DATASETS.items():
        X, y = load(spec)
        dataset_info[disease] = {
            "source": spec["name"], "openml_id": spec["data_id"], "n": int(len(y)),
            "features": int(X.shape[1]), "positives": int(y.sum()),
            "prevalence": round(float(y.mean()), 3),
            "missing_cells": int(X.isna().sum().sum()),
            "categorical_features": int(sum(X[c].dtype == object or str(X[c].dtype) in ("str", "string", "category") for c in X.columns)),
        }
        print(f"== {disease}: {dataset_info[disease]}", flush=True)
        cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
        fold_top = []
        for fold, (tr, te) in enumerate(cv.split(X, y)):
            for name, clf in models(SEED + fold).items():
                pipe = Pipeline([("prep", preprocessor(X)), ("clf", clf)])
                t0 = time.time()
                pipe.fit(X.iloc[tr], y[tr])
                fit_s = time.time() - t0
                t0 = time.time()
                prob = pipe.predict_proba(X.iloc[te])[:, 1]
                rows.append({"disease": disease, "model": name, "fold": fold,
                             "n_train": len(tr), "n_test": len(te), "fit_seconds": fit_s,
                             "predict_seconds": time.time() - t0, **metrics(y[te], prob)})
                if name == "LightGBM":
                    Xt = pipe.named_steps["prep"].transform(X.iloc[te])
                    names = pipe.named_steps["prep"].get_feature_names_out()
                    sv = shap.TreeExplainer(pipe.named_steps["clf"]).shap_values(Xt)
                    sv = sv[1] if isinstance(sv, list) else sv
                    imp = pd.Series(np.abs(sv).mean(axis=0), index=names)
                    fold_top.append(imp)
        imp_df = pd.concat(fold_top, axis=1)
        mean_imp = imp_df.mean(axis=1).sort_values(ascending=False)
        top_sets = [set(imp_df[c].nlargest(5).index) for c in imp_df]
        jac = [len(a & b) / len(a | b) for a, b in combinations(top_sets, 2)]
        shap_stability[disease] = {"top5_jaccard_mean": float(np.mean(jac)), "top5_jaccard_sd": float(np.std(jac))}
        for feat, val in mean_imp.head(8).items():
            shap_rows.append({"disease": disease, "feature": feat, "mean_abs_shap": float(val),
                              "rank_sd": float(imp_df.rank(ascending=False).loc[feat].std())})

    per_fold = pd.DataFrame(rows)
    per_fold.to_csv(OUT / "per_fold_metrics.csv", index=False)
    pd.DataFrame(shap_rows).to_csv(OUT / "shap_top_features.csv", index=False)

    mcols = ["accuracy", "sensitivity", "specificity", "f1", "auroc", "auprc", "brier"]
    for (d, m), g in per_fold.groupby(["disease", "model"]):
        entry = {}
        for c in mcols:
            v = g[c].dropna().values
            ci = stats.t.interval(0.95, len(v) - 1, loc=v.mean(), scale=stats.sem(v)) if len(v) > 1 else (np.nan, np.nan)
            entry[c] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "ci95_low": float(ci[0]), "ci95_high": float(ci[1])}
        entry["fit_seconds_mean"] = float(g["fit_seconds"].mean())
        entry["predict_seconds_mean"] = float(g["predict_seconds"].mean())
        summary.setdefault(d, {})[m] = entry

    for d, g in per_fold.groupby("disease"):
        piv = g.pivot(index="fold", columns="model", values="auroc")
        n_tr, n_te = int(g.n_train.iloc[0]), int(g.n_test.iloc[0])
        for a, b in combinations(piv.columns, 2):
            t, p = corrected_t((piv[a] - piv[b]).values, n_tr, n_te)
            tests.append({"disease": d, "comparison": f"{a} vs {b}", "metric": "auroc",
                          "mean_diff": float((piv[a] - piv[b]).mean()), "t": t, "p_corrected": p})
    # Holm correction across all 12 comparisons
    order = np.argsort([t["p_corrected"] for t in tests])
    m = len(tests)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank) * tests[idx]["p_corrected"]))
        tests[idx]["p_holm"] = running

    result = {
        "protocol": {
            "cv": f"{N_REPEATS}x repeated stratified {N_SPLITS}-fold", "seed": SEED, "threshold": 0.5,
            "preprocessing": "median/mode imputation and one-hot encoding fitted within training folds only",
            "tuning": "none (fixed hyperparameters, not selected on held-out folds)",
            "significance": "Nadeau-Bengio corrected resampled t-test on per-fold AUROC, Holm-adjusted over 12 comparisons",
            "runtime_seconds": round(time.time() - started, 1),
        },
        "datasets": dataset_info, "summary": summary, "tests": tests, "shap_stability": shap_stability,
    }
    (OUT / "experiment_results.json").write_text(json.dumps(result, indent=2))

    # Figures -------------------------------------------------------------
    colors = {"LightGBM": "#487798", "CatBoost": "#bb653d", "Random Forest": "#758749"}
    fig, ax = plt.subplots(figsize=(7, 3.4))
    diseases = list(DATASETS)
    w = 0.26
    for i, m_ in enumerate(colors):
        means = [summary[d][m_]["auroc"]["mean"] for d in diseases]
        sds = [summary[d][m_]["auroc"]["sd"] for d in diseases]
        ax.bar(np.arange(4) + (i - 1) * w, means, w, yerr=sds, capsize=2, label=m_, color=colors[m_])
    ax.set_xticks(range(4), diseases)
    ax.set_ylim(0.5, 1.12)
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_ylabel("AUROC")
    ax.legend(frameon=False, ncol=3, loc="upper center", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig_auroc.png", dpi=300)
    plt.close(fig)

    shap_df = pd.DataFrame(shap_rows)
    fig, axes = plt.subplots(1, 4, figsize=(10, 3), sharex=False)
    for ax, d in zip(axes, diseases):
        s = shap_df[shap_df.disease == d].head(5).iloc[::-1]
        ax.barh(s.feature, s.mean_abs_shap, color="#487798")
        ax.set_title(d, fontsize=9)
        ax.tick_params(labelsize=7)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_xlabel("mean |SHAP|", fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig_shap.png", dpi=300)
    plt.close(fig)
    print(f"done in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
