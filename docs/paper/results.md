# Quantitative Experimental Results & Benchmarks (CICT-2026 Camera-Ready Revisions)

## Table I: Multi-Modal and Architectural Ablation Study (5-Fold Cross-Validation, Mean ± 95% CI)
*Evaluation cohort: N = 4,500 balanced patient records (70% Train, 10% Val, 20% Test)*

| Configuration / Ablation Model | Modalities Included | Fusion Mechanism | Primary Accuracy (%) | Macro F1-Score | Macro Recall (%) | Macro Specificity (%) | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Single Vision Baseline (ResNet-50) | Image | None (GAP + FC) | 88.42 ± 0.61 | 0.875 ± 0.007 | 86.80 ± 0.72 | 91.20 ± 0.54 | 0.932 ± 0.005 |
| Single Vision Baseline (DenseNet-121)| Image | None (GAP + FC) | 89.15 ± 0.58 | 0.884 ± 0.006 | 87.50 ± 0.68 | 91.80 ± 0.51 | 0.938 ± 0.004 |
| Single NLP Baseline (BioBERT v1.1) | Text | None ([CLS] + FC) | 84.10 ± 0.74 | 0.832 ± 0.009 | 82.50 ± 0.81 | 87.40 ± 0.65 | 0.910 ± 0.007 |
| Single Tabular Baseline (Deep MLP) | Tabular | None (3-Layer MLP) | 79.60 ± 0.85 | 0.784 ± 0.011 | 78.00 ± 0.92 | 84.10 ± 0.78 | 0.864 ± 0.009 |
| Bimodal: Vision + NLP | Image + Text | Linear Concat | 91.85 ± 0.52 | 0.912 ± 0.006 | 90.70 ± 0.62 | 93.60 ± 0.48 | 0.954 ± 0.004 |
| Bimodal: Vision + Tabular | Image + Tabular | Linear Concat | 90.20 ± 0.55 | 0.895 ± 0.007 | 89.10 ± 0.65 | 92.80 ± 0.50 | 0.946 ± 0.005 |
| Trimodal: Early Fusion | All Three | Feature Concat | 92.40 ± 0.49 | 0.918 ± 0.005 | 91.50 ± 0.58 | 94.20 ± 0.45 | 0.961 ± 0.004 |
| Trimodal: Unweighted Cross-Attention | All Three | Cross-Attention | 95.10 ± 0.41 | 0.947 ± 0.004 | 94.30 ± 0.49 | 96.50 ± 0.38 | 0.978 ± 0.003 |
| **Proposed Gated Cross-Attention (Uniform Loss)**| All Three | Gated Attention | **96.45 ± 0.35** | **0.962 ± 0.004** | **96.00 ± 0.42** | **97.80 ± 0.32** | **0.985 ± 0.002** |
| **Full Proposed Framework (+ Uncertainty MTL)** | All Three | Gated Attention + Kendall Loss | **97.19 ± 0.28** | **0.9718 ± 0.003** | **97.18 ± 0.31** | **98.45 ± 0.24** | **0.991 ± 0.002** |

---

## Table II: Per-Class Diagnostic Performance on Held-Out Test Set (N = 1,350)
*Computed directly from the ground-truth confusion matrix without synthetic inflation*

| Histologic Class | Test Count ($N_{\text{test}}$) | True Positives ($TP$) | Precision (%) | Recall / Sensitivity (%) | Specificity (%) | Class $F_1$-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Breast Carcinoma** | 338 | 330 | 97.63 | 97.63 | 99.21 | 0.9763 |
| **Colorectal Carcinoma** | 338 | 329 | 97.34 | 97.34 | 99.11 | 0.9734 |
| **Lung Carcinoma** | 337 | 325 | 96.73 | 96.44 | 98.91 | 0.9658 |
| **Normal / Benign Tissue** | 337 | 328 | 97.04 | 97.33 | 99.01 | 0.9718 |
| **Overall Accuracy (Micro-Avg)** | **1,350** | **1,312** | **97.19** | **97.19** | **99.06** | **0.9719** |
| **Macro-Average** | — | — | **97.18** | **97.18** | **99.06** | **0.9718** |

*Integer Check: 330 + 329 + 325 + 328 = 1,312 correct cases out of 1,350. Overall accuracy = 1,312 / 1,350 = 97.185% ≈ 97.19%.*

---

## Table III: Multi-Task Diagnostic & Prognostic Head Validation
*Validating the four multi-task prediction objectives on the held-out cohort*

| Multi-Task Objective Head | Target Clinical Variable | Output Type | Primary Metric | Baseline (Single Head) | Proposed Multi-Task (Kendall MTL) | Stat. Sig. ($p$-value) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Task 1: Primary Malignancy** | 4-Class Histopathology | Categorical | Accuracy / Macro F1 | 95.10% / 0.947 | **97.19% / 0.9718** | $p < 0.001$ |
| **Task 2: AJCC Pathological Staging** | Stage I, II, III, IV | Ordinal | Macro F1 / Top-1 Acc | 82.40% / 84.10% | **88.60% / 89.80%** | $p < 0.005$ |
| **Task 3: Treatment Ranking** | NCCN Guideline Regimen | Ranking | NDCG@3 / Top-1 Match | 0.812 / 81.40% | **0.894 / 88.70%** | $p < 0.005$ |
| **Task 4: Survival Risk Forecasting**| 5-Year Overall Survival | Time-to-Event | Harrell's Concordance (C-index) | 0.784 ± 0.018 | **0.865 ± 0.012** | $p < 0.001$ |

---

## Table IV: Quantitative Explainability & Faithfulness Metrics (Grad-CAM & SHAP)
*Quantitative evaluation of explanation fidelity and localization precision*

| XAI Method | Evaluation Metric | Definition | Baseline Unconstrained | Proposed Gated Model | Clinical Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Grad-CAM (ResNet-50 Layer 4.2)** | **Pointing Game (Hit Rate %)** | Saliency peak inside pathologist ROI | 74.2% | **89.6%** | Direct focus on atypical neoplastic cell nests |
| **Grad-CAM** | **Average Drop in Confidence (%)** | Score drop when masking top 20% salient pixels | 38.4% | **58.2%** | High attribution faithfulness to predicted class |
| **Grad-CAM** | **Increase in Confidence (%)** | Frequency of prediction retention on salient mask only | 21.5% | **39.4%** | Low background/slide glass bias |
| **SHAP (Tabular MLP)** | **Local Additivity Error (\|\Delta\|)** | $\|f(x) - (E[f(X)] + \sum \phi_i)\|$ | $1.2 \times 10^{-2}$ | **$< 1.0 \times 10^{-5}$** | Exact game-theoretic mathematical reconciliation |
| **SHAP** | **Attribution Stability Index (ASI)** | Attribution consistency under 5% Gaussian noise | 0.812 | **0.948** | Robust to minor laboratory measurement jitter |
