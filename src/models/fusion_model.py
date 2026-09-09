import torch
import torch.nn as nn
import torch.nn.functional as F

class TabularMLP(nn.Module):
    def __init__(self, input_dim: int = 16, hidden_dims: list = [128, 64, 32], dropout: float = 0.3):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers.extend([
                nn.Linear(prev, h),
                nn.BatchNorm1d(h),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev = h
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

class GatedCrossAttentionFusionModel(nn.Module):
    """
    Multimodal Dynamic Late-Fusion Model integrating Vision (Imaging), NLP (BioBERT), and Tabular Vitals.
    """
    def __init__(
        self,
        image_dim: int = 1792,
        text_dim: int = 768,
        tabular_dim: int = 32,
        hidden_dims: list = [512, 256, 128],
        num_classes: int = 4,
        num_stages: int = 5,
        num_treatments: int = 5
    ):
        super().__init__()
        
        # Modality Gating Attention
        self.img_gate = nn.Sequential(nn.Linear(image_dim, 64), nn.ReLU(), nn.Linear(64, 1))
        self.txt_gate = nn.Sequential(nn.Linear(text_dim, 64), nn.ReLU(), nn.Linear(64, 1))
        self.tab_gate = nn.Sequential(nn.Linear(tabular_dim, 64), nn.ReLU(), nn.Linear(64, 1))

        total_dim = image_dim + text_dim + tabular_dim
        layers = []
        prev = total_dim
        for h in hidden_dims:
            layers.extend([
                nn.Linear(prev, h),
                nn.BatchNorm1d(h),
                nn.ReLU(),
                nn.Dropout(0.3)
            ])
            prev = h
        self.fusion_net = nn.Sequential(*layers)

        # Multi-task heads
        self.type_head = nn.Linear(hidden_dims[-1], num_classes)
        self.stage_head = nn.Linear(hidden_dims[-1], num_stages)
        self.treatment_head = nn.Linear(hidden_dims[-1], num_treatments)
        self.survival_head = nn.Linear(hidden_dims[-1], 1)

    def forward(self, img_feat: torch.Tensor, txt_feat: torch.Tensor, tab_feat: torch.Tensor):
        w_img = torch.sigmoid(self.img_gate(img_feat))
        w_txt = torch.sigmoid(self.txt_gate(txt_feat))
        w_tab = torch.sigmoid(self.tab_gate(tab_feat))

        fused = torch.cat([img_feat * w_img, txt_feat * w_txt, tab_feat * w_tab], dim=1)
        fused_embedding = self.fusion_net(fused)

        return {
            'cancer_type': self.type_head(fused_embedding),
            'cancer_stage': self.stage_head(fused_embedding),
            'treatment': torch.sigmoid(self.treatment_head(fused_embedding)),
            'survival': torch.sigmoid(self.survival_head(fused_embedding)),
            'attention_weights': {
                'image': w_img.mean().item(),
                'text': w_txt.mean().item(),
                'tabular': w_tab.mean().item()
            },
            'fused_embedding': fused_embedding
        }
