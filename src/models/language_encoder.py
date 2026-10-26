"""
Language Encoder Module (BioBERT v1.1)
Project: EHASMCDTR Multimodal Cancer Diagnosis
Encodes unstructured clinical pathology reports and diagnostic narratives.
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

class BioBERTLanguageEncoder(nn.Module):
    def __init__(self, model_name="dmis-lab/biobert-v1.1", output_dim=256, dropout_rate=0.3):
        super(BioBERTLanguageEncoder, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Projection from BERT 768-dim [CLS] token to unified latent space
        self.projection = nn.Sequential(
            nn.Linear(768, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, output_dim),
            nn.LayerNorm(output_dim)
        )

    def forward(self, input_ids, attention_mask=None, token_type_ids=None):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )
        # Extract [CLS] token representation across final layer (index 0)
        cls_rep = outputs.last_hidden_state[:, 0, :]  # (B, 768)
        embedding = self.projection(cls_rep)          # (B, output_dim)
        return embedding, outputs.last_hidden_state
