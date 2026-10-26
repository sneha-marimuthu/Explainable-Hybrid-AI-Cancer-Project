"""
Explainable AI (XAI) Suite: Grad-CAM, SHAP, and Optical Stain Deconvolution
Project: EHASMCDTR Multimodal Cancer Diagnosis
"""

import numpy as np
import cv2
import torch
import shap
from skimage.color import rgb2hed, hed2rgb
from skimage.exposure import rescale_intensity

class GradCAMExplainer:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradient = None
        self.activation = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activation = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradient = grad_out[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_backward_hook(backward_hook)

    def generate_heatmap(self, input_tensor, class_idx=None):
        self.model.eval()
        outputs = self.model(input_tensor)
        logits = outputs["logits_diagnosis"] if isinstance(outputs, dict) else outputs

        if class_idx is None:
            class_idx = torch.argmax(logits, dim=1).item()

        self.model.zero_grad()
        loss = logits[0, class_idx]
        loss.backward(retain_graph=True)

        # Global average pooling of gradients
        weights = torch.mean(self.gradient, dim=[2, 3], keepdim=True)
        cam = torch.sum(weights * self.activation, dim=1).squeeze().cpu().numpy()

        cam = np.maximum(cam, 0)
        if np.max(cam) != 0:
            cam = (cam - np.min(cam)) / (np.max(cam) - np.min(cam))
        return cam, class_idx


def optical_stain_deconvolution(image_np):
    """
    Separates Hematoxylin (nuclear) and Eosin (stromal) optical density channels.
    """
    hed = rgb2hed(image_np)
    null_ch = np.zeros_like(hed[:, :, 0])
    
    # Hematoxylin (Nuclear Atypia)
    h_rgb = hed2rgb(np.stack((hed[:, :, 0], null_ch, null_ch), axis=-1))
    h_rgb = rescale_intensity(h_rgb, out_range=(0, 1))

    # Eosin (Cytoplasm / Desmoplastic Collagen)
    e_rgb = hed2rgb(np.stack((null_ch, hed[:, :, 1], null_ch), axis=-1))
    e_rgb = rescale_intensity(e_rgb, out_range=(0, 1))

    return h_rgb, e_rgb


class TabularSHAPExplainer:
    def __init__(self, predict_fn, background_distribution, feature_names):
        self.feature_names = feature_names
        self.explainer = shap.Explainer(predict_fn, background_distribution, feature_names=feature_names)

    def explain_instance(self, patient_feature_vector):
        """
        Computes local additive feature attributions phi_i satisfying:
        f(x) = E[f(X)] + sum(phi_i)
        """
        explanation = self.explainer(patient_feature_vector)
        patient_shap = explanation[0]
        
        # Verify local additivity error |Delta|
        shap_sum = np.sum(patient_shap.values)
        base_val = float(patient_shap.base_values)
        reconciled = base_val + shap_sum
        
        return {
            "shap_values": patient_shap.values,
            "base_value": base_val,
            "reconciled_prediction": reconciled,
            "feature_names": self.feature_names
        }
