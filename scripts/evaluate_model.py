import os
import torch
import json
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

import sys
sys.path.insert(0, os.path.abspath("."))

from src.config import Config
from src.models.cnn_model import CancerClassificationModel

def evaluate_accuracy(data_dir="data/processed/test", model_path="models/trained/best_model.pth"):
    """
    Manually evaluate the accuracy of the trained model on test or validation dataset.
    """
    print("=" * 65)
    print("MANUAL MODEL ACCURACY EVALUATION")
    print("=" * 65)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Compute Device: {device}")
    
    if not os.path.exists(model_path):
        print(f"[!] Error: Model checkpoint not found at {model_path}")
        return

    if not os.path.exists(data_dir):
        print(f"[!] Error: Data directory not found at {data_dir}")
        return

    # Image preprocessing transform (matches training validation pipeline)
    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Load dataset
    dataset = datasets.ImageFolder(data_dir, transform=eval_transform)
    loader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=0)
    class_names = dataset.classes

    print(f"[*] Evaluation Data Path: {data_dir}")
    print(f"[*] Total Evaluation Samples: {len(dataset)}")
    print(f"[*] Classes ({len(class_names)}): {class_names}\n")

    # Load Model
    config = Config()
    model = CancerClassificationModel(config.model)
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()

    all_preds = []
    all_labels = []
    correct_count = 0
    total_count = 0

    print("[*] Running inference across batches...")
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            
            correct_count += (preds == labels).sum().item()
            total_count += labels.size(0)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = (correct_count / total_count) * 100.0
    cm = confusion_matrix(all_labels, all_preds)
    report_text = classification_report(all_labels, all_preds, target_names=class_names)
    report_dict = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True)

    print("\n" + "=" * 65)
    print("EVALUATION RESULTS")
    print("=" * 65)
    print(f" -> Total Images Evaluated : {total_count}")
    print(f" -> Correct Predictions    : {correct_count}")
    print(f" -> Incorrect Predictions  : {total_count - correct_count}")
    print(f" -> EXACT ACCURACY         : {accuracy:.2f}%")
    print("=" * 65)
    
    print("\nClassification Report:\n")
    print(report_text)

    print("Confusion Matrix:")
    print(cm)

    # Save to metrics.json
    metrics = {
        'best_val_accuracy': accuracy,
        'test_accuracy': accuracy,
        'classification_report': report_dict,
        'confusion_matrix': cm.tolist()
    }
    os.makedirs("outputs/results", exist_ok=True)
    with open("outputs/results/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n[+] Results saved to outputs/results/metrics.json")
    return accuracy

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Cancer Model Accuracy")
    parser.add_argument("--data_dir", type=str, default="data/processed/test", help="Path to evaluation dataset")
    parser.add_argument("--model_path", type=str, default="models/trained/best_model.pth", help="Path to model weights .pth")
    args = parser.parse_args()
    
    evaluate_accuracy(data_dir=args.data_dir, model_path=args.model_path)
