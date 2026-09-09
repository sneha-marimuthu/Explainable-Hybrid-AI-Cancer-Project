import torch
import torch.nn.functional as F
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from typing import Tuple, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class GradCAM:
    """Grad-CAM implementation for visual explanations"""
    
    def __init__(self, model, target_layer: str = 'layer4.2'):
        self.model = model
        self.target_layer = self._find_layer(target_layer)
        self.gradients = None
        self.activations = None
        self._register_hooks()
    
    def _find_layer(self, layer_name: str):
        """Find target layer by name"""
        for name, module in self.model.named_modules():
            if name == layer_name:
                return module
        # Fallback to last Conv2d layer if specific named layer not found
        conv_layers = [m for m in self.model.modules() if isinstance(m, torch.nn.Conv2d)]
        if conv_layers:
            return conv_layers[-1]
        raise ValueError(f"Layer {layer_name} not found")
    
    def _register_hooks(self):
        """Register forward and backward hooks"""
        def forward_hook(module, input, output):
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)
    
    def generate(self, input_tensor: torch.Tensor, class_idx: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """Generate Grad-CAM heatmap"""
        self.model.eval()
        self.model.zero_grad()
        
        # Forward pass
        output = self.model(input_tensor)
        
        if class_idx is None:
            class_idx = torch.argmax(output).item()
        
        # Backward pass
        one_hot = torch.zeros_like(output)
        one_hot[0][class_idx] = 1
        output.backward(gradient=one_hot, retain_graph=True)
        
        # Get gradients and activations
        gradients = self.gradients.cpu().numpy()[0]
        activations = self.activations.cpu().numpy()[0]
        
        # Global average pooling
        weights = np.mean(gradients, axis=(1, 2))
        
        # Weighted combination
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # ReLU
        cam = np.maximum(cam, 0)
        
        # Normalize
        cam = (cam - np.min(cam)) / (np.max(cam) - np.min(cam) + 1e-8)
        
        return cam, class_idx
    
    def overlay_heatmap(self, image_path: str, cam: np.ndarray, alpha: float = 0.5) -> np.ndarray:
        """Overlay heatmap on original image"""
        # Load and resize image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        
        # Resize cam to image size
        cam = cv2.resize(cam, (224, 224))
        
        # Convert to heatmap
        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Overlay
        overlay = cv2.addWeighted(img.astype(np.uint8), 1 - alpha,
                                  heatmap.astype(np.uint8), alpha, 0)
        
        return overlay
    
    def save_heatmap(self, image_path: str, cam: np.ndarray, output_path: str):
        """Save heatmap to file"""
        overlay = self.overlay_heatmap(image_path, cam)
        overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
        cv2.imwrite(output_path, overlay_rgb)

class SHAPAnalyzer:
    """SHAP analysis for feature importance"""
    
    def __init__(self, model, background_data, feature_names=None):
        self.model = model
        self.background = background_data
        self.feature_names = feature_names
        self.explainer = None
        self._init_explainer()
    
    def _init_explainer(self):
        """Initialize SHAP explainer"""
        try:
            import shap
            self.explainer = shap.KernelExplainer(
                self._model_predict,
                self.background
            )
        except ImportError:
            raise ImportError("SHAP is not installed. Run: pip install shap")
    
    def _model_predict(self, data):
        """Wrapper for model prediction"""
        import torch
        self.model.eval()
        with torch.no_grad():
            tensor_data = torch.tensor(data, dtype=torch.float32)
            outputs = self.model(tensor_data)
            return torch.softmax(outputs, dim=1).numpy()
    
    def explain_instance(self, instance):
        """Explain a single instance"""
        shap_values = self.explainer.shap_values(instance.reshape(1, -1))
        return shap_values
    
    def get_feature_importance(self, shap_values):
        """Get feature importance ranking"""
        importance = np.abs(shap_values).mean(0)
        sorted_idx = np.argsort(importance)[::-1]
        
        feature_importance = {}
        for idx in sorted_idx[:10]:
            name = self.feature_names[idx] if self.feature_names else f"Feature_{idx}"
            feature_importance[name] = float(importance[idx])
        
        return feature_importance
    
    def plot_waterfall(self, shap_values, instance, output_path=None):
        """Generate waterfall plot"""
        import shap
        
        shap.initjs()
        plt.figure(figsize=(12, 8))
        
        shap.plots.waterfall(
            shap.Explanation(
                values=shap_values[0] if isinstance(shap_values, list) else shap_values,
                base_values=self.explainer.expected_value,
                data=instance,
                feature_names=self.feature_names
            ),
            show=False
        )
        
        if output_path:
            plt.savefig(output_path, bbox_inches='tight', dpi=100)
            plt.close()
        else:
            plt.show()

class LIMEExplainer:
    """LIME for local interpretability"""
    
    def __init__(self, model, class_names, device='cpu'):
        self.model = model
        self.class_names = class_names
        self.device = device
        self.explainer = None
        self._init_explainer()
    
    def _init_explainer(self):
        """Initialize LIME explainer"""
        try:
            import lime
            from lime.lime_image import LimeImageExplainer
            self.explainer = LimeImageExplainer()
        except ImportError:
            raise ImportError("LIME is not installed. Run: pip install lime")
    
    def _predict(self, images):
        """Predict function for LIME"""
        import torch
        from torchvision import transforms
        
        # Convert images to tensor
        tensor_images = torch.tensor(images).permute(0, 3, 1, 2) / 255.0
        tensor_images = tensor_images.to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(tensor_images)
            probabilities = torch.softmax(outputs, dim=1)
        
        return probabilities.cpu().numpy()
    
    def explain_image(self, image_path, num_features=10):
        """Explain image prediction"""
        # Load and preprocess image
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img)
        
        # Generate explanation
        explanation = self.explainer.explain_instance(
            img_array,
            self._predict,
            top_labels=3,
            hide_color=0,
            num_samples=1000
        )
        
        # Get explanation for top class
        prediction = self._predict([img_array])[0]
        top_class = np.argmax(prediction)
        top_class_name = self.class_names[top_class]
        
        mask = explanation.get_image_and_mask(
            top_class,
            positive_only=True,
            hide_rest=False,
            num_features=num_features
        )
        
        return {
            'top_class': top_class_name,
            'top_class_prob': float(prediction[top_class]),
            'mask': mask,
            'explanation': explanation
        }

class ExplainableCancerModel(torch.nn.Module):
    """Full Multimodal Explainable Cancer Diagnosis Model"""
    
    def __init__(self, image_dim: int = 1792, text_dim: int = 768, tabular_dim: int = 32):
        super().__init__()
        from src.models.cnn_model import VisionBackbone
        from src.models.fusion_model import GatedCrossAttentionFusionModel
        
        self.vision_backbone = VisionBackbone(architecture="resnet50", embedding_dim=image_dim, pretrained=False)
        self.tab_proj = torch.nn.Linear(16, tabular_dim)
        self.fusion_model = GatedCrossAttentionFusionModel(
            image_dim=image_dim, text_dim=text_dim, tabular_dim=tabular_dim, num_classes=4
        )
        
    def forward(self, img: torch.Tensor, txt: torch.Tensor, tab: torch.Tensor):
        img_feat = self.vision_backbone(img)
        if tab.shape[-1] == 16:
            tab_feat = self.tab_proj(tab)
        else:
            tab_feat = tab
        return self.fusion_model(img_feat, txt, tab_feat)

