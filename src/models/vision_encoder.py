"""
Vision Encoder Module (ResNet-50)
Project: EHASMCDTR Multimodal Cancer Diagnosis
Extracts spatial visual representations from 20x Whole-Slide Histopathology Tiles.
"""

import torch
import torch.nn as nn
from torchvision import models

class ResNet50VisionEncoder(nn.Module):
    def __init__(self, output_dim=256, pretrained=True, dropout_rate=0.3):
        super(ResNet50VisionEncoder, self).__init__()
        # Load ResNet-50 backbone
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        resnet = models.resnet50(weights=weights)
        
        # Base convolutional layers up to layer4 (Bottleneck block 2)
        self.conv1 = resnet.conv1
        self.bn1 = resnet.bn1
        self.relu = resnet.relu
        self.maxpool = resnet.maxpool
        self.layer1 = resnet.layer1
        self.layer2 = resnet.layer2
        self.layer3 = resnet.layer3
        self.layer4 = resnet.layer4  # Layer 4.2 target layer for Grad-CAM
        
        # Adaptive pooling & linear projection
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.projection = nn.Sequential(
            nn.Linear(2048, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, output_dim),
            nn.LayerNorm(output_dim)
        )

    def forward(self, x):
        # x shape: (B, 3, 224, 224)
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        spatial_features = self.layer4(x)  # (B, 2048, 7, 7) - Grad-CAM hook point

        pooled = self.avgpool(spatial_features)  # (B, 2048, 1, 1)
        pooled = torch.flatten(pooled, 1)        # (B, 2048)
        embedding = self.projection(pooled)      # (B, output_dim)
        
        return embedding, spatial_features
