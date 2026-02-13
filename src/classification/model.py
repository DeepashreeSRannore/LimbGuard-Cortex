"""Vision Transformer classifier for gangrene grade detection.

Wraps a Hugging Face ViT model for fine-tuning and inference on the
LimbGuard-Cortex foot image dataset.
"""

import os
from typing import Optional

import torch
import torch.nn as nn
from transformers import ViTForImageClassification, ViTFeatureExtractor

from src.config import (
    VIT_MODEL_NAME,
    NUM_CLASSES,
    CLASS_NAMES,
    CHECKPOINT_DIR,
    IMAGE_SIZE,
)


class GangreneClassifier(nn.Module):
    """ViT-based classifier that predicts gangrene grade from a foot image.

    The backbone is a pre-trained ``google/vit-base-patch16-224-in21k``
    model.  The final classification head is replaced with a linear layer
    mapping to ``NUM_CLASSES`` outputs.
    """

    def __init__(self, num_classes: int = NUM_CLASSES, model_name: str = VIT_MODEL_NAME):
        super().__init__()
        self.model = ViTForImageClassification.from_pretrained(
            model_name,
            num_labels=num_classes,
            ignore_mismatched_sizes=True,
        )
        self.model.config.id2label = {i: c for i, c in enumerate(CLASS_NAMES)}
        self.model.config.label2id = {c: i for i, c in enumerate(CLASS_NAMES)}

    def forward(self, pixel_values: torch.Tensor, labels: Optional[torch.Tensor] = None):
        return self.model(pixel_values=pixel_values, labels=labels)

    # ── convenience helpers ────────────────────────────────────────────
    def predict(self, pixel_values: torch.Tensor) -> str:
        """Return the predicted class name for a single image tensor."""
        self.eval()
        with torch.no_grad():
            outputs = self.forward(pixel_values.unsqueeze(0) if pixel_values.dim() == 3 else pixel_values)
            pred_idx = outputs.logits.argmax(dim=-1).item()
        return CLASS_NAMES[pred_idx]

    def save(self, path: Optional[str] = None):
        path = path or os.path.join(CHECKPOINT_DIR, "vit_classifier.pt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.state_dict(), path)

    def load(self, path: Optional[str] = None, device: str = "cpu"):
        path = path or os.path.join(CHECKPOINT_DIR, "vit_classifier.pt")
        self.load_state_dict(torch.load(path, map_location=device))
        self.eval()


def get_feature_extractor():
    """Return the ViT feature extractor for image pre-processing."""
    return ViTFeatureExtractor.from_pretrained(VIT_MODEL_NAME)
