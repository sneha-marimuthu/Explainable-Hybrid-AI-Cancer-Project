# Multimodal Explainable Hybrid AI System Architecture & Methodology (CICT-2026 Camera-Ready)

## 1. Vision Feature Extraction
Whole-slide imaging (WSI) tiles ($224 \times 224$ pixels, $20\times$ optical magnification, $0.50\,\mu\text{m/px}$) are processed using a **ResNet-50** backbone pre-trained on ImageNet and fine-tuned on TCGA slide patches. Spatial feature activations are extracted from convolutional block `layer4.2`, yielding a visual embedding vector $\mathbf{f}_{\text{img}} \in \mathbb{R}^{2048}$ after adaptive average pooling.

## 2. BioBERT Clinical Text Representation
Unstructured diagnostic pathology narratives and macroscopic examination reports are tokenized and encoded using **BioBERT (v1.1)** pre-trained on PubMed biomedical literature. The hidden state of the classification token `[CLS]` across 12 transformer layers produces a contextual text embedding $\mathbf{f}_{\text{txt}} \in \mathbb{R}^{768}$.

## 3. Deep Tabular Representation Network
Laboratory biomarkers (CA-125, CEA, Ki-67 index), receptor immunohistochemistry (HER2, ER, PR status), patient vitals (systolic/diastolic BP, heart rate), and demographics (16 standardized clinical parameters) are passed through a 3-layer Multilayer Perceptron with Batch Normalization, ReLU activations, and a Dropout rate of $0.3$, producing a tabular feature vector $\mathbf{f}_{\text{tab}} \in \mathbb{R}^{128}$.

## 4. Gated Cross-Attention Fusion Mechanism
To dynamically suppress modality-specific noise (e.g., slide staining variability or incomplete clinical notes), each modality is projected into a shared latent space $\mathbb{R}^{d}$ ($d=256$) via linear projections $W_v, W_t, W_s$. A sigmoid gating network computes scalar modality reliability coefficients:
$$g_{\text{img}} = \sigma(W_{g,v} \mathbf{f}_{\text{img}} + b_{g,v}), \quad g_{\text{txt}} = \sigma(W_{g,t} \mathbf{f}_{\text{txt}} + b_{g,t}), \quad g_{\text{tab}} = \sigma(W_{g,s} \mathbf{f}_{\text{tab}} + b_{g,s})$$
Cross-attention weights are computed using query-key-value projections across modalities:
$$\mathbf{z}_{\text{fused}} = \text{Softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V \odot [g_{\text{img}} \parallel g_{\text{txt}} \parallel g_{\text{tab}}]$$

## 5. Homoscedastic Uncertainty-Weighted Multi-Task Objective
Rather than optimizing a heuristic unweighted loss sum, the multi-task heads are trained simultaneously using Kendall & Gal's homoscedastic task uncertainty formulation:
$$\mathcal{L}_{\text{total}} = \frac{1}{2\sigma_1^2} \mathcal{L}_{\text{diag}} + \frac{1}{2\sigma_2^2} \mathcal{L}_{\text{stage}} + \frac{1}{2\sigma_3^2} \mathcal{L}_{\text{therapy}} + \frac{1}{2\sigma_4^2} \mathcal{L}_{\text{surv}} + \sum_{k=1}^4 \log(1 + \sigma_k^2)$$
where $\sigma_k$ are learnable observation noise parameters that balance gradient descent across:
1. **$\mathcal{L}_{\text{diag}}$**: 4-Class categorical cross-entropy for primary tumor classification.
2. **$\mathcal{L}_{\text{stage}}$**: Ordinal cross-entropy for AJCC TNM clinical staging (I, II, III, IV).
3. **$\mathcal{L}_{\text{therapy}}$**: ListNet ranking loss matching first-line NCCN clinical regimens.
4. **$\mathcal{L}_{\text{surv}}$**: Negative partial log-likelihood of the Cox proportional hazards model for 5-year survival risk.

## 6. Patient-Level Cohort Splitting & Leakage Safeguards
To guarantee patient-independent validation:
1. All tile augmentations, clinical notes, and laboratory vectors are bound by unique **Patient Subject IDs**.
2. Partitioning is performed using **`GroupShuffleSplit`** (70% Train, 10% Validation, 20% Held-Out Test).
3. Early stopping (patience $= 12$ epochs) is governed exclusively by validation loss. The test cohort ($N=1,350$) is sequestered until final unblinded evaluation.
