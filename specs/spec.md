# E-XMAI Multimodal Health Research Demonstrator — Specification

**Status:** Implementation baseline v2 (demonstrator + offline baseline experiment) · **Owner:** generated from supplied source material · **Last updated:** 2026-10-11

## 0. Source material

The supplied proposal is translated into an inspectable local application; the
prototype is intentionally narrower than the proposed clinical research
programme.

1. **`input/base-paper.pdf`** — proposal titled *Development of an Expandable
   Explainable AI Framework for Multimodal Prediction of Diabetes,
   Cardiovascular, Renal and Liver Diseases*. Its abstract and proposed
   three-paper progression describe multimodal prediction, four initial disease
   areas, local explanations, and future incremental/continual expansion.
2. **`input/generic-spec-template.docx`** and
   **`specs/generic-spec-template.md`** — the supplied reusable research-artifact
   specification template.
3. **Reference code:** none was supplied. Requirements therefore distinguish
   source-paper proposals from the behavior implemented here; no absent
   algorithm, metric, or clinical result is inferred.

## 1. Purpose

Make the proposal's high-level shape inspectable through a runnable research
demonstrator: enter synthetic or de-identified structured measures and a
clinical-note example, adjust modality weights, and inspect four illustrative
condition scores and their handcrafted contributing cues. Reproducibility means
versioned source, a small synthetic fixture, validated request contracts, and a
single lifecycle script—not replication of clinical performance.

## 2. Source gaps and implementation boundary

The supplied manuscript proposes LightGBM, CatBoost and TabNet for an initial
multidisease study and discusses SHAP/LIME; its broader programme also proposes
continual learning, counterfactual explanations and evaluation of catastrophic
forgetting. The supplied PDF does not provide a runnable implementation or
clinical dataset/results sufficient to reproduce those claims.

1. **No reference implementation or fitted model artifacts.** The application
   cannot claim to reproduce model architectures, preprocessing, or reported
   scores from code that was not provided.
2. **No completed, reproducible evaluation is specified.** Cohort provenance,
   eligibility, labels, split protocol, calibration, and test-set results are
   not available in the supplied materials.
3. **The proposal is broader than a safe prototype.** Incremental learning,
   retention/forgetting analysis, SHAP/LIME, and counterfactual explanations
   are future research requirements, not implemented capabilities.

The proposal's own workflow section, however, does specify a protocol that
*can* be executed without private data: four public single-disease datasets,
LightGBM / CatBoost / Random Forest baselines, training-fold-only preprocessing,
repeated evaluation with confidence intervals, and SHAP summaries. That protocol
is implemented as an offline script (FR-13 to FR-16). Because the four datasets
describe different patients, they are **not** a linked multimodal cohort; the
proposal itself flags this.

This application therefore has two parts: (a) the web demonstrator, which uses
transparent, bounded, handcrafted scoring rules for demonstration only, and (b)
an offline baseline experiment on public data that is reported separately. The displayed contributions are rule terms, not SHAP,
LIME, causal effects, or clinically meaningful risk factors. Synthetic fixture
records are not used to train or validate the rules, and the public-dataset
experiment does not feed the demonstrator. Uploaded CSV files are
stored locally for research exploration and do not feed inference.

## 3. Users and use cases

- **Researcher:** explores how input measures and note-cue matches flow through
  the prototype; adjusts and inspects normalized modality weights.
- **Reviewer or collaborator:** checks the implementation boundary, data
  provenance, per-output terms, API behavior, and explicit non-claims.

## 4. Functional requirements

### 4.1 Inputs and provenance

- **FR-1:** Bundle the supplied paper and generic specification template under
  `input/`; identify the sample patient CSV as synthetic.
- **FR-2:** Collect bounded demographic, anthropometric, cardiovascular, renal,
  hepatic and lifestyle example fields plus an optional text note.
- **FR-3:** Show the sample dataset's row/column summary and explain that it is
  not used to train or validate the scoring rules.
- **FR-4:** Accept CSV uploads up to 5 MB, validate UTF-8 and required headers,
  and save accepted files with generated safe filenames under `input/uploads/`.
  Uploaded files are not used by `/api/predict`.

### 4.2 Scoring and explanations

- **FR-5:** Return separate illustrative indices for diabetes, cardiovascular,
  renal and liver modules.
- **FR-6:** Fuse the structured input index with matching note-cue index using
  non-negative clinical and text weights normalized to sum to one.
- **FR-7:** Return per-module modality scores, a qualitative demo band, matched
  note cues, and the largest signed handcrafted feature terms.
- **FR-8:** Label every score and explanation as unvalidated demonstration
  output; do not present scores as calibrated probabilities or diagnoses.

### 4.3 Offline baseline experiment

- **FR-13:** `scripts/run_experiments.py` loads one public OpenML dataset per
  disease area (Pima diabetes, Statlog heart, chronic kidney disease, ILPD
  liver) and trains LightGBM, CatBoost and Random Forest on each.
