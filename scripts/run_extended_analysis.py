"""Extended analyses requested by the base paper's step-by-step workflow.

Adds to run_experiments.py: ROC/PR and calibration curves, missing-data
robustness, disease-wise feature-association networks (+ centrality), a
network-feature ablation, SHAP summary / local / cross-disease figures and model
cost. Same datasets, seed, and leakage rules (everything fitted on training
folds only; the descriptive full-data networks and SHAP summaries are labelled
descriptive and never feed an evaluation).

Usage: .venv/bin/python scripts/run_extended_analysis.py
"""
from __future__ import annotations

import json
import pickle
import sys
import time
import warnings
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import shap
from scipy import stats
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, f1_score, precision_recall_curve, roc_auc_score, roc_curve
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_experiments import DATASETS, FIG, OUT, SEED, corrected_t, load, models, preprocessor  # noqa: E402

warnings.filterwarnings("ignore")
COL = {"LightGBM": "#487798", "CatBoost": "#bb653d", "Random Forest": "#758749"}
EDGE_THRESHOLD = 0.30
MISS_LEVELS = [0.0, 0.1, 0.2, 0.3, 0.4]
DIS = list(DATASETS)


class NetworkScores(BaseEstimator, TransformerMixin):
    """Training-fold feature-association network -> community score features."""

    def __init__(self, threshold=EDGE_THRESHOLD, keep_original=True):
        self.threshold = threshold
        self.keep_original = keep_original

    def fit(self, X, y):
        X = np.asarray(X, float)
        self.mu_, self.sd_ = X.mean(0), X.std(0) + 1e-9
        Z = (X - self.mu_) / self.sd_
        rho = pd.DataFrame(Z).corr(method="spearman").fillna(0).values
        g = nx.Graph()
        g.add_nodes_from(range(X.shape[1]))
        for i, j in combinations(range(X.shape[1]), 2):
            if abs(rho[i, j]) >= self.threshold:
                g.add_edge(i, j, weight=abs(rho[i, j]))
        comms = [sorted(c) for c in nx.algorithms.community.greedy_modularity_communities(g, weight="weight")
                 if len(c) >= 2]
        self.groups_ = comms
        yv = np.asarray(y, float)
        self.signs_ = []
        for c in comms:
            s = []
            for j in c:
                r = stats.spearmanr(Z[:, j], yv)[0]
                s.append(1.0 if not np.isfinite(r) or r >= 0 else -1.0)
            self.signs_.append(np.array(s))
        return self

    def transform(self, X):
        X = np.asarray(X, float)
        Z = (X - self.mu_) / self.sd_
        scores = [ (Z[:, c] * s).mean(1) for c, s in zip(self.groups_, self.signs_) ]
        S = np.column_stack(scores) if scores else np.zeros((len(X), 0))
        return np.hstack([X, S]) if self.keep_original else S


def ece(y, p, bins=5):
    edges = np.quantile(p, np.linspace(0, 1, bins + 1))
    idx = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, bins - 1)
    return float(sum((idx == b).mean() * abs(y[idx == b].mean() - p[idx == b].mean())
                     for b in range(bins) if (idx == b).any()))


