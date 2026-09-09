import torch
from src.models.cnn_model import VisionBackbone
from src.models.fusion_model import GatedCrossAttentionFusionModel
from src.models.xai_model import ExplainableCancerModel

def test_vision_backbone():
    model = VisionBackbone(architecture="resnet50", embedding_dim=1792, pretrained=False)
    x = torch.randn(2, 3, 300, 300)
    out = model(x)
    assert out.shape == (2, 1792)

def test_fusion_model():
    model = GatedCrossAttentionFusionModel(image_dim=1792, text_dim=768, tabular_dim=32)
    img = torch.randn(2, 1792)
    txt = torch.randn(2, 768)
    tab = torch.randn(2, 32)
    out = model(img, txt, tab)
    assert 'cancer_type' in out
    assert out['cancer_type'].shape == (2, 4)

def test_explainable_cancer_model():
    model = ExplainableCancerModel()
    img = torch.randn(2, 3, 300, 300)
    txt = torch.randn(2, 768)
    tab = torch.randn(2, 16)
    out = model(img, txt, tab)
    assert 'cancer_type' in out
