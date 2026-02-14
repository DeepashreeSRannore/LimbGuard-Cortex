"""Dataset loader for LimbGuard-Cortex image classification.

Scans the Dataset folder to build a labelled dataset of foot images with
gangrene grade annotations.  Normal feet images come from the
``normal_feet_images`` sub-tree and wound images from the Medetec dataset.
"""

import os
import glob
from typing import List, Tuple

from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from backend.src.config import (
    IMAGE_SIZE,
    NORMAL_DATA_DIR,
    WOUND_DATA_DIR,
    CLASS_NAMES,
)


def _collect_image_paths(root: str, extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png")) -> List[str]:
    """Recursively collect image file paths under *root*."""
    paths: List[str] = []
    for ext in extensions:
        paths.extend(glob.glob(os.path.join(root, "**", f"*{ext}"), recursive=True))
    return sorted(paths)


class FootDataset(Dataset):
    """PyTorch Dataset that yields ``(image_tensor, label_index)`` pairs.

    Parameters
    ----------
    image_paths : list[str]
        Absolute paths to image files.
    labels : list[int]
        Integer class labels aligned with *image_paths*.
    transform : torchvision.transforms.Compose, optional
        Image transforms.  A sensible default is applied when *None*.
    """

    def __init__(self, image_paths: List[str], labels: List[int], transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform or transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert("RGB")
        img = self.transform(img)
        return img, self.labels[idx]


def build_dataset() -> Tuple[List[str], List[int]]:
    """Scan the repository Dataset folder and return ``(paths, labels)``.

    Label mapping (index → name) follows ``config.CLASS_NAMES``:
      0 – normal, 1 – grade_1, 2 – grade_2, 3 – grade_3, 4 – grade_4

    Wound images that do not have an explicit grade sub-folder are assigned
    to *grade_1* by default.
    """
    paths: List[str] = []
    labels: List[int] = []

    # Normal images
    if os.path.isdir(NORMAL_DATA_DIR):
        for p in _collect_image_paths(NORMAL_DATA_DIR):
            paths.append(p)
            labels.append(CLASS_NAMES.index("normal"))

    # Wound images – check for grade sub-folders first
    if os.path.isdir(WOUND_DATA_DIR):
        train_img_dir = os.path.join(WOUND_DATA_DIR, "train", "images")
        test_img_dir = os.path.join(WOUND_DATA_DIR, "test", "images")
        for img_dir in (train_img_dir, test_img_dir):
            if os.path.isdir(img_dir):
                # Check for grade sub-directories
                sub_dirs = [d for d in os.listdir(img_dir)
                            if os.path.isdir(os.path.join(img_dir, d))]
                if sub_dirs:
                    for sub in sub_dirs:
                        grade_name = sub.lower().replace(" ", "_")
                        if grade_name in CLASS_NAMES:
                            label_idx = CLASS_NAMES.index(grade_name)
                        else:
                            label_idx = CLASS_NAMES.index("grade_1")
                        for p in _collect_image_paths(os.path.join(img_dir, sub)):
                            paths.append(p)
                            labels.append(label_idx)
                else:
                    # Flat directory – default to grade_1
                    for p in _collect_image_paths(img_dir):
                        paths.append(p)
                        labels.append(CLASS_NAMES.index("grade_1"))

    return paths, labels