def fit_pipe(clf, X, y):
    return Pipeline([("prep", preprocessor(X)), ("clf", clf)]).fit(X, y)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    out: dict = {"protocol": {"edge_threshold": EDGE_THRESHOLD, "missingness_levels": MISS_LEVELS,
                              "robustness_cv": "5-fold x 2 repeats, test-time MCAR missingness, imputation fitted on training folds",
                              "ablation_cv": "5-fold x 5 repeats, LightGBM and Random Forest, corrected t-test on AUROC"},
                 "calibration": {}, "robustness": {}, "networks": {}, "ablation": {}, "cost": {}}
    data = {d: load(s) for d, s in DATASETS.items()}
    t_start = time.time()

    # ---- ROC / PR / calibration (pooled out-of-fold predictions, one 5-fold pass)
    fig_rp, ax_rp = plt.subplots(2, 4, figsize=(11, 5))
    fig_cal, ax_cal = plt.subplots(1, 4, figsize=(11, 2.9))
    oof_models = {}
    for k, d in enumerate(DIS):
        X, y = data[d]
        oof = {m: np.zeros(len(y)) for m in COL}
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED).split(X, y):
            for m, clf in models(SEED).items():
                oof[m][te] = fit_pipe(clf, X.iloc[tr], y[tr]).predict_proba(X.iloc[te])[:, 1]
        out["calibration"][d] = {}
        for m, p in oof.items():
            fpr, tpr, _ = roc_curve(y, p)
            pr, rc, _ = precision_recall_curve(y, p)
            ax_rp[0, k].plot(fpr, tpr, color=COL[m], label=m, lw=1.4)
            ax_rp[1, k].plot(rc, pr, color=COL[m], lw=1.4)
            fy, fx = calibration_curve(y, p, n_bins=5, strategy="quantile")
            ax_cal[k].plot(fx, fy, "o-", color=COL[m], ms=3, lw=1.2, label=m)
            out["calibration"][d][m] = {"ece_5bin": ece(y, p), "oof_auroc": float(roc_auc_score(y, p)),
                                        "oof_auprc": float(average_precision_score(y, p))}
        ax_rp[0, k].plot([0, 1], [0, 1], "--", color="#999", lw=0.8)
        ax_rp[1, k].axhline(y.mean(), ls="--", color="#999", lw=0.8)
        ax_rp[0, k].set_title(d, fontsize=9)
        ax_cal[k].plot([0, 1], [0, 1], "--", color="#999", lw=0.8)
        ax_cal[k].set_title(d, fontsize=9)
        ax_cal[k].set_xlabel("Mean predicted probability", fontsize=7)
        oof_models[d] = oof
    ax_rp[0, 0].set_ylabel("Sensitivity", fontsize=8)
    ax_rp[1, 0].set_ylabel("Precision", fontsize=8)
    for k in range(4):
        ax_rp[1, k].set_xlabel("Recall", fontsize=8)
        ax_rp[0, k].set_xlabel("1 − specificity", fontsize=8)
    ax_rp[0, 0].legend(fontsize=6, frameon=False, loc="lower right")
    ax_cal[0].set_ylabel("Observed fraction positive", fontsize=7)
    ax_cal[0].legend(fontsize=6, frameon=False)
    for a in list(ax_rp.ravel()) + list(ax_cal):
        a.tick_params(labelsize=7)
        a.spines[["top", "right"]].set_visible(False)
    fig_rp.tight_layout(); fig_rp.savefig(FIG / "fig_roc_pr.png", dpi=300); plt.close(fig_rp)
    fig_cal.tight_layout(); fig_cal.savefig(FIG / "fig_calibration.png", dpi=300); plt.close(fig_cal)
    print("curves done", flush=True)

    # ---- Missing-data robustness
    rng = np.random.default_rng(SEED)
    fig, axes = plt.subplots(1, 4, figsize=(11, 2.9), sharey=False)
    for k, d in enumerate(DIS):
        X, y = data[d]
        res = {m: {lv: [] for lv in MISS_LEVELS} for m in COL}
        cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=SEED)
        for f, (tr, te) in enumerate(cv.split(X, y)):
            fitted = {m: fit_pipe(clf, X.iloc[tr], y[tr]) for m, clf in models(SEED + f).items()}
            for lv in MISS_LEVELS:
                Xt = X.iloc[te].copy()
                if lv > 0:
                    mask = rng.random(Xt.shape) < lv
                    Xt = Xt.mask(pd.DataFrame(mask, index=Xt.index, columns=Xt.columns))
                for m, pipe in fitted.items():
                    res[m][lv].append(roc_auc_score(y[te], pipe.predict_proba(Xt)[:, 1]))
        out["robustness"][d] = {m: {str(lv): {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1))}
                                    for lv, v in lvs.items()} for m, lvs in res.items()}
        for m in COL:
            axes[k].errorbar([int(l * 100) for l in MISS_LEVELS], [np.mean(res[m][l]) for l in MISS_LEVELS],
                             yerr=[np.std(res[m][l], ddof=1) for l in MISS_LEVELS], color=COL[m], label=m,
                             marker="o", ms=3, lw=1.2, capsize=2)
        axes[k].set_title(d, fontsize=9)
        axes[k].set_xlabel("Cells missing at test time (%)", fontsize=7)
        axes[k].tick_params(labelsize=7)
        axes[k].spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("AUROC", fontsize=8)
    axes[0].legend(fontsize=6, frameon=False)
    fig.tight_layout(); fig.savefig(FIG / "fig_robustness.png", dpi=300); plt.close(fig)
    print("robustness done", flush=True)

    # ---- Descriptive feature-association networks (full data; not used for evaluation)
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4))
    cent_rows = []
    for k, d in enumerate(DIS):
        X, y = data[d]
        prep = preprocessor(X).fit(X)
        M = pd.DataFrame(prep.transform(X), columns=prep.get_feature_names_out())
        M = M.loc[:, M.std() > 0]
        rho = M.corr(method="spearman").fillna(0)
        g = nx.Graph()
        g.add_nodes_from(M.columns)
        for a, b in combinations(M.columns, 2):
            if abs(rho.loc[a, b]) >= EDGE_THRESHOLD:
                g.add_edge(a, b, weight=float(abs(rho.loc[a, b])), dist=1 / float(abs(rho.loc[a, b])))
        strength = dict(g.degree(weight="weight"))
        btw = nx.betweenness_centrality(g, weight="dist")
        comms = [sorted(c) for c in nx.algorithms.community.greedy_modularity_communities(g, weight="weight")]
        top = sorted(strength, key=strength.get, reverse=True)[:3]
        out["networks"][d] = {"nodes": g.number_of_nodes(), "edges": g.number_of_edges(),
                              "density": round(nx.density(g), 3),
                              "communities": len([c for c in comms if len(c) > 1]),
                              "top_central_features": top,
                              "modularity": round(nx.algorithms.community.modularity(g, comms, weight="weight"), 3)}
        for n in g.nodes:
            cent_rows.append({"disease": d, "feature": n, "strength": strength[n], "betweenness": btw[n]})
        pos = nx.spring_layout(g, seed=7, weight="weight", k=0.9)
        cmap = {n: i for i, c in enumerate(comms) for n in c}
        palette = ["#487798", "#bb653d", "#758749", "#b74755", "#8c6bb1", "#999999", "#d4a017"]
        nx.draw_networkx_edges(g, pos, ax=axes[k], width=[1.5 * g[u][v]["weight"] for u, v in g.edges], alpha=0.5)
        nx.draw_networkx_nodes(g, pos, ax=axes[k], node_size=[30 + 40 * strength[n] for n in g.nodes],
                               node_color=[palette[cmap[n] % len(palette)] for n in g.nodes])
        nx.draw_networkx_labels(g, pos, ax=axes[k], font_size=4.5,
                                labels={n: n.replace("_", " ")[:14] for n in top})
        axes[k].set_title(f"{d} ({g.number_of_nodes()} nodes, {g.number_of_edges()} edges)", fontsize=8)
        axes[k].axis("off")
    fig.tight_layout(); fig.savefig(FIG / "fig_networks.png", dpi=300); plt.close(fig)
    cent = pd.DataFrame(cent_rows)
    cent.to_csv(OUT / "network_centrality.csv", index=False)
    fig, axes = plt.subplots(1, 4, figsize=(11, 2.8))
    for k, d in enumerate(DIS):
        s = cent[cent.disease == d].nlargest(5, "strength").iloc[::-1]
        axes[k].barh(s.feature.str.replace("_", " "), s.strength, color="#487798")
        axes[k].set_title(d, fontsize=9)
        axes[k].tick_params(labelsize=7)
        axes[k].spines[["top", "right"]].set_visible(False)
    axes[0].set_xlabel("weighted degree", fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "fig_centrality.png", dpi=300); plt.close(fig)
    print("networks done", flush=True)

    # ---- Ablation: baseline vs +network-derived features vs network-only
    variants = {"Baseline (original features)": None, "Original + network scores": True, "Network scores only": False}
    learners = {
        "LightGBM": lambda s: models(s)["LightGBM"],
        "Random Forest": lambda s: RandomForestClassifier(n_estimators=300, random_state=s, n_jobs=1),
    }
    abl_rows = []
    for d in DIS:
        X, y = data[d]
        cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED)
        for f, (tr, te) in enumerate(cv.split(X, y)):
            for lname, mk in learners.items():
                for vname, keep in variants.items():
                    steps = [("prep", preprocessor(X))]
                    if keep is not None:
                        steps.append(("net", NetworkScores(keep_original=keep)))
                    pipe = Pipeline(steps + [("clf", mk(SEED + f))]).fit(X.iloc[tr], y[tr])
                    pr = pipe.predict_proba(X.iloc[te])[:, 1]
                    abl_rows.append({"disease": d, "learner": lname, "variant": vname, "fold": f,
                                     "n_train": len(tr), "n_test": len(te),
                                     "auroc": roc_auc_score(y[te], pr), "f1": f1_score(y[te], pr >= 0.5)})
    abl = pd.DataFrame(abl_rows)
    abl.to_csv(OUT / "ablation_per_fold.csv", index=False)
    for (d, l, v), g in abl.groupby(["disease", "learner", "variant"]):
        out["ablation"].setdefault(d, {}).setdefault(l, {})[v] = {
            "auroc_mean": float(g.auroc.mean()), "auroc_sd": float(g.auroc.std(ddof=1)),
            "f1_mean": float(g.f1.mean()), "f1_sd": float(g.f1.std(ddof=1))}
    tests = []
    for (d, l), g in abl.groupby(["disease", "learner"]):
        piv = g.pivot(index="fold", columns="variant", values="auroc")
        diff = (piv["Original + network scores"] - piv["Baseline (original features)"]).values
        t, p = corrected_t(diff, int(g.n_train.iloc[0]), int(g.n_test.iloc[0]))
        tests.append({"disease": d, "learner": l, "mean_diff": float(diff.mean()), "t": t, "p": p})
    order = np.argsort([t["p"] for t in tests]); run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(tests) - r) * tests[i]["p"])); tests[i]["p_holm"] = run
    out["ablation_tests"] = tests
    print("ablation done", flush=True)

    # ---- SHAP: summary (descriptive), local explanations, cross-disease
    fig_sum, ax_sum = plt.subplots(1, 4, figsize=(13, 3.6))
    fig_loc, ax_loc = plt.subplots(2, 4, figsize=(12, 5))
    heat = {}
    for k, d in enumerate(DIS):
        X, y = data[d]
        pipe = fit_pipe(models(SEED)["LightGBM"], X, y)
        Xt = pipe.named_steps["prep"].transform(X)
        names = [n.replace("_", " ") for n in pipe.named_steps["prep"].get_feature_names_out()]
        sv = shap.TreeExplainer(pipe.named_steps["clf"]).shap_values(Xt)
        sv = sv[1] if isinstance(sv, list) else sv
        sv = np.asarray(sv)
        imp = pd.Series(np.abs(sv).mean(0), index=names).sort_values(ascending=False)
        heat[d] = (imp / imp.sum()).head(6)
        order_f = list(imp.index[:6])[::-1]
        plt.sca(ax_sum[k])
        for r, fname in enumerate(order_f):
            j = names.index(fname)
            v = Xt[:, j]
            rng_v = (v - v.min()) / (np.ptp(v) + 1e-9)
            ax_sum[k].scatter(sv[:, j], r + rng.uniform(-0.25, 0.25, len(v)), c=rng_v, cmap="coolwarm", s=5,
                              alpha=0.8, linewidths=0)
        ax_sum[k].set_yticks(range(len(order_f)), order_f, fontsize=6)
        ax_sum[k].axvline(0, color="#999", lw=0.6)
        ax_sum[k].set_title(d, fontsize=9)
        ax_sum[k].tick_params(labelsize=6)
        ax_sum[k].spines[["top", "right"]].set_visible(False)
        # local explanations from a held-out split (model never saw the case)
        tr, te = next(StratifiedKFold(5, shuffle=True, random_state=SEED).split(X, y))
        lp = fit_pipe(models(SEED)["LightGBM"], X.iloc[tr], y[tr])
        Xte = lp.named_steps["prep"].transform(X.iloc[te])
        names_l = [n.replace("_", " ") for n in lp.named_steps["prep"].get_feature_names_out()]
        prob = lp.predict_proba(X.iloc[te])[:, 1]
        sv_l = shap.TreeExplainer(lp.named_steps["clf"]).shap_values(Xte)
        sv_l = np.asarray(sv_l[1] if isinstance(sv_l, list) else sv_l)
        yt = y[te]
        picks = [("True positive", int(np.argmax(np.where(yt == 1, prob, -1)))),
                 ("True negative", int(np.argmin(np.where(yt == 0, prob, 2))))]
        for row, (lab, i) in enumerate(picks):
            top = np.argsort(-np.abs(sv_l[i]))[:6][::-1]
            ax_loc[row, k].barh([f"{names_l[j]} = {Xte[i, j]:.3g}" for j in top], sv_l[i, top],
                                color=["#b74755" if v > 0 else "#487798" for v in sv_l[i, top]])
            ax_loc[row, k].set_title(f"{d}: {lab} (p = {prob[i]:.2f})", fontsize=7.5)
            ax_loc[row, k].tick_params(labelsize=6)
            ax_loc[row, k].spines[["top", "right"]].set_visible(False)
            ax_loc[row, k].axvline(0, color="#999", lw=0.6)
    ax_loc[1, 0].set_xlabel("SHAP value (log-odds)", fontsize=7)
    fig_sum.tight_layout(); fig_sum.savefig(FIG / "fig_shap_summary.png", dpi=300); plt.close(fig_sum)
    fig_loc.tight_layout(); fig_loc.savefig(FIG / "fig_shap_local.png", dpi=300); plt.close(fig_loc)
    union = list(dict.fromkeys(f for d in DIS for f in heat[d].index))
    H = pd.DataFrame({d: heat[d].reindex(union) for d in DIS})
    fig, ax = plt.subplots(figsize=(5.5, 0.28 * len(union) + 1))
    im = ax.imshow(H.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(4), DIS, fontsize=7); ax.set_yticks(range(len(union)), union, fontsize=6.5)
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            if np.isfinite(H.values[i, j]):
                ax.text(j, i, f"{H.values[i, j]:.2f}", ha="center", va="center", fontsize=6)
    ax.set_title("Share of total mean |SHAP| (top-6 per disease)", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "fig_shap_cross_disease.png", dpi=300); plt.close(fig)
    print("shap done", flush=True)

    # ---- Model cost
    for d in DIS:
        X, y = data[d]
        out["cost"][d] = {}
        for m, clf in models(SEED).items():
            t0 = time.time(); pipe = fit_pipe(clf, X, y); fit_s = time.time() - t0
            t0 = time.time()
            for _ in range(5):
                pipe.predict_proba(X)
            per_1000 = (time.time() - t0) / 5 / len(X) * 1000
            out["cost"][d][m] = {"fit_seconds_full": fit_s, "predict_seconds_per_1000": per_1000,
                                 "model_kb": len(pickle.dumps(pipe)) / 1024}
    out["runtime_seconds"] = round(time.time() - t_start, 1)
    (OUT / "extended_results.json").write_text(json.dumps(out, indent=2))
    print("done", out["runtime_seconds"])


if __name__ == "__main__":
    main()
