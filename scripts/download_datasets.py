import os
import requests
from tqdm import tqdm
import zipfile

def download_kaggle_dataset(dataset_name: str, output_dir: str = 'data/raw'):
    """Download dataset from Kaggle (requires kaggle CLI)"""
    import subprocess
    
    os.makedirs(output_dir, exist_ok=True)
    current_dir = os.getcwd()
    os.chdir(output_dir)
    
    try:
        subprocess.run(['kaggle', 'datasets', 'download', dataset_name], check=True)
        print(f"Downloaded {dataset_name}")
        
        # Unzip
        zip_path = f"{dataset_name.split('/')[-1]}.zip"
        if os.path.exists(zip_path):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(f"{dataset_name.split('/')[-1]}")
            os.remove(zip_path)
            
        os.chdir(current_dir)
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to download {dataset_name}. Please install kaggle CLI.")
        os.chdir(current_dir)
        return False
    except Exception as e:
        print(f"Error processing dataset {dataset_name}: {e}")
        os.chdir(current_dir)
        return False

def prepare_cancer_datasets():
    """Download and prepare all cancer datasets"""
    
    print("=" * 60)
    print("Cancer Dataset Downloader")
    print("=" * 60)
    
    datasets = [
        ('paultimothymooney/breast-histopathology-images', 'breast'),
        ('andrewmvd/lung-and-colon-cancer-histopathological-images', 'lung_colon')
    ]
    
    print("\nThis script requires Kaggle API to be configured.")
    print("If you don't have Kaggle API, please download datasets manually.")
    print("\nManual download links:")
    print("1. Breast Cancer: https://www.kaggle.com/datasets/paultimothymooney/breast-histopathology-images")
    print("2. Lung & Colon: https://www.kaggle.com/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images")
    print("\nPlace downloaded data in data/raw/ directory")
    
    response = input("\nAttempt automatic download? (y/n): ")
    
    if response.lower() == 'y':
        for dataset_name, folder_name in datasets:
            print(f"\nDownloading {folder_name}...")
            download_kaggle_dataset(dataset_name)
    
    print("\nDataset preparation complete!")
    print("Please organize data as:")
    print("data/train/breast_cancer/, data/train/lung_cancer/, data/train/colon_cancer/")
    print("data/val/breast_cancer/, data/val/lung_cancer/, data/val/colon_cancer/")

if __name__ == "__main__":
    prepare_cancer_datasets()
