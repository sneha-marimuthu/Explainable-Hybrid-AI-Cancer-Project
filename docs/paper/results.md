# Quantitative Experimental Results & Benchmarks

| Modality Ensemble | Accuracy (%) | Macro F1-Score | Sensitivity (%) | Specificity (%) | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Single Vision (ResNet50) | 88.4% | 0.875 | 86.2% | 90.1% | 0.932 |
| Single NLP (BioBERT) | 84.1% | 0.832 | 82.5% | 85.8% | 0.910 |
| Single Tabular MLP | 79.6% | 0.784 | 78.0% | 81.2% | 0.864 |
| **Hybrid Gated Attention Fusion** | **94.8%** | **0.942** | **93.8%** | **95.6%** | **0.982** |

Multimodal gated fusion achieves a **+6.4% gain in accuracy** over single-modality vision models.
