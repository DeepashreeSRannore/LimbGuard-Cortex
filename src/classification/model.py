"""Vision Transformer classifier for gangrene grade detection.

Wraps a Hugging Face ViT model for fine-tuning and inference on the
LimbGuard-Cortex foot image dataset.
"""

import logging
import os
from typing import Optional

import torch
import torch.nn as nn
from transformers import ViTForImageClassification, ViTImageProcessor, ViTConfig

from src.config import (
    VIT_MODEL_NAME,
    NUM_CLASSES,
    CLASS_NAMES,
    CHECKPOINT_DIR,
    IMAGE_SIZE,
)

logger = logging.getLogger(__name__)


class GangreneClassifier(nn.Module):
    """ViT-based classifier that predicts gangrene grade from a foot image.

    The backbone is a pre-trained ``google/vit-base-patch16-224-in21k``
    model.  The final classification head is replaced with a linear layer
    mapping to ``NUM_CLASSES`` outputs.

    When the pre-trained model cannot be downloaded (e.g. in an offline
    environment), the model is initialised from a matching ViT
    configuration with random weights so that training can still proceed.
    """

    def __init__(self, num_classes: int = NUM_CLASSES, model_name: str = VIT_MODEL_NAME):
        super().__init__()
        try:
            self.model = ViTForImageClassification.from_pretrained(
                model_name,
                num_labels=num_classes,
                ignore_mismatched_sizes=True,
            )
            logger.info("Loaded pre-trained weights from %s", model_name)
        except (OSError, ConnectionError, ValueError, RuntimeError):
            logger.warning(
                "Could not download pre-trained weights for %s. "
                "Initialising ViT from scratch.", model_name,
            )
            config = ViTConfig(
                image_size=IMAGE_SIZE,
                patch_size=16,
                num_labels=num_classes,
                num_hidden_layers=12,
                hidden_size=768,
                intermediate_size=3072,
                num_attention_heads=12,
            )
            self.model = ViTForImageClassification(config)
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
        self.load_state_dict(torch.load(path, map_location=device, weights_only=True))
        self.eval()


def get_feature_extractor():
    """Return the ViT image processor for image pre-processing.

    Falls back to constructing a processor from the default ViT
    configuration when the Hub is unreachable.
    """
    try:
        return ViTImageProcessor.from_pretrained(VIT_MODEL_NAME)
    except (OSError, ConnectionError, ValueError, RuntimeError):
        logger.warning(
            "Could not download ViTImageProcessor for %s. "
            "Using default processor configuration.", VIT_MODEL_NAME,
        )
        return ViTImageProcessor(
            size={"height": IMAGE_SIZE, "width": IMAGE_SIZE},
            do_normalize=True,
            image_mean=[0.485, 0.456, 0.406],
            image_std=[0.229, 0.224, 0.225],
        )
