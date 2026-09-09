import os
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image

class MultimodalDataset(Dataset):
    def __init__(self, data_list: list, transform=None):
        self.data_list = data_list
        self.transform = transform

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        item = self.data_list[idx]
        img_path = item.get('image_path')
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path).convert('RGB')
            if self.transform:
                img = self.transform(img)
        else:
            img = torch.randn(3, 300, 300)

        txt_tensor = torch.randn(768)
        vitals_list = item.get('vitals', [0.0]*16)
        while len(vitals_list) < 16:
            vitals_list.append(0.0)
        tab_tensor = torch.tensor(vitals_list[:16], dtype=torch.float32)

        label = torch.tensor(item.get('label', 0), dtype=torch.long)
        return img, txt_tensor, tab_tensor, label

def create_dataloader(data_list: list, batch_size: int = 16, shuffle: bool = True):
    dataset = MultimodalDataset(data_list)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
