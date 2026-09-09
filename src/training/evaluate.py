import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

def compute_evaluation_metrics(y_true, y_pred, labels=None):
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted')
    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=labels, output_dict=True)
    
    return {
        'accuracy': float(acc),
        'f1_score': float(f1),
        'confusion_matrix': cm.tolist(),
        'classification_report': report
    }
