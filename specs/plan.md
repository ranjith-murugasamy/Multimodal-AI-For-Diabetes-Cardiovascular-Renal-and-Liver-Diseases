# Technical plan

## Layout
```
backend/app.py                 Flask API + handcrafted scoring rules
backend/tests/test_app.py      API/validation/regression tests
backend/requirements*.txt      runtime (Flask) and research (ML) dependencies
frontend/src/App.jsx           React 19 + Tailwind 4 single-page UI (hash-addressable pages)
scripts/app.sh                 setup | start | stop | restart | status | logs
scripts/run_experiments.py     offline baseline experiment (public OpenML data)
scripts/build_paper.py         builds DOCX + PDF from result files
scripts/similarity_check.py    local n-gram overlap report vs. supplied proposal
input/                         proposal PDF, spec template, synthetic fixture, uploads/
output/results/                experiment + API sample + size report + figures
output/screenshots/            UI captures
output/paper/                  drafts and final/ (DOCX, PDF, similarity report)
```

## Data flow
1. UI → `POST /api/predict` → clamp/validate → per-disease clinical index
   `C = clip(28 + Σ clip(((x-ref)/span)·100·w, -12, 24), 0, 100)`,
   note index `T = min(100, 18 + Σ cue weights)`, fused
   `S = round(w_c·C + w_t·T)` with `w_c + w_t = 1`; bands: ≥65 Elevated, ≥38 Review.
2. `run_experiments.py` → OpenML fetch → fold-wise pipeline (impute/encode → model)
   → metrics → corrected t-tests → SHAP → JSON/CSV/PNG.
3. `build_paper.py` reads `experiment_results.json` and writes DOCX + PDF.

## API
`GET /api/health`, `GET /api/dataset`, `POST /api/dataset/upload`, `POST /api/predict`.

## Frontend pages
Risk overview, Patient assessment, Data & methodology.
