# Change summary

The revised manuscript was written as original prose from the supplied proposal
and the behavior of this software demonstrator. It narrows the proposed clinical
research programme to an honest, reproducible software artifact and distinguishes
planned methodology from completed implementation.

| Topic | Supplied proposal | Demonstrator and revised manuscript |
|---|---|---|
| Disease scope | Diabetes, cardiovascular, renal and liver diseases | Four separate illustrative scoring modules for the same disease areas |
| Modalities | Demographic, clinical, biochemical, lifestyle and physiological data | Bounded structured example inputs plus optional note-text cue matching |
| Algorithms | Proposes LightGBM, CatBoost and TabNet; later continual/adaptive models | Handcrafted rules only; no trained models or clinical cohort |
| Explanations | SHAP, LIME and counterfactual methods are proposed | Direct display of rule contributions; explicitly not SHAP/LIME/counterfactuals |
| Expandability | Incremental learning and retention are research objectives | Modular code scaffold only; no continual learning or forgetting experiment |
| Evidence | Describes intended metrics and experiments | No clinical metrics, performance claims, or fabricated results |
| Deliverable | Research proposal / planned programme | React/Tailwind frontend, Flask API, synthetic fixture, tests, operations script, and manuscript package |

The final manuscript states the evidentiary boundary, synthetic-data status,
upload limitation, and future validation requirements. It does not claim to have
passed a plagiarism detector. A similarity checker and citation review by the
authors/editor remain necessary; no software can guarantee a particular result.

## Update 2026-10-11 (final package)

- Added a real, reproducible baseline experiment (public OpenML data; LightGBM,
  CatBoost, Random Forest; SHAP; corrected resampled t-tests) and rewrote the
  manuscript around it: `paper/final/`.
- Fixed a scoring defect in `backend/app.py`: the per-feature scale constant (16)
  was applied on top of weights of ~0.1–0.2, capping contributions near 3 points so
  no profile could leave the Lower band. Scale is now 100; regression test added.
- Local similarity check: 0.0% 8-gram and 0.04% 6-gram overlap with the proposal;
  the only 6-word shared run is the programme name "Expandable and Explainable
  Multimodal Artificial Intelligence". Not an iThenticate/Turnitin result.
