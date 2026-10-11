# E-XMAI research demonstrator

*Development of an Expandable Explainable AI Framework for Multimodal Prediction
of Diabetes, Cardiovascular, Renal and Liver Diseases*. This project is a software
demonstrator, not a reproduction of a validated clinical model.

## Start and stop

From this folder, run the single lifecycle script:

```sh
./scripts/app.sh start
./scripts/app.sh status
./scripts/app.sh stop
```

`start` creates a project-local Python virtual environment, installs Flask and
the frontend packages if needed, then starts both local services. Open
<http://127.0.0.1:5173>. The script also supports `setup`, `restart`, and
`logs backend|frontend`. Default ports are 5002 (API) and 5173 (web); override
them with `BACKEND_PORT` and `FRONTEND_PORT`.

## What is implemented

- Four illustrative disease modules (diabetes, cardiovascular, renal, and liver).
- A small, explicitly synthetic CSV fixture and editable demographic/clinical
  values plus a free-text note.
- A configurable, normalized fusion of structured measures and simple note-cue
  matches, with the contributing handcrafted terms surfaced in the UI.
- A CSV upload endpoint that validates and stores files locally for exploration.
  Imported files do **not** train a model or change the scoring endpoint.
- REST API at `/api/health`, `/api/dataset`, `/api/dataset/upload`, and
  `/api/predict`.

## Research and safety boundary

The input paper is a proposal describing a planned research programme. It does
not include a runnable reference implementation, a defined clinical cohort,
trained model artifacts, or completed validation results. Accordingly, the app
uses handcrafted demonstration rules, not LightGBM/CatBoost/TabNet, SHAP, LIME,
counterfactuals, or continual learning. Displayed values are uncalibrated
illustrative indices, not probabilities, diagnoses, or medical advice. Do not
enter identifiable or real patient data; this prototype is not suitable for
clinical use.

The manuscript drafts in `output/paper/` describe that boundary and do not claim
clinical performance, journal acceptance, or a plagiarism-check pass. A
similarity tool result cannot be guaranteed; authors should verify citations,
complete missing authorship/ethics details, and use their institution's
approved originality workflow before submission.

See `specs/spec.md` for requirements and `output/results/` for the saved demo
response and artifact size report.
