import numpy as np

def normalize_vitals(vitals_dict: dict) -> dict:
    """Normalizes clinical patient vitals & biomarker values."""
    cleaned = {}
    cleaned['age'] = float(vitals_dict.get('age', 50)) / 100.0
    cleaned['blood_pressure_systolic'] = float(vitals_dict.get('blood_pressure_systolic', 120)) / 200.0
    cleaned['blood_pressure_diastolic'] = float(vitals_dict.get('blood_pressure_diastolic', 80)) / 130.0
    cleaned['ca125'] = min(float(vitals_dict.get('ca125', 10.0)) / 100.0, 1.0)
    cleaned['cea'] = min(float(vitals_dict.get('cea', 2.0)) / 50.0, 1.0)
    cleaned['ki67'] = float(vitals_dict.get('ki67', 20)) / 100.0
    cleaned['bmi'] = float(vitals_dict.get('bmi', 24.0)) / 40.0
    return cleaned

def preprocess_clinical_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.strip().split())
