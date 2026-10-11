"""Build the manuscript (clean DOCX + PDF) and a change-highlighted PDF.

Numbers are read from output/results/*.json|csv; citations are numbered
automatically in order of first appearance.

    .venv/bin/python scripts/build_paper.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docgen import build_docx, build_pdf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "output" / "results"
FIGS = RES / "figures"
SHOTS = ROOT / "output" / "screenshots"
OUT = ROOT / "output" / "paper" / "final"
OUT.mkdir(parents=True, exist_ok=True)

R = json.loads((RES / "experiment_results.json").read_text())
E = json.loads((RES / "extended_results.json").read_text())
SHAP = pd.read_csv(RES / "shap_top_features.csv")
S, D, T = R["summary"], R["datasets"], R["tests"]
DIS = list(D)
MOD = ["LightGBM", "CatBoost", "Random Forest"]
TITLE = ("Network-Assisted Tree-Ensemble Baselines and SHAP Explanations for Diabetes, Cardiovascular, "
         "Renal and Liver Disease: A Reproducible Foundation for an Expandable Explainable Framework")

CHANGES = [  # id, base-paper plan / proposal element, what this manuscript does
    ("C1", "Title and abstract claim a multimodal framework for four diseases.",
     "Scope narrowed: four separate public single-disease datasets are not a linked multimodal cohort (the base paper's own caution); 'multimodal' is confined to the demonstrator."),
    ("C2", "Paper 1 lists LightGBM, CatBoost and TabNet; the journal workflow lists LightGBM, CatBoost and Random Forest.",
     "Followed the journal workflow (LightGBM, CatBoost, Random Forest). TabNet not run; stated as a limitation."),
    ("C3", "Workflow: consistent protocol, no test-set thresholds, preprocessing on training data only.",
     "5x5 repeated stratified CV, in-fold imputation/encoding, fixed 0.5 threshold, no tuning on held-out data."),
    ("C4", "Workflow Table 6: confidence intervals and paired statistical tests.",
     "95% t-intervals; Nadeau-Bengio corrected resampled t-test with Holm adjustment."),
    ("C5", "Workflow Step 4: disease-specific feature-association networks, centrality, communities.",
     "Spearman networks (|rho| >= 0.30) per disease with strength/betweenness centrality and modularity communities."),
    ("C6", "Workflow Step 5: network-derived features and ablation (baseline vs proposed variants).",
     "Training-fold community scores added to the original features; three-variant ablation with corrected tests."),
    ("C7", "Workflow Step 6: SHAP summary, local explanations, cross-disease comparison, stability.",
     "SHAP summary, held-out local explanations, cross-disease heatmap, top-5 Jaccard stability."),
    ("C8", "Workflow Step 7: ROC/PR, calibration, missing-data robustness.",
     "Out-of-fold ROC/PR and calibration curves, expected calibration error, test-time missingness 0-40%."),
    ("C9", "Workflow Table 6: computational cost.",
     "Training time, inference time per 1,000 records and serialized model size."),
    ("C10", "Proposal: expandable decision-support system.",
     "Open demonstrator with handcrafted rules, a corrected scoring defect, tests, and screenshots; explicitly not a validated model."),
    ("C11", "Workflow: do not claim clinical significance; do not start from assumed accuracy tables.",
     "All numbers come from executed runs; negative results (no network gain, no significant model differences) are reported."),
    ("C12", "Proposal: continual learning (Paper 2), adaptive/personalised models (Paper 3), LIME, counterfactuals.",
     "Not performed; listed as limitations and future work with the required study design."),
]

REFS = {
    "rudin": "Rudin C. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. Nat Mach Intell. 2019;1:206–215.",
    "baltrusaitis": "Baltrušaitis T, Ahuja C, Morency LP. Multimodal machine learning: a survey and taxonomy. IEEE Trans Pattern Anal Mach Intell. 2019;41(2):423–443.",
    "proposal": "E-XMAI research proposal: development of an expandable explainable AI framework for multimodal prediction of diabetes, cardiovascular, renal and liver diseases. Unpublished project document; authors and date not stated in the supplied file.",
    "lightgbm": "Ke G, Meng Q, Finley T, et al. LightGBM: a highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems 30. 2017:3146–3154.",
    "catboost": "Prokhorenkova L, Gusev G, Vorobev A, Dorogush AV, Gulin A. CatBoost: unbiased boosting with categorical features. In: Advances in Neural Information Processing Systems 31. 2018:6638–6648.",
    "rf": "Breiman L. Random forests. Mach Learn. 2001;45(1):5–32.",
    "shap": "Lundberg SM, Lee SI. A unified approach to interpreting model predictions. In: Advances in Neural Information Processing Systems 30. 2017:4765–4774.",
    "treeshap": "Lundberg SM, Erion G, Chen H, et al. From local explanations to global understanding with explainable AI for trees. Nat Mach Intell. 2020;2:56–67.",
    "grinsztajn": "Grinsztajn L, Oyallon E, Varoquaux G. Why do tree-based models still outperform deep learning on typical tabular data? In: Advances in Neural Information Processing Systems 35 (Datasets and Benchmarks). 2022.",
    "tabnet": "Arik SÖ, Pfister T. TabNet: attentive interpretable tabular learning. Proc AAAI Conf Artif Intell. 2021;35(8):6679–6687.",
    "lime": "Ribeiro MT, Singh S, Guestrin C. “Why should I trust you?”: explaining the predictions of any classifier. In: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. 2016:1135–1144.",
    "wachter": "Wachter S, Mittelstadt B, Russell C. Counterfactual explanations without opening the black box: automated decisions and the GDPR. Harv J Law Technol. 2018;31(2):841–887.",
    "alvarez": "Alvarez-Melis D, Jaakkola TS. On the robustness of interpretability methods. arXiv:1806.08049. 2018.",
    "kirkpatrick": "Kirkpatrick J, Pascanu R, Rabinowitz N, et al. Overcoming catastrophic forgetting in neural networks. Proc Natl Acad Sci USA. 2017;114(13):3521–3526.",
    "kapoor": "Kapoor S, Narayanan A. Leakage and the reproducibility crisis in machine-learning-based science. Patterns. 2023;4(9):100804.",
    "nadeau": "Nadeau C, Bengio Y. Inference for the generalization error. Mach Learn. 2003;52(3):239–281.",
    "tripod": "Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378.",
    "openml": "Vanschoren J, van Rijn JN, Bischl B, Torgo L. OpenML: networked science in machine learning. ACM SIGKDD Explor Newsl. 2013;15(2):49–60.",
    "smith": "Smith JW, Everhart JE, Dickson WC, Knowler WC, Johannes RS. Using the ADAP learning algorithm to forecast the onset of diabetes mellitus. Proc Annu Symp Comput Appl Med Care. 1988:261–265.",
    "detrano": "Detrano R, Janosi A, Steinbrunn W, et al. International application of a new probability algorithm for the diagnosis of coronary artery disease. Am J Cardiol. 1989;64(5):304–310.",
    "soundar": "Soundarapandian P, Rubini L, Eswaran P. Chronic_Kidney_Disease data set. UCI Machine Learning Repository. 2015.",
    "ramana": "Ramana BV, Babu MSP, Venkateswarlu NB. A critical study of selected classification algorithms for liver disease diagnosis. Int J Database Manag Syst. 2011;3(2):101–114.",
    "clauset": "Clauset A, Newman MEJ, Moore C. Finding community structure in very large networks. Phys Rev E. 2004;70:066111.",
    "networkx": "Hagberg AA, Schult DA, Swart PJ. Exploring network structure, dynamics, and function using NetworkX. In: Proceedings of the 7th Python in Science Conference. 2008:11–15.",
    "holm": "Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat. 1979;6(2):65–70.",
    "niculescu": "Niculescu-Mizil A, Caruana R. Predicting good probabilities with supervised learning. In: Proceedings of the 22nd International Conference on Machine Learning. 2005:625–632.",
    "saito": "Saito T, Rehmsmeier M. The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLoS ONE. 2015;10(3):e0118432.",
}


def ms(d, m, k):
    e = S[d][m][k]
    return f"{e['mean']:.3f} ± {e['sd']:.3f}"


def best(d, k="auroc", low=False):
    return (min if low else max)(MOD, key=lambda m: S[d][m][k]["mean"])


def rob(d, m, lv):
    return E["robustness"][d][m][lv]["mean"]


min_holm = min(T, key=lambda t: t["p_holm"])
min_raw = min(T, key=lambda t: t["p_corrected"])
jac = R["shap_stability"]
J = {d: jac[d]["top5_jaccard_mean"] for d in DIS}
AT = E["ablation_tests"]
abl_max = max(AT, key=lambda t: abs(t["mean_diff"]))
abl_minp = min(AT, key=lambda t: t["p_holm"])
total_n = sum(D[d]["n"] for d in DIS)
ece_best = {d: min(MOD, key=lambda m: E["calibration"][d][m]["ece_5bin"]) for d in DIS}
drop40 = {(d, m): rob(d, m, "0.0") - rob(d, m, "0.4") for d in DIS for m in MOD}
least_drop = {d: min(MOD, key=lambda m: drop40[(d, m)]) for d in DIS}
rf_brier_best = [d for d in DIS if best(d, "brier", low=True) == "Random Forest"]


def auroc_rng(d):
    v = [S[d][m]["auroc"]["mean"] for m in MOD]
    return min(v), max(v)


ABSTRACT = [
    ("Background", "Diabetes, cardiovascular, kidney and liver diseases are usually modelled separately, often with "
     "opaque classifiers. A proposed expandable and explainable framework (E-XMAI) needs, as its first step, a "
     "transparent and leakage-controlled multi-disease baseline."),
    ("Objective", "To benchmark three tree-based learners with SHAP explanations on four public disease datasets, "
     "to test whether a training-fold feature-association network adds predictive information, and to document an "
     "open demonstrator of multimodal input fusion."),
    ("Methods", f"LightGBM, CatBoost and Random Forest were evaluated on four public tabular datasets (n = {total_n:,} "
     "records) with 5 × 5 repeated stratified cross-validation, in-fold preprocessing, fixed hyperparameters and a "
     "fixed 0.5 threshold. We report AUROC, AUPRC, F1, sensitivity, specificity, Brier score and expected calibration "
     "error with 95% confidence intervals, corrected resampled t-tests with Holm adjustment, test-time missing-data "
     "robustness, feature-association networks, a network-feature ablation and SHAP summaries, local explanations and "
     "stability."),
    ("Results", f"Mean AUROC was {auroc_rng('Liver')[0]:.2f}–{auroc_rng('Liver')[1]:.2f} (liver), "
     f"{auroc_rng('Diabetes')[0]:.2f}–{auroc_rng('Diabetes')[1]:.2f} (diabetes), "
     f"{auroc_rng('Cardiovascular')[0]:.2f}–{auroc_rng('Cardiovascular')[1]:.2f} (cardiovascular) and about 1.00 "
     f"(kidney). No pairwise model difference was significant after Holm adjustment (smallest adjusted p = "
     f"{min_holm['p_holm']:.2f}). Adding network-derived community scores changed AUROC by at most "
     f"{abs(abl_max['mean_diff']):.3f} and no change was significant (smallest adjusted p = "
     f"{abl_minp['p_holm']:.2f}). Leading SHAP features matched established clinical markers, with top-5 "
     f"agreement across folds of {min(J.values()):.2f}–{max(J.values()):.2f} (Jaccard). AUROC fell by "
     f"{min(drop40.values()):.2f}–{max(drop40.values()):.2f} when 40% of test cells were missing."),
    ("Conclusions", "Under one protocol the three learners performed similarly, and the network component, although "
     "interpretable, provided no reliable predictive gain. The datasets describe different patients, so the work "
     "does not establish multimodal prediction; the demonstrator's rules are unvalidated; and external validation, "
     "LIME, counterfactuals and continual learning remain future work."),
]
KEYWORDS = ("explainable artificial intelligence; SHAP; gradient boosting; feature-association network; "
            "multi-disease prediction; calibration; reproducibility")

DECLARATIONS = [
    ("Ethics approval and consent", "Only publicly available, de-identified datasets were used and no new data were "
     "collected from human participants. The authors should confirm whether their institution requires a formal "
     "exemption statement."),
    ("Data and code availability", "Datasets: OpenML IDs 37, 53, 42972 and 1480 (UCI Machine Learning Repository "
     "origin). Code, fixed seed, per-fold metrics, figures and screenshots are in the project repository "
     "(scripts/run_experiments.py, scripts/run_extended_analysis.py; output/)."),
    ("Funding", "[To be completed by the authors.]"),
    ("Competing interests", "[To be completed by the authors.]"),
    ("Author contributions", "[To be completed by the authors, e.g. using the CRediT taxonomy.]"),
    ("Use of generative AI", "A generative-AI assistant (Claude, Anthropic) was used to help write the experiment and "
     "application code and to draft and edit the manuscript. The authors are responsible for verifying all content, "
     "results and citations and for complying with the target journal's AI-use policy."),
]


def blocks() -> list:
    B: list = []
    h1 = lambda t: B.append(("h1", t))
    h2 = lambda t: B.append(("h2", t))
    p = lambda t: B.append(("p", t))
    tag = lambda t: B.append(("tag", t))
    fig = lambda path, cap, w=6.0: B.append(("fig", path, cap, w))

    h1("1. Introduction")
    tag(None)
    p("Diabetes mellitus, cardiovascular disease, chronic kidney disease and chronic liver disease account for a large "
      "share of long-term morbidity, and they frequently co-occur and share risk factors such as age, adiposity, "
      "blood pressure and glycaemic control. Machine-learning studies have nonetheless tended to treat each condition "
      "in isolation, with a separate dataset, feature set and evaluation protocol per paper. That fragmentation makes "
      "results hard to compare and complicates any attempt to build one system that can accommodate further diseases. "
      "Many of the classifiers involved are also opaque, which limits trust and clinical adoption [@rudin].")
    tag("C1")
    p("Throughout, \"multimodal\" is used in the usual sense of combining heterogeneous data sources describing the "
      "same patients [@baltrusaitis]. A research programme referred to here as E-XMAI (Expandable and Explainable "
      "Multimodal Artificial Intelligence) proposes three stages: a common multi-disease framework with model "
      "comparison and post-hoc explanation; an expandable framework based on continual learning; and an adaptive, "
      "personalised framework with counterfactual explanations [@proposal]. The first stage has a prerequisite that is "
      "easily skipped: a transparent, leakage-controlled baseline against which later claims about expansion, "
      "forgetting or personalisation can be measured. The programme's own workflow also cautions that separate "
      "datasets of unrelated patients cannot simply be treated as one multimodal cohort; this article heeds that "
      "caution and restricts its multimodal claims accordingly.")
    tag(None)
    p("We make four contributions. First, we benchmark LightGBM [@lightgbm], CatBoost [@catboost] and Random Forest "
      "[@rf] on four public datasets, one per disease, under one protocol with training-fold-only preprocessing, "
      "repeated cross-validation, confidence intervals and multiplicity-adjusted tests. Second, we construct "
      "disease-specific feature-association networks and test, by ablation, whether network-derived features add "
      "predictive information. Third, we summarise SHAP explanations [@shap; @treeshap] globally, locally and across "
      "diseases, and quantify their stability, calibration and robustness to missing data. Fourth, we document an open "
      "demonstrator of structured-value and note-text fusion, with its non-claims stated precisely.")

    h1("2. Background")
    p("**Tabular learners.** Gradient-boosted trees and random forests remain strong defaults for small and medium "
      "tabular data; benchmarks report that tree-based models often match or exceed deep tabular architectures on "
      "such data [@grinsztajn]. Attention-based tabular networks such as TabNet [@tabnet] are part of the proposed "
      "programme but were not evaluated here.")
    p("**Explanation.** SHAP assigns each feature an additive contribution to an individual prediction using Shapley "
      "values, with a fast exact algorithm for tree ensembles [@shap; @treeshap]. LIME fits a local surrogate [@lime], "
      "and counterfactual explanations describe minimal input changes that alter an outcome [@wachter]. Explanations "
      "describe model behaviour, not causal mechanisms, and their stability should be checked rather than assumed "
      "[@alvarez].")
    p("**Networks and expandability.** Feature-association networks summarise how variables co-vary and allow "
      "community structure [@clauset] to be inspected; they describe association, not causation. Learning new tasks "
      "without erasing earlier ones is the subject of continual learning, where catastrophic forgetting is the central "
      "difficulty [@kirkpatrick]; it requires a task sequence and retention measurements and is not attempted here.")
    p("**Evaluation hygiene.** Information leakage between training and test data is a frequent cause of inflated "
      "results [@kapoor]. Resampled cross-validation estimates are also correlated, so naive paired tests over folds are "
      "anti-conservative; a variance correction is available [@nadeau].")

    h1("3. Materials and methods")
    h2("3.1 Study design")
    p("This is a retrospective secondary analysis of public, de-identified datasets, reported in line with the "
      "applicable items of TRIPOD+AI [@tripod]. Each disease is a separate binary classification task; no pooled "
      "model is trained and no cross-dataset claim is made.")
    h2("3.2 Datasets")
    p("One public dataset per disease was obtained through OpenML [@openml] on 11 October 2026 (Table 1): the Pima "
      "Indians diabetes cohort [@smith], the Statlog heart-disease data derived from the work of Detrano et al. "
      "[@detrano], the chronic-kidney-disease records of Soundarapandian et al. [@soundar] and the Indian Liver Patient "
      "Dataset (ILPD) [@ramana]. Two kidney records carried a mistyped label and were mapped to the positive class; no "
      "records were removed. Zero values for some physiological variables in the diabetes file were left as provided, "
      "because recoding them would be an additional analytic decision outside the stated protocol.")
    B.append(("table", "Table 1. Characteristics of the four public datasets.",
              ["Disease area", "Source", "Records", "Features", "Positive (prevalence)", "Categorical", "Missing cells"],
              [[d, D[d]["source"], D[d]["n"], D[d]["features"], f"{D[d]['positives']} ({D[d]['prevalence']:.1%})",
                D[d]["categorical_features"], D[d]["missing_cells"]] for d in DIS]))
    tag("C3")
    h2("3.3 Preprocessing and evaluation protocol")
    p("Median imputation (numeric) and most-frequent imputation with one-hot encoding (categorical) were fitted on "
      "each training fold only. No feature selection, resampling or scaling was applied to the baseline models. "
      "Performance was estimated by stratified 5-fold cross-validation repeated five times (25 test folds per dataset; "
      "seed 20261011). Accuracy, sensitivity, specificity and F1 used a probability threshold of 0.5 fixed in advance; "
      "AUROC, AUPRC, Brier score and a five-bin expected calibration error (ECE) were also computed. Means, standard "
      "deviations over folds and t-based 95% confidence intervals are reported; because folds share training data, "
      "the intervals understate uncertainty about new populations.")
    tag("C2")
    h2("3.4 Models")
    p("LightGBM (200 trees, learning rate 0.05, 15 leaves, minimum 10 samples per leaf), CatBoost (300 iterations, "
      "learning rate 0.05, depth 4) and Random Forest (300 trees) were trained with fixed hyperparameters that were "
      "not selected using held-out data. The reported performance is therefore a floor for each learner, not its "
      "tuned optimum.")
    tag("C4")
    h2("3.5 Statistical comparison")
    p("Models were compared pairwise on per-fold AUROC with the corrected resampled t-test [@nadeau]; the resulting "
      "p-values (three pairs × four datasets) were adjusted with the Holm procedure [@holm].")
    tag("C5")
    h2("3.6 Feature-association networks")
    p("For each disease, nodes are the preprocessed features (one-hot columns are separate nodes) and an undirected "
      "edge joins two features whose absolute Spearman correlation is at least 0.30, a threshold fixed in advance. "
      "Weighted degree (strength) and betweenness centrality (edge length 1/|ρ|) were computed with NetworkX "
      "[@networkx], and communities were found by greedy modularity maximisation [@clauset]. The networks reported in "
      "Section 4.3 use all records and are descriptive; they never feed an evaluation. Networks used inside "
      "evaluation were rebuilt on each training fold (Section 3.7).")
    tag("C6")
    h2("3.7 Network-feature ablation")
    p("Within each training fold, features were standardised, the network was built, and each community of at least "
      "two features was converted to one score: the mean standardised value of its members after aligning each "
      "member's sign with its training-fold correlation with the outcome. Three variants were compared with "
      "LightGBM and Random Forest using the same 5 × 5 folds: the baseline (original features), original features "
      "plus community scores, and community scores only. SHAP is a post-hoc explanation and is not a predictive "
      "component in any variant. Differences in AUROC were tested with the corrected t-test and Holm adjustment over "
      "the eight (disease × learner) comparisons.")
    tag("C7")
    h2("3.8 Explanations")
    p("TreeExplainer SHAP values [@treeshap] were computed for LightGBM on the held-out records of every fold, and mean "
      "absolute SHAP values were averaged over the 25 folds. Stability was the mean pairwise Jaccard index between "
      "the top-five feature sets of different folds. For descriptive summary plots, a LightGBM model was fitted to "
      "all records of each dataset. Local explanations were computed for one true-positive and one true-negative "
      "record of a held-out split that the model had not seen.")
    tag("C8")
    h2("3.9 Calibration, discrimination curves and robustness")
    p("ROC, precision–recall [@saito] and reliability curves [@niculescu] were derived from pooled out-of-fold "
      "predictions of one 5-fold pass. Robustness to missing data was assessed by deleting 10–40% of test-set cells at "
      "random (missing completely at random) while models and imputers were fitted on complete training folds "
      "(5-fold × 2 repeats).")
    tag("C9")
    h2("3.10 Computational cost")
    p("Training time and inference time per 1,000 records were measured on a laptop CPU, and model size was taken "
      "as the serialized pipeline size.")
    tag("C10")
    h2("3.11 Demonstrator software")
    p("A local web application (React 19, Tailwind CSS 4, Flask 3) accepts bounded numeric measures (age, body-mass "
      "index, glucose, systolic blood pressure, cholesterol, creatinine, eGFR, ALT, AST, smoking and alcohol flags) "
      "and an optional free-text note. For each disease d it forms a structured index "
      "C_d = clip(28 + Σ_i clip((x_i − r_i)/s_i · 100 · w_i, −12, 24), 0, 100), where r_i is a reference value, s_i a "
      "span and w_i a signed weight; a note index T_d = min(100, 18 + Σ cue weights) from keyword matches; and a "
      "fused index S_d = round(a·C_d + (1 − a)·T_d) with a user-set modality weight a normalised to [0, 1]. Scores of "
      "at least 65 are labelled Elevated, 38–64 Review and below 38 Lower. Reference values, spans, weights and cues "
      "are hand-specified and were not fitted to, or validated on, any dataset; the displayed per-feature terms are rule "
      "contributions, not SHAP values. The service validates numeric ranges and weights, restricts uploads to CSV "
      "files up to 5 MB with required headers, runs on the loopback interface, and stores uploads locally without "
      "using them for scoring. Eight automated tests cover the API contract, validation and a regression check that "
      "clearly abnormal inputs leave the lowest band.")
    tag(None)
    h2("3.12 Reproducibility")
    p("All code, the fixed seed, dependency lists, per-fold metrics, figures and screenshots are provided in the "
      "project repository. The manuscript is generated from the result files so that reported numbers match them.")

    h1("4. Results")
    tag("C3")
    h2("4.1 Baseline performance")
    ranking = "; ".join(f"{d.lower()}: {best(d)}" for d in DIS)
    liv_sens = [S["Liver"][m]["sensitivity"]["mean"] for m in MOD]
    liv_spec = [S["Liver"][m]["specificity"]["mean"] for m in MOD]
    p(f"Table 2 and Figure 1 summarise cross-validated performance. The learner with the highest mean AUROC was "
      f"({ranking}), but margins were small relative to fold-to-fold variation. Kidney-disease discrimination was "
      f"near the ceiling for all learners (AUROC {auroc_rng('Renal')[0]:.3f}–{auroc_rng('Renal')[1]:.3f}). Liver "
      f"disease was the most difficult task (AUROC {auroc_rng('Liver')[0]:.2f}–{auroc_rng('Liver')[1]:.2f}); with a "
      f"prevalence of {D['Liver']['prevalence']:.1%} and a 0.5 threshold, all liver models favoured sensitivity "
      f"({min(liv_sens):.2f}–{max(liv_sens):.2f}) at the cost of specificity ({min(liv_spec):.2f}–{max(liv_spec):.2f}), "
      f"and the high AUPRC largely reflects the base rate, which a no-skill classifier already attains.")
    rows = [[d, m] + [ms(d, m, k) for k in ["auroc", "auprc", "f1", "sensitivity", "specificity", "brier"]]
            for d in DIS for m in MOD]
    B.append(("table", "Table 2. Baseline performance (mean ± SD over 25 test folds; threshold 0.5).",
              ["Disease", "Model", "AUROC", "AUPRC", "F1", "Sensitivity", "Specificity", "Brier"], rows))
    fig(FIGS / "fig_auroc.png", "Figure 1. AUROC of the three learners for each disease (mean ± SD over 25 folds). "
        "Kidney-disease performance is at ceiling.", 5.8)
    tag("C4")
    h2("4.2 Model comparison")
    cis = "; ".join(f"{d} {best(d)} {S[d][best(d)]['auroc']['ci95_low']:.3f}–{S[d][best(d)]['auroc']['ci95_high']:.3f}"
                    for d in DIS)
    p(f"The 95% confidence intervals for the best learner's AUROC were: {cis}. Table 3 lists the pairwise "
      f"comparisons. None remained significant after adjustment: the smallest unadjusted p-value "
      f"({min_raw['p_corrected']:.3f}, {min_raw['comparison']} on {min_raw['disease'].lower()}) became "
      f"{min_raw['p_holm']:.2f} after Holm correction. The data do not support a claim that any learner is superior; "
      f"they are equally consistent with small true differences that these sample sizes cannot resolve.")
    B.append(("table", "Table 3. Pairwise AUROC comparisons (corrected resampled t-test; Holm-adjusted over 12 tests).",
              ["Disease", "Comparison", "Mean difference", "Unadjusted p", "Holm-adjusted p"],
              [[t["disease"], t["comparison"],
                f"{t['mean_diff']:+.3f}" if abs(t["mean_diff"]) >= 0.0005 else "0.000",
                f"{t['p_corrected']:.3f}", f"{t['p_holm']:.3f}"] for t in T]))
    tag("C5")
    h2("4.3 Feature-association networks")
    NW = E["networks"]
    dens = max(DIS, key=lambda d: NW[d]["density"])
    p(f"Table 4 and Figures 2–3 describe the networks. {dens} produced the densest network "
      f"(density {NW[dens]['density']:.2f}; {NW[dens]['nodes']} nodes after one-hot expansion), which is expected "
      f"because many kidney variables are mutually correlated markers of renal function. The most central features "
      f"were: " + "; ".join(
          f"{d.lower()}: {', '.join(x.replace('_', ' ') for x in NW[d]['top_central_features'])}" for d in DIS) +
      ". Edges represent statistical association only and are not evidence of causal or biological relationships.")
    B.append(("table", "Table 4. Network characteristics (descriptive, all records; |Spearman ρ| ≥ 0.30).",
              ["Disease", "Nodes", "Edges", "Density", "Communities (≥2)", "Modularity", "Top central features"],
              [[d, NW[d]["nodes"], NW[d]["edges"], f"{NW[d]['density']:.3f}", NW[d]["communities"],
                f"{NW[d]['modularity']:.2f}", ", ".join(x.replace("_", " ") for x in NW[d]["top_central_features"])]
               for d in DIS], [1.1, 0.6, 0.6, 0.7, 0.9, 0.8, 2.6]))
    fig(FIGS / "fig_networks.png", "Figure 2. Disease-specific feature-association networks. Node size is weighted "
        "degree, node colour is the community, edge width is |Spearman ρ|; the three most central features are labelled.", 6.3)
    fig(FIGS / "fig_centrality.png", "Figure 3. Five most central features per disease (weighted degree).", 6.0)
    tag("C6")
    h2("4.4 Network-feature ablation")
    A = E["ablation"]
    rows = []
    for d in DIS:
        for l in ["LightGBM", "Random Forest"]:
            for v, (orig, net) in [("Baseline (original features)", ("Yes", "No")),
                                   ("Network scores only", ("No", "Yes")),
                                   ("Original + network scores", ("Yes", "Yes"))]:
                a = A[d][l][v]
                rows.append([d, l, v, orig, net, "Post-hoc", f"{a['auroc_mean']:.3f} ± {a['auroc_sd']:.3f}",
                             f"{a['f1_mean']:.3f} ± {a['f1_sd']:.3f}"])
    p(f"Table 5 reports the ablation. Adding community scores to the original features changed mean AUROC by "
      f"{min(t['mean_diff'] for t in AT):+.3f} to {max(t['mean_diff'] for t in AT):+.3f}; the largest change "
      f"({abl_max['mean_diff']:+.3f}, {abl_max['learner']} on {abl_max['disease'].lower()}) had an adjusted p-value of "
      f"{abl_max['p_holm']:.2f}. Community scores alone were weaker than the original features for diabetes, where the "
      f"network is sparse, and close to them (or, for liver disease, slightly above) for the other three diseases. The network therefore offered an "
      f"interpretable summary of feature structure but no reliable predictive benefit in these data.")
    B.append(("table", "Table 5. Ablation of network-derived features (mean ± SD over 25 folds).",
              ["Disease", "Learner", "Configuration", "Original", "Network", "SHAP", "AUROC", "F1"], rows,
              [1.0, 1.0, 2.0, 0.6, 0.6, 0.7, 1.2, 1.2]))
    tag("C7")
    h2("4.5 Explainability")
    rows = []
    for d in DIS:
        top = SHAP[SHAP.disease == d].head(5)
        rows.append([d, "; ".join(f"{r.feature.replace('_', ' ')} ({r.mean_abs_shap:.2f})" for r in top.itertuples()),
                     f"{jac[d]['top5_jaccard_mean']:.2f} ± {jac[d]['top5_jaccard_sd']:.2f}"])
    jtxt = ", ".join(f"{d.lower()} {J[d]:.2f}" for d in DIS)
    p(f"Table 6 and Figures 4–6 present the explanations. Highest-ranked features were clinically plausible: plasma "
      f"glucose and body-mass index for diabetes; number of major vessels, chest-pain type and thalassaemia test result "
      f"for cardiovascular disease; haemoglobin, specific gravity, serum creatinine and albumin for kidney disease; and "
      f"bilirubin and liver enzymes for liver disease. Top-five agreement across folds was moderate to good "
      f"({jtxt}) and lowest for cardiovascular disease, the smallest dataset. The local explanations (Figure 5) show "
      f"that individual predictions are driven by different features: the true-positive diabetes case is dominated by "
      f"pedigree function and glucose, whereas the true-positive kidney case is dominated by serum creatinine and "
      f"appetite. Plausibility is not validation: SHAP describes what the fitted model uses, not what causes disease, "
      f"and the cross-disease comparison (Figure 6) mixes variables that are not shared across datasets.")
    B.append(("table", "Table 6. Highest-ranked features by mean absolute SHAP value (LightGBM, held-out folds; log-odds "
              "units) and top-5 stability (pairwise Jaccard, mean ± SD).",
              ["Disease", "Top-5 features (mean |SHAP|)", "Top-5 stability"], rows, [1.0, 4.5, 1.3]))
    fig(FIGS / "fig_shap_summary.png", "Figure 4. SHAP summary plots (descriptive; LightGBM fitted to all records). "
        "Each point is a record; horizontal position is its SHAP value and colour is the min–max scaled feature value "
        "(blue low, red high).", 6.4)
    fig(FIGS / "fig_shap_local.png", "Figure 5. Local SHAP explanations for one true-positive (top) and one "
        "true-negative (bottom) held-out record per disease; red bars raise and blue bars lower the predicted risk.", 6.4)
    fig(FIGS / "fig_shap_cross_disease.png", "Figure 6. Share of total mean |SHAP| for the six highest-ranked "
        "features of each disease (blank = not in that disease's top six).", 4.4)
    tag("C8")
    h2("4.6 Calibration, discrimination curves and robustness")
    p(f"Figures 7–9 and Table 7 give calibration and robustness. Expected calibration error was lowest for "
      f"{', '.join(f'{ece_best[d]} ({d.lower()})' for d in DIS)}. Random Forest also had the lowest Brier score in "
      f"{', '.join(x.lower() for x in rf_brier_best)}. LightGBM was the least well calibrated learner outside kidney "
      f"disease, consistent with unconstrained boosting at fixed hyperparameters on small samples; no recalibration "
      f"was attempted. Deleting 40% of test cells reduced AUROC by {min(drop40.values()):.2f}–{max(drop40.values()):.2f}; "
      f"the least-affected learner was {', '.join(f'{least_drop[d]} ({d.lower()})' for d in DIS)}. "
      f"Kidney-disease discrimination was the most robust, presumably because many of its variables are redundant "
      f"markers of the same condition.")
    rows = []
    for d in DIS:
        for m in MOD:
            c, cost = E["calibration"][d][m], E["cost"][d][m]
            rows.append([d, m, f"{rob(d, m, '0.0'):.3f}", f"{rob(d, m, '0.2'):.3f}", f"{rob(d, m, '0.4'):.3f}",
                         f"{c['ece_5bin']:.3f}", f"{S[d][m]['brier']['mean']:.3f}",
                         f"{cost['fit_seconds_full']:.2f}", f"{cost['predict_seconds_per_1000']:.3f}",
                         f"{cost['model_kb']:.0f}"])
    B.append(("table", "Table 7. Robustness (AUROC at 0%, 20% and 40% of test cells missing), calibration and "
              "computational cost.",
              ["Disease", "Model", "AUROC 0%", "AUROC 20%", "AUROC 40%", "ECE", "Brier", "Fit (s)",
               "Predict (s/1000)", "Size (KB)"], rows, [1.5, 1.5, 0.8, 0.8, 0.8, 0.7, 0.7, 0.7, 0.9, 0.8]))
    fig(FIGS / "fig_roc_pr.png", "Figure 7. ROC (top) and precision–recall (bottom) curves from pooled out-of-fold "
        "predictions. Dashed lines are no-skill references.", 6.4)
    fig(FIGS / "fig_calibration.png", "Figure 8. Reliability curves (five quantile bins) from pooled out-of-fold "
        "predictions.", 6.4)
    fig(FIGS / "fig_robustness.png", "Figure 9. AUROC under random deletion of test-set cells (mean ± SD over 10 folds).", 6.4)
    tag("C9")
    h2("4.7 Computational cost")
    mx = max(E["cost"][d][m]["fit_seconds_full"] for d in DIS for m in MOD)
    szs = {m: max(E["cost"][d][m]["model_kb"] for d in DIS) for m in MOD}
    p(f"Full-data training took at most {mx:.2f} s per model and inference well under 0.1 s per 1,000 records on a "
      f"laptop CPU (Table 7). Serialized size reached {szs['CatBoost']:.0f} KB for CatBoost, "
      f"{szs['LightGBM']:.0f} KB for LightGBM and {szs['Random Forest']:.0f} KB for Random Forest, so the forest is "
      f"the heaviest model to deploy at similar accuracy.")
    tag("C10")
    h2("4.8 Demonstrator behaviour")
    p("Figure 10 and Appendix A show the demonstrator. For a default profile all four indices fall in the Lower "
      "band; for the example profile of Figure 10 three indices reach the Review band and note cues add visible terms "
      "only to the affected disease. These checks confirm intended software behaviour and are not evidence of "
      "predictive validity.")
    fig(SHOTS / "02-overview-example-patient.png", "Figure 10. Demonstrator overview after loading the example "
        "patient: four illustrative indices, rule contributions for the selected disease and modality weights, under a "
        "research-use banner. Further screenshots are in Appendix A.", 5.2)

    tag("C11")
    h1("5. Discussion")
    p("Across four public datasets, three tree-based learners reached similar discrimination under a common, "
      "leakage-controlled protocol, and no learner was reliably better after multiplicity adjustment. A feature-"
      "association network built on training folds produced coherent, interpretable structure but did not improve "
      "prediction. For a programme whose later stages concern expansion and adaptation, both are useful baselines: "
      "any later gain from a continual or adaptive method should be judged against differences of this size, and a "
      "network component should be justified by interpretability or data efficiency rather than accuracy.")
    p("Leading SHAP features agreed with established clinical markers and their ranks were moderately stable, but "
      "stability was lower in the smallest dataset, which suggests that explanation reliability depends on data volume "
      "and should be reported with intervals. Near-perfect kidney-disease discrimination should be read cautiously: "
      "the leading features (haemoglobin, specific gravity, albumin, serum creatinine) are themselves manifestations of "
      "established kidney dysfunction and the task separates recorded disease from non-disease rather than anticipating "
      "onset. Robustness to missing data and calibration differed more between learners than discrimination did, "
      "which argues for reporting both alongside AUROC.")
    B.append(("table", "Table 8. Coverage of the proposed E-XMAI programme by this work.",
              ["Proposed element", "Status in this article"],
              [["Four disease areas", "Evaluated as four separate single-disease tasks on public data"],
               ["LightGBM, CatBoost, Random Forest comparison", "Done (fixed hyperparameters)"],
               ["TabNet", "Not evaluated"],
               ["Feature-association network and ablation", "Done; no reliable predictive gain"],
               ["SHAP explanations, local explanations, stability", "Done (LightGBM; top-5 Jaccard across folds)"],
               ["LIME and counterfactual explanations", "Not implemented"],
               ["Multimodal integration", "Illustrated by a demonstrator with handcrafted rules; no linked multimodal cohort"],
               ["Calibration, ROC/PR, missing-data robustness, cost", "Done (ECE, Brier, curves, test-time missingness)"],
               ["External validation, subgroup and fairness analysis", "Not performed"],
               ["Continual / incremental learning, forgetting", "Not performed (planned second stage)"],
               ["Adaptive and personalised prediction", "Not performed (planned third stage)"]]))
    tag("C12")
    h2("5.1 Limitations")
    for item in [
        "The datasets are small (270–768 records), single-source and of differing provenance; no external or temporal validation was performed, so generalisation to other populations is unknown.",
        "Separate datasets for separate diseases are not a multimodal cohort. Multimodal claims require linked modalities (for example laboratory data, imaging or notes for the same patients).",
        "Hyperparameters were fixed rather than tuned and a single threshold was used; the ranking among learners could change with tuning, and the missing-data experiment assumes data missing completely at random.",
        "Confidence intervals and tests rely on resampled folds and understate uncertainty about new populations even with the variance correction.",
        "Known data-quality issues, such as physiologically implausible zeros in the diabetes file, were not recoded, and label provenance in some sources is uncertain.",
        "SHAP values are model-specific and associational; LIME, counterfactuals and clinician evaluation of explanations were not studied. Networks describe association, not causation, and the network threshold was not tuned.",
        "The demonstrator's rules are handcrafted, unvalidated and uncalibrated; its scores are not probabilities and must not inform care. Note handling is keyword matching, not language modelling.",
        "Continual learning, catastrophic forgetting and adaptive or personalised models, central to the proposed programme, were not studied.",
    ]:
        B.append(("bullet", item))
    h2("5.2 Future work")
    p("Stage two would add disease tasks sequentially with a continual-learning method and report both new-task "
      "performance and retention of earlier tasks. Stage three would introduce distribution shift across populations or "
      "time and evaluate adaptation, explanation stability, counterfactual explanations and cost. Both would benefit "
      "from linked multimodal data under appropriate governance, recalibration, subgroup analysis and external "
      "validation.")
    tag(None)
    h1("6. Conclusion")
    p("A transparent baseline for four chronic-disease prediction tasks shows that LightGBM, CatBoost and Random Forest "
      "perform comparably under a leakage-controlled protocol, that a training-fold feature-association network adds "
      "interpretable structure but no reliable accuracy, and that SHAP explanations are clinically plausible and "
      "moderately stable. The accompanying demonstrator makes multimodal fusion inspectable but is explicitly not a "
      "validated model. The work supplies a reproducible starting point, not evidence of clinical utility, for the "
      "proposed expandable and explainable framework.")

    tag("C10")
    B.append(("pagebreak",))
    h1("Appendix A. Application screenshots")
    p("All captures were taken from the running application (Chrome, 1280 px wide unless stated) with synthetic "
      "values only.")
    for i, (f, cap, w) in enumerate([
        ("01-overview-default.png", "Overview page with default values; all four indices in the Lower band.", 5.4),
        ("02-overview-example-patient.png", "Overview after loading the example patient; note cues and clinical terms are itemised.", 5.4),
        ("03-assessment-filled.png", "Assessment form completed with a clinical note and smoking flag.", 5.4),
        ("04-assessment-after-calculate.png", "Result after submitting the assessment; scores move into the Review band.", 5.4),
        ("05-overview-renal-selected.png", "Overview with the renal module selected.", 5.4),
        ("06-data-methodology.png", "Data and methodology page: synthetic fixture summary and stated limitations.", 5.4),
        ("07-data-upload-success.png", "CSV upload accepted and stored locally; not used for scoring.", 5.4),
        ("08-mobile-overview.png", "Responsive layout at 390 px width (device scale 2): left, top of the overview with score cards; right, the explanation panel and patient snapshot.", 6.2)], 1):
        fig(SHOTS / f, f"Figure A{i}. {cap}", w)
    return B


def number_citations(B):
    order: list[str] = []
    pat = r"\[((?:@[a-z]+[,; ]*)+)\]"
    for blk in B:
        if blk[0] in ("h1", "h2", "p", "bullet"):
            for grp in re.findall(pat, blk[1]):
                for k in re.findall(r"@([a-z]+)", grp):
                    if k not in order:
                        order.append(k)
    num = {k: i + 1 for i, k in enumerate(order)}
    sub = lambda t: re.sub(pat, lambda m: "[" + ",".join(str(num[k]) for k in re.findall(r"@([a-z]+)", m.group(1))) + "]", t)
    out = [(b[0], sub(b[1])) + tuple(b[2:]) if b[0] in ("h1", "h2", "p", "bullet") else b for b in B]
    return out, [REFS[k] for k in order]


def plain_text(B, meta) -> str:
    parts = [meta["title"]] + [f"{h}: {t}" for h, t in meta["abstract"]]
    for blk in B:
        if blk[0] in ("h1", "h2", "p", "bullet", "table"):
            parts.append(blk[1])
        elif blk[0] == "fig":
            parts.append(blk[2])
    parts += [f"{h}. {t}" for h, t in meta["declarations"]]
    return "\n\n".join(parts).replace("**", "")


if __name__ == "__main__":
    B, refs = number_citations(blocks())
    meta = dict(title=TITLE, abstract=ABSTRACT, keywords=KEYWORDS, declarations=DECLARATIONS, references=refs,
                author_lines=["[Author names and affiliations to be completed by the authors]",
                              "Corresponding author: [name, e-mail]"])
    (OUT / "manuscript_text.txt").write_text(plain_text(B, meta), encoding="utf-8")
    build_docx(B, OUT / "E-XMAI_manuscript.docx", meta)
    build_pdf(B, OUT / "E-XMAI_manuscript.pdf", meta)

    reg = ("table", "Register of changes from the base paper (identifiers [C1]–[C12] mark the shaded passages).",
           ["ID", "Base paper plan / proposal element", "Treatment in this manuscript"],
           [[c[0], c[1], c[2]] for c in CHANGES], [0.5, 3.0, 3.6])
    meta_h = dict(meta, title=TITLE + " — changes from the base paper highlighted",
                  preface=[("h1", "Summary of changes from the base paper"),
                           ("p", "The base paper is a research proposal with an embedded step-by-step journal "
                                 "workflow; it contains no results. Shaded passages below are the parts of this "
                                 "manuscript that implement, narrow or depart from the base paper's plan. Unshaded "
                                 "text is standard manuscript material."), reg])
    build_pdf(B, OUT / "E-XMAI_manuscript_changes_highlighted.pdf", meta_h, highlight=True)
    print("built", sorted(p.name for p in OUT.iterdir()))
