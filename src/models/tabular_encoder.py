"""
Tabular Biomarker & Vitals Encoder (Deep MLP)
Project: EHASMCDTR Multimodal Cancer Diagnosis
Processes 16 standardized serological, receptor, and physiological parameters.
"""

import torch
import torch.nn as nn

class TabularBiomarkerEncoder(nn.Module):
    def __init__(self, input_dim=16, output_dim=256, dropout_rate=0.3):
        super(TabularBiomarkerEncoder, self).__init__()
        # 16 Input Features:
        # CA-125, CEA, Age, Systolic BP, Diastolic BP, Heart Rate,
        # Tumor Size (cm), Ki-67 (%), Hemoglobin, WBC, Platelets,
        # Glucose, HER2 Status, ER Status, PR Status, ECOG Score
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(128, output_dim),
            nn.LayerNorm(output_dim)
        )

    def forward(self, x):
        # x shape: (B, 16)
        return self.net(x)
