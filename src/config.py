import os
import yaml
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ModelConfig:
    """Configuration for model architecture"""
    model_name: str = 'resnet50'
    input_size: int = 224
    num_classes: int = 3
    pretrained: bool = True
    dropout_rate: float = 0.3

@dataclass
class TrainingConfig:
    """Configuration for training"""
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001
    optimizer: str = 'adam'
    scheduler: str = 'step'
    early_stopping_patience: int = 10
    validation_split: float = 0.2
    data_augmentation: bool = True

@dataclass
class XAIConfig:
    """Configuration for explainability"""
    grad_cam_layer: str = 'layer4.2'
    shap_samples: int = 100
    lime_samples: int = 1000
    attention_visualization: bool = True
    output_heatmaps: bool = True

class Config:
    """Master configuration class"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.model = ModelConfig()
        self.training = TrainingConfig()
        self.xai = XAIConfig()
        self.device = 'cuda' if self._check_cuda() else 'cpu'
        
        if config_path and os.path.exists(config_path):
            self._load_from_yaml(config_path)
    
    def _check_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def _load_from_yaml(self, path: str):
        """Load configuration from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
            for key, value in data.items():
                if hasattr(self, key):
                    for sub_key, sub_value in value.items():
                        if hasattr(getattr(self, key), sub_key):
                            setattr(getattr(self, key), sub_key, sub_value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'model': self.model.__dict__,
            'training': self.training.__dict__,
            'xai': self.xai.__dict__,
            'device': self.device
        }
