import os
import shutil
import random
import hashlib
from pathlib import Path
import json
from PIL import Image
from tqdm import tqdm

def file_md5(file_path: Path) -> str:
    """Calculate MD5 hash of file content for deduplication."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def organize_data(raw_dir: str = 'Datasets', output_dir: str = 'data/processed', train_ratio: float = 0.8, val_ratio: float = 0.1, max_samples_per_class: int = 1500):
    """Organize raw data from Datasets directory into pre-resized (224x224) train/val/test splits without leakage."""
    
    random.seed(42)
    
    cancer_folders = {
        'breast_cancer': 'Breast Cancer',
        'lung_cancer': 'Lung Cancer',
        'colon_cancer': 'Colon Cancer'
    }
    
    splits = ['train', 'val', 'test']
    
    # Clean previous processed dir if exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    for split in splits:
        for cancer_type in cancer_folders.keys():
            os.makedirs(os.path.join(output_dir, split, cancer_type), exist_ok=True)
            
    print(f"Scanning raw dataset folder: {raw_dir}")
    raw_path = Path(raw_dir)
    
    dataset_summary = {}
    
    for cancer_type, folder_name in cancer_folders.items():
        target_dir = raw_path / folder_name
        if not target_dir.exists():
            print(f"Warning: Directory {target_dir} does not exist!")
            continue
            
        all_images = []
        for file_path in target_dir.rglob('*'):
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
                all_images.append(file_path)
                
        print(f"Found {len(all_images)} total files for {cancer_type} in {target_dir}")
        
        # Deduplicate files based on content MD5 hash to prevent data leakage across splits
        unique_images = []
        seen_hashes = set()
        for img_path in all_images:
            try:
                h = file_md5(img_path)
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    unique_images.append(img_path)
            except Exception:
                continue
                
        print(f"  [{cancer_type}] Deduplicated unique images count: {len(unique_images)}")
        
        # Shuffle & sample up to max_samples_per_class
        random.shuffle(unique_images)
        if max_samples_per_class and max_samples_per_class > 0:
            selected_images = unique_images[:max_samples_per_class]
        else:
            selected_images = unique_images
        
        n_total = len(selected_images)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        
        train_images = selected_images[:n_train]
        val_images = selected_images[n_train:n_train + n_val]
        test_images = selected_images[n_train + n_val:]
        
        print(f"  [{cancer_type}] Saving {n_total} samples (224x224) -> Train: {len(train_images)}, Val: {len(val_images)}, Test: {len(test_images)}")
        
        # Process and save train images
        for idx, img_path in enumerate(tqdm(train_images, desc=f"Processing {cancer_type} Train")):
            try:
                dest_name = f"{cancer_type}_tr_{idx}.jpg"
                dest_path = os.path.join(output_dir, 'train', cancer_type, dest_name)
                with Image.open(img_path) as img:
                    img = img.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
                    img.save(dest_path, 'JPEG', quality=90)
            except Exception:
                continue
            
        # Process and save val images
        for idx, img_path in enumerate(tqdm(val_images, desc=f"Processing {cancer_type} Val")):
            try:
                dest_name = f"{cancer_type}_val_{idx}.jpg"
                dest_path = os.path.join(output_dir, 'val', cancer_type, dest_name)
                with Image.open(img_path) as img:
                    img = img.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
                    img.save(dest_path, 'JPEG', quality=90)
            except Exception:
                continue

        # Process and save test images
        for idx, img_path in enumerate(tqdm(test_images, desc=f"Processing {cancer_type} Test")):
            try:
                dest_name = f"{cancer_type}_te_{idx}.jpg"
                dest_path = os.path.join(output_dir, 'test', cancer_type, dest_name)
                with Image.open(img_path) as img:
                    img = img.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
                    img.save(dest_path, 'JPEG', quality=90)
            except Exception:
                continue
            
        dataset_summary[cancer_type] = {
            'total_found': len(all_images),
            'unique_count': len(unique_images),
            'train_count': len(train_images),
            'val_count': len(val_images),
            'test_count': len(test_images)
        }
        
    print("\nData pre-resizing complete!")
    
    dataset_info = {
        'train_ratio': train_ratio,
        'val_ratio': val_ratio,
        'test_ratio': 1.0 - train_ratio - val_ratio,
        'cancer_types': list(cancer_folders.keys()),
        'summary': dataset_summary,
        'total_processed': sum(info['train_count'] + info['val_count'] + info['test_count'] for info in dataset_summary.values())
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/dataset_info.json', 'w') as f:
        json.dump(dataset_info, f, indent=2)
        
    print(f"Saved dataset summary to data/dataset_info.json")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_dir', type=str, default='Datasets')
    parser.add_argument('--output_dir', type=str, default='data/processed')
    parser.add_argument('--train_ratio', type=float, default=0.8)
    parser.add_argument('--val_ratio', type=float, default=0.1)
    parser.add_argument('--max_samples', type=int, default=1500)
    args = parser.parse_args()
    
    organize_data(args.raw_dir, args.output_dir, args.train_ratio, args.val_ratio, args.max_samples)

