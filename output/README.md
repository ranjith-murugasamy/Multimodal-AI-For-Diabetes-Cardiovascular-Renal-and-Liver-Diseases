# Generated outputs

- `paper/final/`
  - `E-XMAI_manuscript.pdf` / `.docx` — clean manuscript (8 tables, 10 figures, screenshot appendix).
  - `E-XMAI_manuscript_changes_highlighted.pdf` — same text with passages that implement or depart from the
    base paper's plan shaded and tagged C1–C12, plus a change register.
  - `Review_Comment_Status_and_Approach.pdf` / `.docx` — status and approach for each review comment in the base paper.
  - `similarity_report.json` — local n-gram overlap (not a commercial plagiarism checker).
- `results/` — `experiment_results.json`, `extended_results.json`, `per_fold_metrics.csv`,
  `ablation_per_fold.csv`, `shap_top_features.csv`, `network_centrality.csv`,
  `example_predict_response.json`, `artifact_size_report.json`, and `figures/` (10 charts).
- `screenshots/` — 8 captures of the running application.
- `paper/01_*`, `02_*`, `change_summary.md` — earlier drafts, superseded.

Regenerate: `scripts/run_experiments.py`, `scripts/run_extended_analysis.py`, then
`scripts/build_paper.py`, `scripts/build_status_report.py`, `scripts/similarity_check.py`
(use `.venv/bin/python`; research dependencies in `backend/requirements-research.txt`).

The demonstrator's scores are illustrative. Experiment results use public, de-identified
datasets and are not clinical evidence.
