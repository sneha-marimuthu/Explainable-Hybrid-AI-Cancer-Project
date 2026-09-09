from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_predict_endpoint():
    response = client.post("/api/v1/predict", data={
        "report_text": "Invasive ductal carcinoma biopsy.",
        "vitals": '{"age": 58, "ca125": 48.5}'
    })
    assert response.status_code == 200
    json_data = response.json()
    assert "cancer_type" in json_data
    assert "grad_cam_image" in json_data
