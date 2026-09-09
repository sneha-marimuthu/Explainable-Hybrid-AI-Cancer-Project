# API Reference Specification

## Base URL
`http://localhost:8000/api/v1`

## Endpoints

### 1. GET `/health`
Returns system status and model version.

### 2. POST `/predict`
Executes end-to-end multimodal inference and XAI heatmap generation.

**Form Parameters:**
- `image` *(optional UploadFile)*: Histopathology / Radiology image file (`.png`, `.jpg`, `.dcm`).
- `report_text` *(string)*: Clinical pathology report text.
- `vitals` *(JSON string)*: Patient vitals & lab biomarker values.

**Response (JSON):**
```json
{
  "id": "DIAG-1787293572",
  "status": "completed",
  "cancer_type": "Breast Cancer",
  "cancer_type_confidence": 0.942,
  "cancer_stage": "Stage IIA",
  "cancer_stage_confidence": 0.885,
  "treatment_recommendations": ["Surgical Lumpectomy", "Neoadjuvant Chemotherapy"],
  "survival_probability": 0.825,
  "grad_cam_image": "data:image/png;base64,...",
  "top_feature_importance": [
    {"feature": "CA-125 Biomarker", "shap_value": 1.34}
  ],
  "attention_scores": [
    {"word": "biopsy", "score": 0.85, "is_keyword": true}
  ]
}
```
