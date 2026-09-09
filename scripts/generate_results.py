import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import os

def generate_performance_report(metrics_path: str, output_dir: str = 'outputs/results'):
    """Generate performance report from metrics"""
    
    if not os.path.exists(metrics_path):
        print(f"Metrics file not found at {metrics_path}. Generating dummy report framework.")
        os.makedirs(output_dir, exist_ok=True)
        return
        
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    # Normalize class keys from metrics
    class_map = {
        'breast_cancer': 'Breast Cancer',
        'lung_cancer': 'Lung Cancer',
        'colon_cancer': 'Colon Cancer',
        'Breast Cancer': 'Breast Cancer',
        'Lung Cancer': 'Lung Cancer',
        'Colon Cancer': 'Colon Cancer'
    }
    
    report_data = {
        'Metric': ['Precision', 'Recall', 'F1-Score'],
        'Breast Cancer': [0.0, 0.0, 0.0],
        'Lung Cancer': [0.0, 0.0, 0.0],
        'Colon Cancer': [0.0, 0.0, 0.0],
        'Average': [0.0, 0.0, 0.0]
    }
    
    clf_report = metrics.get('classification_report', {})
    for key, val in clf_report.items():
        if key in class_map and isinstance(val, dict):
            disp_name = class_map[key]
            report_data[disp_name] = [
                val.get('precision', 0.0),
                val.get('recall', 0.0),
                val.get('f1-score', 0.0)
            ]
            
    if 'macro avg' in clf_report and isinstance(clf_report['macro avg'], dict):
        report_data['Average'] = [
            clf_report['macro avg'].get('precision', 0.0),
            clf_report['macro avg'].get('recall', 0.0),
            clf_report['macro avg'].get('f1-score', 0.0)
        ]
    else:
        # Compute mean
        for i in range(3):
            report_data['Average'][i] = np.mean([report_data[c][i] for c in ['Breast Cancer', 'Lung Cancer', 'Colon Cancer']])
            
    df_report = pd.DataFrame(report_data)
    
    # Save to CSV
    os.makedirs(output_dir, exist_ok=True)
    df_report.to_csv(os.path.join(output_dir, 'performance_report.csv'), index=False)
    
    # Generate comparison bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(df_report['Metric']))
    width = 0.25
    
    ax.bar(x - width, df_report['Breast Cancer'], width, label='Breast Cancer', color='#22c55e')
    ax.bar(x, df_report['Lung Cancer'], width, label='Lung Cancer', color='#667eea')
    ax.bar(x + width, df_report['Colon Cancer'], width, label='Colon Cancer', color='#f59e0b')
    
    ax.set_xlabel('Metrics', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Performance Comparison Across Cancer Types', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df_report['Metric'], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'performance_comparison.png'), dpi=150)
    plt.close()
    
    print(f"Performance report saved to {output_dir}")

def generate_confusion_matrix(cm_path: str, class_names: list, output_dir: str = 'outputs/visualizations'):
    """Generate enhanced confusion matrix"""
    if not os.path.exists(cm_path):
        print(f"Confusion matrix file not found at {cm_path}")
        return
        
    with open(cm_path, 'r') as f:
        cm_data = json.load(f)
    
    cm = np.array(cm_data)
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names,
                ax=ax, annot_kws={'size': 12})
    
    ax.set_title('Confusion Matrix', fontsize=16, fontweight='bold')
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('Actual', fontsize=12)
    
    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'confusion_matrix_enhanced.png'), dpi=150)
    plt.close()
    
    print(f"Enhanced confusion matrix saved to {output_dir}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--metrics_path', type=str, default='outputs/results/metrics.json')
    parser.add_argument('--output_dir', type=str, default='outputs/results')
    
    args = parser.parse_args()
    
    generate_performance_report(args.metrics_path, args.output_dir)
