import os
import shutil
import glob
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def prepare_multimodal_dataset():
    print("=" * 60)
    print("Preparing Multimodal Cancer Dataset for Training...")
    print("=" * 60)

    base_dir = "d:/Explainable Hybrid AI Cancer Project/data"
    raw_images_dir = os.path.join(base_dir, "data", "images")
    processed_dir = os.path.join(base_dir, "processed")
    
    train_dir = os.path.join(processed_dir, "train")
    val_dir = os.path.join(processed_dir, "val")

    classes = ['breast_cancer', 'lung_cancer', 'colon_cancer']
    for c in classes:
        os.makedirs(os.path.join(train_dir, c), exist_ok=True)
        os.makedirs(os.path.join(val_dir, c), exist_ok=True)

    # 1. Collect Breast Cancer Images from BreakHis
    print("\n1. Collecting Breast Cancer Histopathology Images...")
    breast_pattern = os.path.join(raw_images_dir, "**", "malignant", "**", "*.png")
    breast_imgs = glob.glob(breast_pattern, recursive=True)
    if not breast_imgs:
        breast_pattern = os.path.join(raw_images_dir, "**", "malignant", "*.png")
        breast_imgs = glob.glob(breast_pattern, recursive=True)
    print(f"Found {len(breast_imgs)} breast cancer malignant images.")

    # 2. Collect Lung Cancer Images (lung_aca)
    print("\n2. Collecting Lung Cancer Histopathology Images...")
    lung_pattern = os.path.join(raw_images_dir, "**", "lung_aca", "*.*")
    lung_imgs = [f for f in glob.glob(lung_pattern, recursive=True) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(lung_imgs)} lung cancer images.")

    # 3. Collect Colon Cancer Images (colon_aca)
    print("\n3. Collecting Colon Cancer Histopathology Images...")
    colon_pattern = os.path.join(raw_images_dir, "**", "colon_aca", "*.*")
    colon_imgs = [f for f in glob.glob(colon_pattern, recursive=True) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(colon_imgs)} colon cancer images.")

    # Select balanced subsets for training speed & memory efficiency (up to 1,000 per class)
    np.random.seed(42)
    max_samples = 800
    
    breast_selected = np.random.choice(breast_imgs, min(max_samples, len(breast_imgs)), replace=False) if len(breast_imgs) > 0 else []
    lung_selected = np.random.choice(lung_imgs, min(max_samples, len(lung_imgs)), replace=False) if len(lung_imgs) > 0 else []
    colon_selected = np.random.choice(colon_imgs, min(max_samples, len(colon_imgs)), replace=False) if len(colon_imgs) > 0 else []

    all_records = []

    # Copy files and build metadata
    for category, img_list in [('breast_cancer', breast_selected), ('lung_cancer', lung_selected), ('colon_cancer', colon_selected)]:
        if len(img_list) == 0:
            continue
        tr_imgs, val_imgs = train_test_split(img_list, test_size=0.2, random_state=42)
        
        for idx, img_path in enumerate(tr_imgs):
            dst_name = f"{category}_tr_{idx}{os.path.splitext(img_path)[1]}"
            dst_path = os.path.join(train_dir, category, dst_name)
            shutil.copy(img_path, dst_path)
            all_records.append({'image_path': dst_path, 'label': category, 'split': 'train'})
            
        for idx, img_path in enumerate(val_imgs):
            dst_name = f"{category}_val_{idx}{os.path.splitext(img_path)[1]}"
            dst_path = os.path.join(val_dir, category, dst_name)
            shutil.copy(img_path, dst_path)
            all_records.append({'image_path': dst_path, 'label': category, 'split': 'val'})

    metadata_df = pd.DataFrame(all_records)
    metadata_csv = os.path.join(processed_dir, "multimodal_dataset.csv")
    metadata_df.to_csv(metadata_csv, index=False)

    print("\nDataset preparation completed successfully!")
    print(f"Total processed samples: {len(metadata_df)}")
    print(f"Summary by class:\n{metadata_df['label'].value_counts()}")

if __name__ == "__main__":
    prepare_multimodal_dataset()
