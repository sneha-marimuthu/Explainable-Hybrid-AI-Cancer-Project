"""
Gated Cross-Attention Fusion Network
Project: EHASMCDTR Multimodal Cancer Diagnosis
Learns adaptive sigmoidal gating coefficients to filter discordant or noisy modalities.
"""

import math
import torch
import torch.nn as nn

class GatedCrossAttentionBlock(nn.Module):
    def __init__(self, embed_dim=256, num_heads=4, dropout=0.1):
        super(GatedCrossAttentionBlock, self).__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim, "embed_dim must be divisible by num_heads"

        # Multi-Head Projections
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

        # Learned Gating Mechanism: g = sigma(W_g [X || Y] + b_g)
        self.gate_net = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.Sigmoid()
        )

        # Feedforward Network & Normalization
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim * 2, embed_dim),
            nn.Dropout(dropout)
        )

    def forward(self, query_modality, context_modality):
        # Shape: (B, embed_dim)
        B, D = query_modality.shape

        # Reshape to (B, 1, D) for sequence attention
        q_in = query_modality.unsqueeze(1)
        k_in = context_modality.unsqueeze(1)

        Q = self.q_proj(q_in).view(B, 1, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_proj(k_in).view(B, 1, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_proj(k_in).view(B, 1, self.num_heads, self.head_dim).transpose(1, 2)

        # Scaled Dot-Product Attention: Softmax(QK^T / sqrt(d_k)) V
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn_weights = torch.softmax(scores, dim=-1)
        attended = torch.matmul(attn_weights, V)  # (B, num_heads, 1, head_dim)
        attended = attended.transpose(1, 2).contiguous().view(B, D)
        attended = self.out_proj(attended)

        # Learned Sigmoidal Gate
        concat_pair = torch.cat([query_modality, context_modality], dim=-1)
        gate = self.gate_net(concat_pair)  # (B, embed_dim) in (0, 1)

        # Gated Integration
        gated_attended = query_modality + gate * attended
        norm_attended = self.norm1(gated_attended)

        # FFN with residual connection
        out = self.norm2(norm_attended + self.ffn(norm_attended))
        return out, gate


class TriModalGatedFusion(nn.Module):
    def __init__(self, embed_dim=256):
        super(TriModalGatedFusion, self).__init__()
        # Cross-modality attention pairs
        self.img_to_txt = GatedCrossAttentionBlock(embed_dim)
        self.img_to_tab = GatedCrossAttentionBlock(embed_dim)
        self.txt_to_img = GatedCrossAttentionBlock(embed_dim)
        self.tab_to_img = GatedCrossAttentionBlock(embed_dim)

        # Master Fused Latent Projection (3 * 256 = 768)
        self.fusion_projection = nn.Sequential(
            nn.Linear(embed_dim * 3, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, embed_dim * 3),
            nn.LayerNorm(embed_dim * 3)
        )

    def forward(self, v_img, v_txt, v_tab):
        # Cross-Modal Interaction
        fused_img, g_it = self.img_to_txt(v_img, v_txt)
        fused_txt, g_ti = self.txt_to_img(v_txt, v_img)
        fused_tab, g_si = self.tab_to_img(v_tab, v_img)

        # Concatenate gated aligned representations
        concat_fused = torch.cat([fused_img, fused_txt, fused_tab], dim=-1) # (B, 768)
        z_fused = self.fusion_projection(concat_fused)
        
        gates = {"gate_img_txt": g_it, "gate_txt_img": g_ti, "gate_tab_img": g_si}
        return z_fused, gates
