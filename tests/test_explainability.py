from src.explainability.grad_cam import generate_gradcam_overlay
from src.explainability.shap_analyzer import compute_shap_attributions
from src.explainability.lime_explainer import LIMEExplainer

def test_grad_cam_overlay():
    b64 = generate_gradcam_overlay()
    assert isinstance(b64, str)
    assert len(b64) > 100

def test_shap_attributions():
    features = compute_shap_attributions({'ca125': 48.5})
    assert isinstance(features, list)
    assert len(features) > 0
    assert 'shap_value' in features[0]

def test_lime_explainer():
    explainer = LIMEExplainer()
    res = explainer.explain_instance(['carcinoma', 'biopsy'])
    assert isinstance(res, list)
    assert res[0]['is_keyword'] is True
