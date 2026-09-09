import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import os
import json
import pickle
from datetime import datetime
from typing import Dict, Any, Tuple

from src.training.augment import get_transforms

class Trainer:
    """Complete training pipeline"""
    
    def __init__(self, model, config, device):
        self.model = model.to(device)
        self.config = config.training
        self.device = device
        self.best_acc = 0.0
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
        self.class_names = None
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader) -> float:
        """Complete training pipeline"""
        criterion = nn.CrossEntropyLoss()
        
        # Setup optimizer
        if self.config.optimizer == 'adam':
            optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        elif self.config.optimizer == 'sgd':
            optimizer = optim.SGD(self.model.parameters(), lr=self.config.learning_rate, momentum=0.9)
        else:
            raise ValueError(f"Unsupported optimizer: {self.config.optimizer}")
        
        # Setup scheduler
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', patience=5, factor=0.1
        )
        
        print(f"Starting training on {self.device}")
        print(f"Epochs: {self.config.epochs}, Batch size: {self.config.batch_size}")
        print("-" * 50)
        
        for epoch in range(self.config.epochs):
            # Training phase
            train_loss, train_acc = self._train_epoch(train_loader, criterion, optimizer)
            
            # Validation phase
            val_loss, val_acc = self._validate(val_loader, criterion)
            
            # Update history
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            print(f"Epoch {epoch+1}/{self.config.epochs}")
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
            
            # Save best model
            if val_acc > self.best_acc:
                self.best_acc = val_acc
                self._save_model('best_model.pth')
                print(f"✓ New best model saved with accuracy: {val_acc:.2f}%")
            
            # Early stopping
            if epoch > 10 and min(self.history['val_loss'][-5:]) > val_loss:
                print("Early stopping triggered...")
                break
            
            print("-" * 50)
        
        # Save final model and history
        self._save_model('final_model.pth')
        self._save_history()
        self._save_config()
        
        print(f"Training complete! Best accuracy: {self.best_acc:.2f}%")
        
        return self.best_acc
    
    def _train_epoch(self, loader: DataLoader, criterion, optimizer) -> Tuple[float, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in tqdm(loader, desc="Training"):
            images, labels = images.to(self.device), labels.to(self.device)
            
            optimizer.zero_grad()
            outputs = self.model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy
    
    def _validate(self, loader: DataLoader, criterion) -> Tuple[float, float]:
        """Validate the model"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy
    
    def _save_model(self, filename: str):
        """Save model weights"""
        os.makedirs('models/trained', exist_ok=True)
        torch.save(self.model.state_dict(), f'models/trained/{filename}')
    
    def _save_history(self):
        """Save training history"""
        os.makedirs('outputs/results', exist_ok=True)
        
        with open('outputs/results/training_history.json', 'w') as f:
            json.dump(self.history, f)
        
        # Plot training curves
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        axes[0].plot(self.history['train_loss'], label='Train Loss')
        axes[0].plot(self.history['val_loss'], label='Val Loss')
        axes[0].set_title('Loss Curves')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        axes[1].plot(self.history['train_acc'], label='Train Acc')
        axes[1].plot(self.history['val_acc'], label='Val Acc')
        axes[1].set_title('Accuracy Curves')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy (%)')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        os.makedirs('outputs/visualizations', exist_ok=True)
        plt.savefig('outputs/visualizations/training_curves.png', dpi=150)
        plt.close()
    
    def _save_config(self):
        """Save configuration"""
        with open('outputs/results/config.json', 'w') as f:
            json.dump(self.config.__dict__, f)

def evaluate_model(model, test_loader: DataLoader, class_names: list, device: str) -> Dict[str, Any]:
    """Evaluate model performance"""
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Evaluating"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            probabilities = torch.softmax(outputs, dim=1)
            _, predicted = torch.max(outputs.data, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probabilities.cpu().numpy())
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    
    # Classification report
    report = classification_report(
        all_labels, 
        all_preds, 
        target_names=class_names,
        output_dict=True
    )
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    
    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    os.makedirs('outputs/visualizations', exist_ok=True)
    plt.savefig('outputs/visualizations/confusion_matrix.png', dpi=150)
    plt.close()
    
    # Save metrics
    metrics = {
        'accuracy': accuracy,
        'classification_report': report,
        'confusion_matrix': cm.tolist(),
        'per_class_accuracy': {
            class_names[i]: report[class_names[i]]['recall'] 
            for i in range(len(class_names))
        }
    }
    
    with open('outputs/results/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\nAccuracy: {accuracy*100:.2f}%")
    print("\nPer-class accuracy:")
    for class_name, acc in metrics['per_class_accuracy'].items():
        print(f"  {class_name}: {acc*100:.2f}%")
    
    return metrics
