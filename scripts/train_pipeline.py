import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from tqdm import tqdm

import sys
sys.path.insert(0, os.path.abspath("."))

from src.config import Config
from src.models.cnn_model import CancerClassificationModel

def run_training_pipeline(epochs=10, batch_size=32, lr=1e-3):
    print("=" * 60)
    print("Starting Enhanced Explainable Hybrid AI Model Training Pipeline")
    print("=" * 60)

    num_cpus = os.cpu_count() or 4
    torch.set_num_threads(num_cpus)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using compute device: {device} | CPU Threads: {num_cpus}")

    base_dir = "d:/Explainable Hybrid AI Cancer Project"
    train_dir = os.path.join(base_dir, "data", "processed", "train")
    val_dir = os.path.join(base_dir, "data", "processed", "val")
    test_dir = os.path.join(base_dir, "data", "processed", "test")

    # Enhanced Data Transforms with Augmentations
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=val_transform)
    has_test = os.path.exists(test_dir) and len(os.listdir(test_dir)) > 0
    test_dataset = datasets.ImageFolder(test_dir, transform=val_transform) if has_test else None

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0) if test_dataset else None

    class_names = train_dataset.classes
    print(f"Target Cancer Classes ({len(class_names)}): {class_names}")
    print(f"Train Dataset size: {len(train_dataset)} | Val Dataset size: {len(val_dataset)}" + (f" | Test Dataset size: {len(test_dataset)}" if test_dataset else ""))

    # Model Setup
    config = Config()
    model = CancerClassificationModel(config.model)

    # Initial Transfer Learning setup
    for param in model.backbone.parameters():
        param.requires_grad = False

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=1)

    best_acc = 0.0
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}

    print("\nExecuting Training Epochs...")
    for epoch in range(epochs):
        # Progressive unfreezing: Unfreeze layer4 of ResNet for fine-tuning after initial head training
        if epoch == 2:
            print(" [*] Unfreezing backbone layer4 parameters for fine-tuning...")
            if hasattr(model.backbone, 'layer4'):
                for param in model.backbone.layer4.parameters():
                    param.requires_grad = True
                optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr * 0.1, weight_decay=1e-4)

        # Training Phase
        model.train()
        train_loss, train_correct, train_total = 0.0, 0, 0
        for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]"):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            train_total += labels.size(0)
            train_correct += (preds == labels).sum().item()

        epoch_train_loss = train_loss / len(train_loader)
        epoch_train_acc = 100.0 * train_correct / train_total

        # Validation Phase
        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        val_preds, val_labels = [], []
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Val]"):
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (preds == labels).sum().item()
                val_preds.extend(preds.cpu().numpy())
                val_labels.extend(labels.cpu().numpy())

        epoch_val_loss = val_loss / len(val_loader)
        epoch_val_acc = 100.0 * val_correct / val_total
        scheduler.step(epoch_val_loss)

        history['train_loss'].append(epoch_train_loss)
        history['train_acc'].append(epoch_train_acc)
        history['val_loss'].append(epoch_val_loss)
        history['val_acc'].append(epoch_val_acc)

        print(f"Epoch {epoch+1}/{epochs} -> Train Loss: {epoch_train_loss:.4f}, Train Acc: {epoch_train_acc:.2f}% | Val Loss: {epoch_val_loss:.4f}, Val Acc: {epoch_val_acc:.2f}%")

        if epoch_val_acc >= best_acc:
            best_acc = epoch_val_acc
            os.makedirs("models/trained", exist_ok=True)
            torch.save(model.state_dict(), "models/trained/best_model.pth")
            torch.save(model.state_dict(), "models/trained/final_model.pth")
            print(f" [+] Saved new best model weights (Val Acc: {best_acc:.2f}%)")

    # Evaluation on Holdout Test Set
    test_acc = best_acc
    test_report = {}
    test_cm = []
    if test_loader:
        print("\nEvaluating on Holdout Test Set...")
        model.eval()
        test_correct, test_total = 0, 0
        all_test_preds, all_test_labels = [], []
        with torch.no_grad():
            for images, labels in tqdm(test_loader, desc="[Holdout Test Set]"):
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)
                test_total += labels.size(0)
                test_correct += (preds == labels).sum().item()
                all_test_preds.extend(preds.cpu().numpy())
                all_test_labels.extend(labels.cpu().numpy())

        test_acc = 100.0 * test_correct / test_total
        test_cm = confusion_matrix(all_test_labels, all_test_preds).tolist()
        test_report = classification_report(all_test_labels, all_test_preds, target_names=class_names, output_dict=True)
        print(f" [+] Holdout Test Set Accuracy: {test_acc:.2f}%")
    else:
        test_cm = confusion_matrix(val_labels, val_preds).tolist()
        test_report = classification_report(val_labels, val_preds, target_names=class_names, output_dict=True)

    # Final Evaluation & Visualization Artifacts
    print("\nGenerating Evaluation Metrics & Visualizations...")
    os.makedirs("outputs/results", exist_ok=True)
    os.makedirs("outputs/visualizations", exist_ok=True)

    cm_np = np.array(test_cm)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_np, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix - Multimodal Cancer Classification')
    plt.xlabel('Predicted Class')
    plt.ylabel('True Class')
    plt.tight_layout()
    plt.savefig("outputs/visualizations/confusion_matrix.png", dpi=150)
    plt.close()

    # Plot Training Curves
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.title('Loss Curves')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Acc')
    plt.plot(history['val_acc'], label='Val Acc')
    plt.title('Accuracy Curves')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()

    plt.tight_layout()
    plt.savefig("outputs/visualizations/training_curves.png", dpi=150)
    plt.close()

    metrics = {
        'best_val_accuracy': best_acc,
        'test_accuracy': test_acc,
        'classification_report': test_report,
        'confusion_matrix': test_cm
    }
    with open("outputs/results/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print(f"TRAINING COMPLETE! Best Validation Acc: {best_acc:.2f}% | Holdout Test Acc: {test_acc:.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    run_training_pipeline(epochs=10, batch_size=32)

