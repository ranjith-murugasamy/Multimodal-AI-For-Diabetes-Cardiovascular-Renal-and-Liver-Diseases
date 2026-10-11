# Proposal requirement mapping

| Proposal requirement | Status | Where |
|---|---|---|
| Four disease areas (DM, CVD, CKD, CLD) | Implemented (separate public datasets; demo modules) | `scripts/run_experiments.py`, `backend/app.py` |
| Multimodal integration of heterogeneous data | Partially: demo fuses structured values + note cues; datasets are not linked multimodal | `backend/app.py`, paper §3.8, §5 |
| LightGBM, CatBoost, Random Forest comparison | Implemented | `output/results/experiment_results.json` |
| TabNet | Out of scope (not run) | spec §7 |
| SHAP explanations | Implemented (LightGBM TreeExplainer) | `output/results/shap_top_features.csv` |
| LIME, counterfactual explanations | Out of scope | spec §7 |
| Metrics: accuracy, precision/F1, sensitivity, specificity, AUROC, AUPRC | Implemented | `per_fold_metrics.csv` |
| Calibration | Partially: Brier score only; no calibration curves | paper §5.1 |
| Explanation consistency | Partially: top-5 Jaccard across folds | `experiment_results.json` |
| Repeated evaluation, CIs, paired tests | Implemented (5×5 CV, 95% CI, corrected t, Holm) | same |
| Leakage prevention (train-fold-only preprocessing) | Implemented | `run_experiments.py` |
| Missing-data robustness, external validation | Out of scope | paper §5.1 |
| Computational cost | Implemented (fit/predict seconds) | `experiment_results.json` |
| Continual/incremental learning, forgetting | Out of scope (future Paper 2) | spec §7 |
| Adaptive/personalised models (Paper 3) | Out of scope | spec §7 |
| Network/feature-association component (journal workflow) | Out of scope | paper §5.1 |
