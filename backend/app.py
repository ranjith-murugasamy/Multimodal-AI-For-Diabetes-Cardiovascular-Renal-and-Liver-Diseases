from __future__ import annotations

import csv
import io
import math
import os
import re
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "input"
UPLOAD_DIR = INPUT_DIR / "uploads"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
# Points contributed by a feature one "span" above its reference at unit weight.
CONTRIBUTION_SCALE = 100.0

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES + 64 * 1024

FEATURE_RANGES = {
    "age": (18, 110),
    "bmi": (10, 80),
    "glucose": (30, 600),
    "systolic_bp": (60, 260),
    "cholesterol": (50, 600),
    "creatinine": (0.1, 30),
    "egfr": (1, 160),
    "alt": (1, 3000),
    "ast": (1, 3000),
    "smoking": (0, 1),
    "alcohol_use": (0, 1),
}

DISEASES = [
    {
        "key": "diabetes",
        "name": "Diabetes",
        "short": "DM",
        "color": "#bb653d",
        "cues": {
            "high blood sugar": 15,
            "elevated glucose": 12,
            "frequent urination": 12,
            "excessive thirst": 10,
            "diabetes": 8,
            "prediabetes": 6,
        },
        "features": {
            "glucose": ("Blood glucose", 100, 140, 0.16),
            "bmi": ("BMI", 25, 12, 0.18),
            "age": ("Age", 45, 35, 0.08),
            "systolic_bp": ("Systolic blood pressure", 120, 40, 0.06),
        },
    },
    {
        "key": "cardiovascular",
        "name": "Cardiovascular",
        "short": "CVD",
        "color": "#b74755",
        "cues": {
            "chest pain": 16,
            "shortness of breath": 12,
            "high blood pressure": 10,
            "heart disease": 12,
            "palpitations": 10,
            "smoker": 8,
        },
        "features": {
            "systolic_bp": ("Systolic blood pressure", 120, 55, 0.17),
            "cholesterol": ("Total cholesterol", 200, 130, 0.16),
            "age": ("Age", 45, 40, 0.11),
            "smoking": ("Smoking status", 0, 1, 0.12),
            "bmi": ("BMI", 25, 15, 0.06),
        },
    },
    {
        "key": "renal",
        "name": "Renal",
        "short": "CKD",
        "color": "#487798",
        "cues": {
            "reduced egfr": 16,
            "low egfr": 16,
            "elevated creatinine": 16,
            "kidney disease": 12,
            "swelling": 8,
            "protein in urine": 10,
        },
        "features": {
            "creatinine": ("Creatinine", 1, 5, 0.2),
            "egfr": ("eGFR", 90, 70, -0.22),
            "systolic_bp": ("Systolic blood pressure", 120, 55, 0.08),
            "glucose": ("Blood glucose", 100, 160, 0.06),
            "age": ("Age", 45, 40, 0.05),
        },
    },
    {
        "key": "liver",
        "name": "Liver",
        "short": "CLD",
        "color": "#758749",
        "cues": {
            "elevated alt": 14,
            "elevated liver enzymes": 14,
            "liver disease": 12,
            "jaundice": 12,
            "heavy alcohol": 10,
            "fatty liver": 10,
        },
        "features": {
            "alt": ("ALT", 40, 160, 0.22),
            "ast": ("AST", 40, 160, 0.12),
            "bmi": ("BMI", 25, 18, 0.1),
            "alcohol_use": ("Alcohol use noted", 0, 1, 0.1),
            "age": ("Age", 45, 40, 0.04),
        },
    },
]


def _number(payload: dict[str, Any], key: str, default: float) -> float:
    value = payload.get(key, default)
    if isinstance(value, bool):
        raise ValueError(f"{key} must be a number.")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be a number.") from exc
    low, high = FEATURE_RANGES[key]
    if not math.isfinite(parsed) or not low <= parsed <= high:
        raise ValueError(f"{key} must be between {low:g} and {high:g}.")
    return parsed


def _normalize_weights(payload: dict[str, Any]) -> tuple[float, float]:
    try:
        clinical = float(payload.get("clinical_weight", 0.75))
        text = float(payload.get("text_weight", 0.25))
    except (TypeError, ValueError) as exc:
        raise ValueError("Modality weights must be numbers.") from exc
    if not math.isfinite(clinical) or not math.isfinite(text) or clinical < 0 or text < 0:
        raise ValueError("Modality weights must be finite, non-negative numbers.")
    total = clinical + text
    if total == 0:
        raise ValueError("At least one modality weight must be greater than zero.")
    return clinical / total, text / total


