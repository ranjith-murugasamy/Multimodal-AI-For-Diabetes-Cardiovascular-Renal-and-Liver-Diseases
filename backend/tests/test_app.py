import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as backend  # noqa: E402
from app import app, calculate_predictions  # noqa: E402


class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_predict_returns_four_explained_demo_scores(self):
        response = self.client.post("/api/predict", json={})
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual([item["key"] for item in body["results"]], [
            "diabetes", "cardiovascular", "renal", "liver"
        ])
        self.assertTrue(all("contributions" in item for item in body["results"]))
        self.assertEqual(body["model_status"], "illustrative_unvalidated")

    def test_default_profile_is_lower_and_abnormal_profile_leaves_lower_band(self):
        baseline = calculate_predictions({})["results"]
        self.assertTrue(all(item["band"] == "Lower" for item in baseline))
        abnormal = calculate_predictions(
            {"age": 70, "bmi": 38, "glucose": 260, "systolic_bp": 170, "cholesterol": 300,
             "creatinine": 3.5, "egfr": 30, "alt": 140, "ast": 120, "smoking": 1, "alcohol_use": 1}
        )["results"]
        self.assertTrue(all(item["score"] > base["score"] + 20 for item, base in zip(abnormal, baseline)))
        self.assertTrue(all(item["band"] != "Lower" for item in abnormal))

    def test_note_cues_are_visible_in_the_explanation(self):
        result = calculate_predictions({"clinical_note": "Patient reports excessive thirst."})
        diabetes = result["results"][0]
        self.assertIn("Excessive Thirst", diabetes["matched_note_cues"])

    def test_weights_are_normalized(self):
        result = calculate_predictions({"clinical_weight": 3, "text_weight": 1})
        self.assertEqual(result["weights"], {"clinical": 0.75, "text": 0.25})

    def test_invalid_values_and_zero_weights_are_rejected(self):
        with self.assertRaises(ValueError):
            calculate_predictions({"age": 4})
        with self.assertRaises(ValueError):
            calculate_predictions({"clinical_weight": 0, "text_weight": 0})

    def test_dataset_is_explicitly_synthetic(self):
        response = self.client.get("/api/dataset")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["type"], "synthetic")

    def test_csv_upload_requires_expected_columns(self):
        response = self.client.post(
            "/api/dataset/upload",
            data={"file": (io_bytes("name,value\nx,1\n"), "wrong.csv")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required columns", response.get_json()["error"])

    def test_valid_csv_upload_is_stored_locally(self):
        csv_text = "age,bmi,glucose,systolic_bp\n52,27,105,122\n"
        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            backend, "UPLOAD_DIR", Path(temp_dir)
        ):
            response = self.client.post(
                "/api/dataset/upload",
                data={"file": (io_bytes(csv_text), "patient-data.csv")},
                content_type="multipart/form-data",
            )
            self.assertEqual(response.status_code, 201)
            saved_files = list(Path(temp_dir).glob("*.csv"))
            self.assertEqual(len(saved_files), 1)
            self.assertEqual(saved_files[0].read_text(encoding="utf-8"), csv_text)
            self.assertEqual(response.get_json()["rows"], 1)


def io_bytes(value):
    from io import BytesIO

    return BytesIO(value.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
