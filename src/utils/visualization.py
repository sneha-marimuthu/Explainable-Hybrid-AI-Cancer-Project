import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def plot_confusion_matrix(cm, labels):
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True Label')
    ax.set_title('Confusion Matrix')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()
