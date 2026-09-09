import copy
import torch
import torch.nn as nn
import torchvision.models as models
import timm
import warnings
warnings.filterwarnings('ignore')

class CancerClassificationModel(nn.Module):
    """Base CNN model for cancer classification with ResNet50/EfficientNet"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._build_model()
    
    def _build_model(self):
        """Build the model architecture"""
        if self.config.model_name == 'resnet50':
            self.backbone = models.resnet50(pretrained=self.config.pretrained)
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
            
        elif self.config.model_name == 'resnet101':
            self.backbone = models.resnet101(pretrained=self.config.pretrained)
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
            
        elif self.config.model_name == 'efficientnet_b3':
            self.backbone = timm.create_model('efficientnet_b3', 
                                               pretrained=self.config.pretrained)
            num_features = self.backbone.classifier.in_features
            self.backbone.classifier = nn.Identity()
            
        elif self.config.model_name == 'efficientnet_b4':
            self.backbone = timm.create_model('efficientnet_b4', 
                                               pretrained=self.config.pretrained)
            num_features = self.backbone.classifier.in_features
            self.backbone.classifier = nn.Identity()
            
        else:
            raise ValueError(f"Unsupported model: {self.config.model_name}")
        
        # Custom classifier
        self.classifier = nn.Sequential(
            nn.Dropout(self.config.dropout_rate),
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(self.config.dropout_rate),
            nn.Linear(512, self.config.num_classes)
        )
    
    def forward(self, x):
        """Forward pass"""
        features = self.backbone(x)
        return self.classifier(features)
    
    def get_features(self, x):
        """Extract features before classifier (for explainability)"""
        return self.backbone(x)

class HybridEnsembleModel(nn.Module):
    """Ensemble of multiple CNN models with learnable weights"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Create multiple models
        self.models = nn.ModuleList([
            self._create_model('resnet50'),
            self._create_model('resnet101'),
            self._create_model('efficientnet_b3')
        ])
        
        # Learnable ensemble weights
        self.weights = nn.Parameter(torch.ones(len(self.models)) / len(self.models))
        self.dropout = nn.Dropout(0.3)
    
    def _create_model(self, model_name):
        """Create a single model with given name"""
        config_copy = copy.deepcopy(self.config)
        config_copy.model_name = model_name
        return CancerClassificationModel(config_copy)
    
    def forward(self, x):
        """Forward pass with weighted ensemble"""
        outputs = []
        
        for model in self.models:
            outputs.append(model(x))
        
        # Weighted ensemble
        weights = torch.softmax(self.weights, dim=0)
        ensemble_output = torch.zeros_like(outputs[0])
        
        for i, output in enumerate(outputs):
            ensemble_output += weights[i] * output
        
        return ensemble_output
    
    def freeze_backbones(self):
        """Freeze backbone layers for fine-tuning"""
        for model in self.models:
            for param in model.backbone.parameters():
                param.requires_grad = False

class VisionBackbone(nn.Module):
    """Vision Backbone for feature extraction in multimodal hybrid model"""
    
    def __init__(self, architecture: str = 'resnet50', embedding_dim: int = 1792, pretrained: bool = False):
        super().__init__()
        self.architecture = architecture
        self.embedding_dim = embedding_dim
        
        if architecture == 'resnet50':
            backbone = models.resnet50(pretrained=pretrained)
            in_features = backbone.fc.in_features
            backbone.fc = nn.Identity()
            self.backbone = backbone
        elif architecture == 'efficientnet_b3':
            backbone = timm.create_model('efficientnet_b3', pretrained=pretrained)
            in_features = backbone.classifier.in_features
            backbone.classifier = nn.Identity()
            self.backbone = backbone
        else:
            backbone = models.resnet50(pretrained=pretrained)
            in_features = backbone.fc.in_features
            backbone.fc = nn.Identity()
            self.backbone = backbone
            
        self.proj = nn.Linear(in_features, embedding_dim) if in_features != embedding_dim else nn.Identity()
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.backbone(x)
        return self.proj(feat)

