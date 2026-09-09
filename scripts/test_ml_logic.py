import os
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

import sys
sys.path.insert(0, os.path.abspath("."))

from src.config import Config
from src.models.cnn_model import CancerClassificationModel

def inspect_ml_logic(image_path: str, target_class_idx: int = 0):
    """
    Step-by-step ML logic inspection for a single image sample.
    Exposes raw features, model logits, cross-entropy loss, softmax probabilities, and decision confidence.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    class_names = ['breast_cancer', 'colon_cancer', 'lung_cancer']
    
    print("\n" + "=" * 70)
    print(" STEP-BY-STEP ML MODEL LOGIC INSPECTION ")
    print("=" * 70)
    print(f" [*] Image File          : {image_path}")
    print(f" [*] Expected True Class : {class_names[target_class_idx]} (idx: {target_class_idx})")
    
    # 1. Image Preprocessing & Tensor Pipeline
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    img = Image.open(image_path).convert('RGB')
    input_tensor = transform(img).unsqueeze(0).to(device)  # Shape: (1, 3, 224, 224)
    print(f" [*] Preprocessed Tensor : Shape {tuple(input_tensor.shape)} | Min: {input_tensor.min():.2f}, Max: {input_tensor.max():.2f}")

    # 2. Load ML Model
    config = Config()
    model = CancerClassificationModel(config.model)
    model.load_state_dict(torch.load("models/trained/best_model.pth", map_location=device))
    model = model.to(device)
    model.eval()

    with torch.no_grad():
        # 3. Extract Deep Feature Vector (2048-dim representation from ResNet backbone)
        features = model.get_features(input_tensor)  # Shape: (1, 2048)
        
        # 4. Classifier Head Forward Pass (Logits)
        logits = model(input_tensor)  # Shape: (1, 3)
        
        # 5. Softmax Normalization (Probabilities)
        probabilities = F.softmax(logits, dim=1)[0]
        
        # 6. Loss Calculation (CrossEntropy)
        target_tensor = torch.tensor([target_class_idx], device=device)
        loss = F.cross_entropy(logits, target_tensor).item()

    pred_idx = torch.argmax(probabilities).item()
    pred_class = class_names[pred_idx]
    confidence = probabilities[pred_idx].item() * 100.0
    
    sorted_probs, _ = torch.sort(probabilities, descending=True)
    margin = (sorted_probs[0] - sorted_probs[1]).item() * 100.0

    # Output Detailed ML Logic Steps
    print("-" * 70)
    print(" ML LOGIC PIPELINE BREAKDOWN ")
    print("-" * 70)
    print(f" 1. Backbone Feature Vector : Vector norm = {torch.norm(features):.4f} (2048 dims)")
    print(f" 2. Classifier Raw Logits   : {[round(x, 4) for x in logits[0].tolist()]}")
    print(f" 3. CrossEntropy Loss       : {loss:.6f}")
    print(f" 4. Softmax Probabilities   :")
    for idx, cname in enumerate(class_names):
        indicator = "  <-- PREDICTED" if idx == pred_idx else ""
        print(f"    - {cname:<15}: {probabilities[idx].item()*100:6.2f}% ({probabilities[idx].item():.6f}){indicator}")
    print(f" 5. Decision Confidence     : {confidence:.2f}% (Margin over 2nd candidate: {margin:.2f}%)")
    print(f" 6. Logic Decision Match    : {'CORRECT [PASS]' if pred_idx == target_class_idx else 'INCORRECT [FAIL]'}")
    print("=" * 70 + "\n")
    
    return pred_idx == target_class_idx

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inspect ML Model Logic Step-by-Step")
    parser.add_argument("--image", type=str, default="data/processed/test/breast_cancer/sample_1.jpg", help="Path to sample image")
    parser.add_argument("--class_idx", type=int, default=0, help="Expected ground truth class index (0: breast, 1: colon, 2: lung)")
    args = parser.parse_args()
    
    if os.path.exists(args.image):
        inspect_ml_logic(args.image, args.class_idx)
    else:
        # Fallback to finding first image in test folder
        test_dir = "data/processed/test"
        found = False
        for cidx, cname in enumerate(['breast_cancer', 'colon_cancer', 'lung_cancer']):
            folder = os.path.join(test_dir, cname)
            if os.path.exists(folder) and os.listdir(folder):
                img_name = os.listdir(folder)[0]
                img_path = os.path.join(folder, img_name)
                inspect_ml_logic(img_path, cidx)
                found = True
                break
        if not found:
            print(f"[!] No test images found in {test_dir}")