- **FR-14:** Use 5×5 repeated stratified cross-validation with imputation and
  encoding fitted inside training folds only, fixed hyperparameters, and a fixed
  0.5 threshold; report accuracy, sensitivity, specificity, F1, AUROC, AUPRC and
  Brier score with SD and 95% CI, plus fit/predict time.
- **FR-15:** Compare models with the Nadeau–Bengio corrected resampled t-test on
  per-fold AUROC, Holm-adjusted across all comparisons.
- **FR-16:** Compute SHAP (TreeExplainer, LightGBM) on held-out folds, report the
  top features per disease and the top-5 Jaccard stability across folds.
- **FR-17:** Store `experiment_results.json`, `per_fold_metrics.csv`,
  `shap_top_features.csv` and figures under `output/results/`.

### 4.4 Application and operations

- **FR-9:** Provide a responsive React application styled with Tailwind CSS,
  including overview, full assessment, and data/methodology views.
- **FR-10:** Provide Flask JSON endpoints for health, dataset metadata, local
  CSV upload, and scoring.
- **FR-11:** Provide `scripts/app.sh` commands to set up, start, stop, restart,
  inspect status, and follow backend/frontend logs.
- **FR-12:** Save an example JSON response, a size inventory, screenshots, and
  both a manuscript development draft and a revised final manuscript draft in
  `output/`.
- **FR-18:** Produce the final manuscript as DOCX and PDF from one source
  (`scripts/build_paper.py`) with all numbers read from the result files, and a
  local text-overlap report (`scripts/similarity_check.py`).

## 5. Non-functional requirements

- **NFR-1:** Work locally on macOS/Linux with Python 3 and Node.js/npm; no GPU
  or external runtime API is required.
- **NFR-2:** Validate numeric ranges, finite values, weight normalization,
  upload size/type, and required CSV columns.
- **NFR-3:** Keep source inputs and generated deliverables below 80 MB in total;
  report the measured input/output inventory.
- **NFR-4:** Do not transmit uploaded CSVs; serve the API on loopback by default.
- **NFR-5:** Do not represent the prototype as a clinical decision-support
  product, validated diagnostic model, or completed clinical study.

## 6. Architecture

- **Frontend:** React 19, Vite, Tailwind CSS 4.
- **Backend:** Flask REST API in `backend/app.py`; Vite proxies `/api` to the
  local backend during development.
- **Input:** source proposal, generic specification template, and a ten-row
  synthetic illustrative fixture.
- **Output:** manuscript drafts, API sample, screenshot captures, and measured
  size inventory.
- **State:** no database or remote service; accepted CSV uploads are stored
  locally with generated filenames.

## 7. Explicitly deferred

- TabNet, neural, or multimodal-transformer models, and any training on an
  appropriately governed *linked* multimodal clinical cohort.
- LIME, counterfactual explanations, calibration curves/recalibration,
  subgroup/fairness analysis, external validation, hyperparameter tuning, or
  clinical thresholds. (SHAP and baseline evaluation on public data are done.)
- Continual/incremental learning, new disease registration, catastrophic
  forgetting measurement, and deployment in clinical workflows.
- A plagiarism-check certification, similarity-score guarantee, journal
  acceptance, or ethics approval.

These require data, methods, approvals, model artifacts, and independent
evaluation not present in the source bundle.

## 8. Acceptance criteria and verification

| Criterion | Verification |
|---|---|
| One script sets up, starts, reports, and stops both services | `./scripts/app.sh start`, `status`, `stop` |
| API returns four scores and transparent explanations | `python -m unittest discover -s backend/tests` |
| Input bounds and invalid fusion weights fail with a client error | Backend unit tests and `/api/predict` |
| CSV import enforces size/header constraints and remains local | `backend/app.py` upload tests/manual request |
| Frontend compiles with React and Tailwind | `npm run build` in `frontend/` |
| Synthetic/data/clinical non-claims are visible in the UI and manuscript | Review UI and `output/paper/02_final_manuscript.md` |
| Bundled input and generated output are below 80 MB | `output/results/artifact_size_report.json` |
| Baseline experiment reproduces from one command with fixed seed | `.venv/bin/python scripts/run_experiments.py` (needs `backend/requirements-research.txt`) |
| Paper numbers equal result-file numbers; DOCX and PDF are produced | `python scripts/build_paper.py`; `output/paper/final/` |
| Text overlap with the supplied proposal is low | `python scripts/similarity_check.py` (local n-gram report, not a commercial checker) |

## 9. Responsible-use note

The prototype is for software/research-method exploration only. It is not
validated, calibrated, or intended for clinical decisions. Do not enter
identifiable or real patient data. Public datasets are de-identified and used under their
repository terms. The supplied source's authorship and date
were not provided; those bibliographic details and any required ethics,
funding, data-availability, and author-contribution statements must be verified
by the research team before submission.
