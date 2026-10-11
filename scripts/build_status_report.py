"""Status and approach report for the review guidance embedded in the base paper."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docgen import build_docx, build_pdf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "paper" / "final"
RES = ROOT / "output" / "results"
E = json.loads((RES / "extended_results.json").read_text())
R = json.loads((RES / "experiment_results.json").read_text())
AT = E["ablation_tests"]
min_holm = min(t["p_holm"] for t in R["tests"])
abl_p = min(t["p_holm"] for t in AT)

A, P, N = "Addressed", "Partially addressed", "Not addressed"
# id, comment (paraphrased), where in base paper, status, approach, evidence
C = [
 ("RC-01", "No workflow or set of tables can guarantee acceptance; aim for a rigorous, reproducible paper that fits the network-modelling focus of the target journal.",
  "Workflow intro", P, "Reproducible pipeline (fixed seed, scripts, requirements, generated manuscript). Acceptance is not claimed. Journal-specific template/formatting is left to the authors once a journal is chosen.",
  "scripts/run_experiments.py, scripts/run_extended_analysis.py, scripts/build_paper.py"),
 ("RC-02", "Define exactly what the proposed method adds beyond LightGBM, CatBoost and Random Forest; the network component must contribute technically, not only as a visualisation.",
  "Step 1", A, "Defined as training-fold community scores from a Spearman feature-association network, concatenated to the original features and tested in a three-variant ablation. Result reported as is: no reliable gain (smallest Holm-adjusted p = {abl_p:.2f}).".replace("{abl_p:.2f}", f"{abl_p:.2f}"),
  "output/results/extended_results.json (ablation, ablation_tests); manuscript §3.6–3.7, §4.4, Table 5"),
 ("RC-03", "Select one public dataset per disease and document source, sample count, class distribution and features (Table 1).",
  "Step 2", A, "Pima diabetes, Statlog heart, chronic kidney disease and ILPD liver data via OpenML, with size, prevalence, feature and missingness counts.",
  "manuscript Table 1; output/results/experiment_results.json (datasets)"),
 ("RC-04", "Datasets with different patients/features are not automatically multimodal; unless modalities are genuinely linked, revise the title.",
  "Step 2 (Important)", A, "Title and claims revised to single-disease baselines; 'multimodal' is restricted to the demonstrator and the limitation is stated in the abstract, introduction and discussion.",
  "manuscript title, §1, §5.1"),
 ("RC-05", "Train the three baselines separately per disease and report accuracy, sensitivity, specificity, F1, AUROC, AUPRC from actual test predictions with CIs and repeated-run variability; do not choose thresholds on the test set (Table 2).",
  "Step 3", A, "5x5 repeated stratified CV; threshold fixed at 0.5 in advance; mean, SD and 95% CI per metric; 25 folds per dataset.",
  "output/results/per_fold_metrics.csv, experiment_results.json; manuscript Table 2, Fig. 1"),
 ("RC-06", "Build a separate feature-association network per disease with justified node/edge definitions; report nodes, edges, density, top central features, communities (Table 3); degree and betweenness; legends for Figures 2–3; do not read associations as causation.",
  "Step 4", A, "Nodes = preprocessed features, edges = |Spearman| >= 0.30 (fixed a priori); strength and betweenness via NetworkX; greedy modularity communities; legend in caption; association-only caveat in text.",
  "output/results/network_centrality.csv, figures/fig_networks.png, fig_centrality.png; manuscript Table 4, Figs. 2–3"),
 ("RC-07", "Implement the proposed algorithm and compare baseline, network-augmented variants and the full method (Table 4); SHAP alone is not a predictive component.",
  "Step 5", A, "Variants: original features, network scores only, original + network scores, for LightGBM and Random Forest; SHAP marked post-hoc in every variant; corrected t-test with Holm adjustment.",
  "output/results/ablation_per_fold.csv; manuscript Table 5"),
 ("RC-08", "Report top explanatory features with mean |SHAP|, direction and stability across runs (Table 5); SHAP summary plots (Fig. 4), local explanations (Fig. 5), cross-disease comparison (Fig. 6); no clinical-significance claims.",
  "Step 6", A, "Fold-wise SHAP for LightGBM; top-5 features with mean |SHAP|; top-5 Jaccard stability; beeswarm-style summary, held-out local explanations (one TP, one TN per disease) and cross-disease heatmap; explicit statement that SHAP is associational.",
  "output/results/shap_top_features.csv, figures/fig_shap_summary.png, fig_shap_local.png, fig_shap_cross_disease.png; manuscript Table 6, Figs. 4–6"),
 ("RC-09", "Statistical validation: mean/SD, 95% CIs, appropriate paired tests (Table 6).",
  "Step 7", A, f"95% t-intervals and Nadeau–Bengio corrected resampled t-tests, Holm-adjusted (smallest adjusted p = {min_holm:.2f}).",
  "experiment_results.json (tests); manuscript Table 3"),
 ("RC-10", "Robustness to missing data at predefined levels; calibration with Brier score and plots; ROC and PR curves (Figs. 7–9).",
  "Step 7", A, "Test-time MCAR missingness at 0/10/20/30/40%; Brier score, expected calibration error and reliability curves; pooled out-of-fold ROC/PR curves.",
  "extended_results.json (robustness, calibration); figures/fig_roc_pr.png, fig_calibration.png, fig_robustness.png; manuscript Table 7, Figs. 7–9"),
 ("RC-11", "External validation on independent data, if available.",
  "Step 7", N, "No independent cohort with matching variables was available in the supplied material; stated as a limitation and as required future work.",
  "manuscript §5.1"),
 ("RC-12", "Report computational cost: training time, inference time and model size.",
  "Step 7", A, "Full-data fit time, inference time per 1,000 records and serialized model size per learner and dataset.",
  "extended_results.json (cost); manuscript Table 7, §4.7"),
 ("RC-13", "All preprocessing and feature selection must be fitted on training data only; any resampling must happen inside training folds.",
  "Step 7", A, "Imputation, encoding, standardisation, network construction and community scoring are inside the cross-validation pipeline; no resampling used.",
  "scripts/run_experiments.py, run_extended_analysis.py (NetworkScores)"),
 ("RC-14", "Do not generate tables with assumed accuracy values; select datasets, implement, then calculate results.",
  "Closing remarks", A, "Every table and figure is generated from executed runs; the manuscript builder reads the result files directly.",
  "scripts/build_paper.py"),
 ("RC-15", "Follow the suggested results structure (4.1 data, 4.2 baselines, 4.3 network, 4.4 ablation, 4.5 explainability, 4.6 validation).",
  "Step 8", A, "Results section mirrors this order, with the demonstrator added as 4.8.",
  "manuscript §4"),
 ("RC-16", "Proposal (Paper 1) lists TabNet and LIME; the journal workflow lists Random Forest and SHAP only.",
  "Proposal table vs workflow", P, "Followed the journal workflow. TabNet and LIME were not run and are listed as not evaluated.",
  "manuscript Table 8, §5.1"),
 ("RC-17", "Proposal: shared multimodal architecture with disease-specific heads; later papers: continual learning, forgetting measurement, adaptive/personalised models, counterfactual explanations.",
  "Abstract; 3-paper flow", N, "Out of scope for a first-stage baseline paper. A transparent demonstrator and an explicit study design for the later stages are provided instead.",
  "manuscript §5.2, Table 8; specs/spec.md §7"),
 ("RC-18", "Thesis, budget and publication-cost planning sections.",
  "Budget and thesis outline", N, "Administrative planning content, not a manuscript or software requirement.",
  "n/a"),
]
counts = {s: sum(1 for c in C if c[3] == s) for s in (A, P, N)}

body = [
 ("h1", "1. What the base paper contains"),
 ("p", "The supplied base paper (14 pages) is a research proposal. It contains an abstract, a three-paper programme, "
       "a budget and thesis plan, and a step-by-step workflow for a first journal paper. It has no embedded PDF "
       "annotations or formal reviewer report. The review comments tracked here are therefore the directive guidance "
       "and cautions written into the workflow section, which function as reviewer-style requirements. Each was "
       "paraphrased, given an identifier, and checked against the implementation."),
 ("h1", "2. Status summary"),
 ("table", "Table 1. Status counts.", ["Status", "Count"],
  [[s, counts[s]] for s in (A, P, N)] + [["Total", len(C)]]),
 ("p", f"Headline outcomes: the three baselines are statistically indistinguishable after Holm adjustment "
       f"(smallest adjusted p = {min_holm:.2f}); the proposed network-assisted variant gave no reliable predictive "
       f"gain (smallest adjusted p = {abl_p:.2f}); this negative result is reported rather than hidden."),
 ("h1", "3. Comment register"),
 ("table", "Table 2. Review comments, status and approach.",
  ["ID", "Comment (paraphrased)", "Source", "Status", "Approach implemented", "Evidence"],
  [list(c) for c in C], [0.5, 2.2, 0.8, 0.8, 2.4, 1.6]),
 ("h1", "4. Defects found during the review"),
 ("bullet", "Demonstrator scoring: a scale constant (16) was multiplied with weights of about 0.1–0.2, limiting every feature contribution to about 3 points so that no profile could leave the Lower band. Scale changed to 100 and a regression test added (8 tests pass)."),
 ("bullet", "Evidence gap: the previous draft reported no results at all. It is replaced by the executed experiments above."),
 ("bullet", "Documentation gap: plan, tasks and requirement-mapping files required by the generic spec template were missing and were added under specs/."),
 ("h1", "5. Open items for the authors"),
 ("bullet", "Author names, affiliations, funding, competing interests and author contributions."),
 ("bullet", "Choice of journal, its template, and its AI-use policy; verification of every reference."),
 ("bullet", "An independent similarity check (iThenticate/Turnitin). The local n-gram check is not a substitute."),
 ("bullet", "Stage-two and stage-three studies (continual learning, adaptive and personalised models, LIME, counterfactuals, external validation)."),
 ("h1", "6. Deliverables"),
 ("table", "Table 3. Output inventory.", ["Location", "Content"],
  [["output/paper/final/E-XMAI_manuscript.pdf, .docx", "Clean manuscript with all tables, figures and the screenshot appendix"],
   ["output/paper/final/E-XMAI_manuscript_changes_highlighted.pdf", "Same manuscript with passages that differ from the base paper's plan shaded and tagged C1–C12, plus a change register"],
   ["output/paper/final/Review_Comment_Status_and_Approach.docx, .pdf", "This report"],
   ["output/paper/final/similarity_report.json", "Local n-gram overlap report"],
   ["output/results/figures/", "All 10 charts (AUROC, networks, centrality, SHAP summary/local/cross-disease/bars, ROC-PR, calibration, robustness)"],
   ["output/results/*.json, *.csv", "Experiment, extended-analysis, per-fold, SHAP, centrality and ablation results; API sample; size report"],
   ["output/screenshots/", "8 application screenshots (overview, example patient, assessment filled and submitted, renal view, data page, upload, mobile)"]],
  [3.0, 4.0]),
]
meta = dict(title="Status and Approach for the Review Comments in the Base Paper",
            author_lines=["E-XMAI multimodal-health-xai project", "Status as of 11 October 2026"])
build_docx(body, OUT / "Review_Comment_Status_and_Approach.docx", meta, line_numbers=False)
build_pdf(body, OUT / "Review_Comment_Status_and_Approach.pdf", meta)
print(counts)
