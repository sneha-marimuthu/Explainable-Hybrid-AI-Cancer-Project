"""
Full EHASMCDTR Multi-Task Network
Project: EHASMCDTR Multimodal Cancer Diagnosis
Integrates Vision (ResNet-50), NLP (BioBERT), and Tabular MLP via Gated Cross-Attention
to predict:
1. Primary Tumor Classification (4 Classes)
2. AJCC TNM Pathological Staging (Stages I-IV)
3. NCCN Treatment Regimen Ranking (Top Regimens)
4. 5-Year Overall Survival Risk (Cox Proportional Hazard)
"""

import torch
import torch.nn as nn
from .vision_encoder import ResNet50VisionEncoder
from .language_encoder import BioBERTLanguageEncoder
from .tabular_encoder import TabularBiomarkerEncoder
from .gated_fusion import TriModalGatedFusion

class EHASMCDTRNetwork(nn.Module):
    def __init__(self, num_classes=4, num_stages=4, num_treatments=5, embed_dim=256, dropout_rate=0.3):
        super(EHASMCDTRNetwork, self).__init__()
        
        # 1. Modality Encoders
        self.vision_encoder = ResNet50VisionEncoder(output_dim=embed_dim, dropout_rate=dropout_rate)
        self.language_encoder = BioBERTLanguageEncoder(output_dim=embed_dim, dropout_rate=dropout_rate)
        self.tabular_encoder = TabularBiomarkerEncoder(input_dim=16, output_dim=embed_dim, dropout_rate=dropout_rate)

        # 2. Gated Cross-Attention Fusion
        self.fusion = TriModalGatedFusion(embed_dim=embed_dim)
        fused_dim = embed_dim * 3  # 768

        # 3. Multi-Task Output Heads
        # Head 1: Primary Malignancy Classification (4 Classes)
        self.head_diagnosis = nn.Sequential(
            nn.Linear(fused_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, num_classes)
        )

        # Head 2: AJCC TNM Pathological Staging (Ordinal Stages I, II, III, IV)
        self.head_stage = nn.Sequential(
            nn.Linear(fused_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_stages)
        )

        # Head 3: NCCN Guideline Treatment Ranking
        self.head_treatment = nn.Sequential(
            nn.Linear(fused_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_treatments)
        )

        # Head 4: 5-Year Survival Risk Forecasting (Cox Log-Hazard)
        self.head_survival = nn.Sequential(
            nn.Linear(fused_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, 1)  # Outputs scalar log-hazard ratio h(x)
        )

    def forward(self, images, input_ids, attention_mask, tabular_vitals):
        # Unimodal Encoding
        v_img, spatial_cam_feats = self.vision_encoder(images)
        v_txt, text_hidden = self.language_encoder(input_ids, attention_mask=attention_mask)
        v_tab = self.tabular_encoder(tabular_vitals)

        # Gated Cross-Attention Fusion
        z_fused, gates = self.fusion(v_img, v_txt, v_tab)

        # Multi-Task Head Predictions
        logits_diag = self.head_diagnosis(z_fused)
        logits_stage = self.head_stage(z_fused)
        logits_tx = self.head_treatment(z_fused)
        log_hazard_surv = self.head_survival(z_fused)

        outputs = {
            "logits_diagnosis": logits_diag,
            "logits_stage": logits_stage,
            "logits_treatment": logits_tx,
            "log_hazard_survival": log_hazard_surv,
            "fused_embedding": z_fused,
            "spatial_cam_features": spatial_cam_feats,
            "fusion_gates": gates
        }
        return outputs