def _risk_band(score: float) -> str:
    if score >= 65:
        return "Elevated"
    if score >= 38:
        return "Review"
    return "Lower"


def calculate_predictions(payload: dict[str, Any]) -> dict[str, Any]:
    values = {
        key: _number(payload, key, default)
        for key, default in {
            "age": 52,
            "bmi": 27,
            "glucose": 105,
            "systolic_bp": 122,
            "cholesterol": 190,
            "creatinine": 0.9,
            "egfr": 95,
            "alt": 28,
            "ast": 26,
            "smoking": 0,
            "alcohol_use": 0,
        }.items()
    }
    clinical_weight, text_weight = _normalize_weights(payload)
    note = payload.get("clinical_note", "")
    if not isinstance(note, str) or len(note) > 2000:
        raise ValueError("Clinical note must be text of at most 2,000 characters.")
    normalized_note = re.sub(r"\s+", " ", note.casefold())
    results = []

    for disease in DISEASES:
        clinical_contributions = []
        raw_score = 0.0
        for key, (label, reference, span, direction) in disease["features"].items():
            delta = values[key] - reference
            contribution = max(-12.0, min(24.0, (delta / span) * CONTRIBUTION_SCALE * direction))
            raw_score += contribution
            clinical_contributions.append(
                {
                    "feature": label,
                    "value": values[key],
                    "contribution": round(contribution, 1),
                    "modality": "Clinical",
                }
            )
        clinical_score = max(0.0, min(100.0, 28.0 + raw_score))

        matches = [
            {"feature": cue.title(), "value": True, "contribution": weight, "modality": "Note"}
            for cue, weight in disease["cues"].items()
            if cue in normalized_note
        ]
        text_score = min(100.0, 18.0 + sum(item["contribution"] for item in matches))
        fused_score = round(clinical_weight * clinical_score + text_weight * text_score)
        contributions = [
            {**item, "contribution": round(item["contribution"] * clinical_weight, 1)}
            for item in clinical_contributions
        ] + [
            {**item, "contribution": round(item["contribution"] * text_weight, 1)}
            for item in matches
        ]
        contributions.sort(key=lambda item: abs(item["contribution"]), reverse=True)
        results.append(
            {
                "key": disease["key"],
                "name": disease["name"],
                "short": disease["short"],
                "color": disease["color"],
                "score": fused_score,
                "band": _risk_band(fused_score),
                "clinical_score": round(clinical_score),
                "text_score": round(text_score),
                "contributions": contributions[:5],
                "matched_note_cues": [item["feature"] for item in matches],
            }
        )

    return {
        "results": results,
        "weights": {"clinical": round(clinical_weight, 3), "text": round(text_weight, 3)},
        "model_status": "illustrative_unvalidated",
        "disclaimer": (
            "Demonstration only: these uncalibrated scores are not probabilities, "
            "diagnoses, or clinical advice."
        ),
    }


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "E-XMAI research demonstrator"})


@app.errorhandler(413)
def upload_too_large(_error):
    return jsonify({"error": "CSV files must be 5 MB or smaller."}), 413


@app.get("/api/dataset")
def dataset():
    path = INPUT_DIR / "synthetic_demo_patients.csv"
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    return jsonify(
        {
            "name": path.name,
            "rows": len(rows),
            "type": "synthetic",
            "use": "UI example only; not used to train or validate the illustrative scoring rules.",
            "columns": list(rows[0]) if rows else [],
        }
    )


@app.post("/api/dataset/upload")
def upload_dataset():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "Choose a CSV file to upload."}), 400
    if not uploaded.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported."}), 400
    content = uploaded.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        return jsonify({"error": "CSV files must be 5 MB or smaller."}), 413
    try:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        columns = reader.fieldnames or []
        rows = sum(1 for _ in reader)
    except (UnicodeDecodeError, csv.Error) as exc:
        return jsonify({"error": f"Could not parse CSV: {exc}"}), 400
    required = {"age", "bmi", "glucose", "systolic_bp"}
    missing = sorted(required - set(columns))
    if missing:
        return jsonify({"error": f"Missing required columns: {', '.join(missing)}."}), 400
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = UPLOAD_DIR / f"dataset-{uuid.uuid4().hex[:12]}.csv"
    saved_path.write_bytes(content)
    return jsonify(
        {
            "name": saved_path.name,
            "rows": rows,
            "columns": columns,
            "type": "user upload",
            "use": "Saved locally for research exploration; not used by the illustrative scoring endpoint.",
        }
    ), 201


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400
    try:
        return jsonify(calculate_predictions(payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("BACKEND_PORT", "5002")), debug=False)
