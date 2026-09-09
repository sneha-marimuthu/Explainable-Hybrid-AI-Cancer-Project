import matplotlib.pyplot as plt
import numpy as np
import cv2
from PIL import Image
import seaborn as sns
from typing import Dict, List, Optional

def visualize_predictions(image_path: str, result: Dict, 
                         grad_cam_image: Optional[np.ndarray] = None,
                         save_path: Optional[str] = None):
    """Create comprehensive visualization for paper"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Original image
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    axes[0, 0].imshow(img)
    axes[0, 0].set_title('Input Image', fontsize=12, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Grad-CAM if available
    if grad_cam_image is not None:
        axes[0, 1].imshow(grad_cam_image)
        axes[0, 1].set_title('Grad-CAM Heatmap', fontsize=12, fontweight='bold')
        axes[0, 1].axis('off')
    else:
        axes[0, 1].axis('off')
    
    # Probability bar chart
    classes = list(result['class_probabilities'].keys())
    probs = list(result['class_probabilities'].values())
    colors = ['#22c55e' if i == result['predicted_class'] else '#e8ecf1' 
              for i in range(len(classes))]
    
    bars = axes[1, 0].bar(classes, probs, color=colors, edgecolor='black', linewidth=0.5)
    axes[1, 0].set_title('Class Probabilities', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('Probability', fontsize=10)
    axes[1, 0].set_xlabel('Cancer Type', fontsize=10)
    axes[1, 0].set_ylim([0, 1.1])
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, prob in zip(bars, probs):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                       f'{prob*100:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Treatment recommendations
    treatment = result['treatment']
    axes[1, 1].axis('off')
    
    text_content = (
        f"Cancer: {result['cancer_type']}\n"
        f"Confidence: {result['confidence']*100:.1f}%\n"
        f"Stage: {treatment.get('stage', 'N/A').capitalize()}\n\n"
        f"Recommended Treatments:\n"
    )
    
    for t in treatment.get('recommended_treatments', ['Consult Specialist']):
        text_content += f"• {t}\n"
    
    axes[1, 1].text(0.05, 0.95, text_content, fontsize=11,
                    verticalalignment='top', linespacing=1.5,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='#f8fafc', alpha=0.8))
    axes[1, 1].set_title('Diagnosis & Recommendations', fontsize=12, fontweight='bold')
    
    # Confidence meter
    axes[1, 2].axis('off')
    confidence = result['confidence']
    
    # Create circular confidence gauge
    fig_gauge, ax_gauge = plt.subplots(figsize=(3, 3))
    ax_gauge.pie([confidence, 1-confidence], 
                colors=['#22c55e', '#e8ecf1'],
                startangle=90, counterclock=False)
    ax_gauge.text(0, 0, f"{confidence*100:.1f}%", 
                 ha='center', va='center', fontsize=16, fontweight='bold')
    ax_gauge.set_title('Confidence', fontsize=10)
    
    # Save gauge to display
    import io
    from PIL import Image as PILImage
    buf = io.BytesIO()
    fig_gauge.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    gauge_img = PILImage.open(buf)
    axes[1, 2].imshow(gauge_img)
    axes[1, 2].axis('off')
    plt.close(fig_gauge)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
    
    return fig

def create_attention_visualization(attention_weights: Dict, 
                                  modalities: List[str],
                                  save_path: Optional[str] = None):
    """Create attention weight visualization"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Pie chart
    colors = ['#667eea', '#22c55e', '#f59e0b']
    wedges, texts, autotexts = axes[0].pie(
        list(attention_weights.values()),
        labels=modalities,
        autopct='%1.1f%%',
        colors=colors[:len(modalities)],
        startangle=90,
        explode=[0.05] * len(modalities)
    )
    axes[0].set_title('Modality Attention Weights', fontsize=14, fontweight='bold')
    plt.setp(autotexts, size=11, weight='bold', color='white')
    
    # Bar chart
    bars = axes[1].bar(modalities, list(attention_weights.values()), 
                       color=colors[:len(modalities)])
    axes[1].set_title('Attention Distribution', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Attention Weight', fontsize=11)
    axes[1].set_ylim([0, max(attention_weights.values()) * 1.2])
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, attention_weights.values()):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value*100:.1f}%', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
    
    return fig

def plot_feature_importance(feature_importance: Dict[str, float],
                           title: str = 'Feature Importance',
                           save_path: Optional[str] = None):
    """Plot feature importance"""
    # Sort by importance
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    features = [f[0] for f in sorted_features]
    values = [f[1] for f in sorted_features]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create horizontal bar chart
    colors = plt.cm.viridis(np.linspace(0.3, 0.8, len(features)))[::-1]
    bars = ax.barh(features, values, color=colors)
    
    # Add value labels
    for bar, value in zip(bars, values):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f'{value:.3f}', va='center', fontsize=9)
    
    ax.set_xlabel('Importance Score', fontsize=11)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
    
    return fig
