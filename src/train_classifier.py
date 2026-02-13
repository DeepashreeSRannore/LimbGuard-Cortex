"""Training script for the Vision Transformer gangrene classifier.

Usage::

    python -m src.train_classifier [--epochs N] [--batch-size B] [--lr LR]
"""

import argparse
import json
import logging
import os
import time

import torch
from torch.utils.data import DataLoader, random_split

from src.config import (
    CLASSIFIER_BATCH_SIZE,
    CLASSIFIER_EPOCHS,
    CLASSIFIER_LR,
    CHECKPOINT_DIR,
    NUM_CLASSES,
    CLASS_NAMES,
)
from src.classification.dataset import FootDataset, build_dataset
from src.classification.model import GangreneClassifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def train(epochs: int = CLASSIFIER_EPOCHS,
          batch_size: int = CLASSIFIER_BATCH_SIZE,
          lr: float = CLASSIFIER_LR):
    """Train the ViT classifier on the LimbGuard dataset."""

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Using device: %s", device)

    # ── data ───────────────────────────────────────────────────────────
    paths, labels = build_dataset()
    if not paths:
        logger.error(
            "No images found. Check that the Dataset/ folder "
            "contains images under normal_feet_images/ and "
            "wound-segmentation/data/Medetec_foot_ulcer_224/."
        )
        return

    logger.info("Found %d images across %d classes.", len(paths), NUM_CLASSES)
    for i, name in enumerate(CLASS_NAMES):
        count = labels.count(i)
        logger.info("  %s: %d", name, count)

    dataset = FootDataset(paths, labels)
    val_size = max(1, int(0.2 * len(dataset)))
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    # ── model ──────────────────────────────────────────────────────────
    model = GangreneClassifier().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    best_val_loss = float("inf")
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    history = {"train_loss": [], "val_loss": [], "val_acc": []}
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        train_loss = 0.0
        for imgs, lbls in train_loader:
            imgs, lbls = imgs.to(device), lbls.to(device)
            outputs = model(imgs, labels=lbls)
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        train_loss /= len(train_loader)

        # Validate
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for imgs, lbls in val_loader:
                imgs, lbls = imgs.to(device), lbls.to(device)
                outputs = model(imgs, labels=lbls)
                val_loss += outputs.loss.item()
                preds = outputs.logits.argmax(dim=-1)
                correct += (preds == lbls).sum().item()
                total += lbls.size(0)
        val_loss /= len(val_loader)
        accuracy = correct / total if total else 0.0

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(accuracy)

        logger.info(
            "Epoch %d/%d | train_loss=%.4f | val_loss=%.4f | val_acc=%.4f",
            epoch, epochs, train_loss, val_loss, accuracy,
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            model.save()
            logger.info("  → checkpoint saved")

    elapsed = time.time() - start_time
    logger.info("Training complete in %.1f seconds.", elapsed)

    # Save training history
    history_path = os.path.join(CHECKPOINT_DIR, "training_history.json")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    logger.info("Training history saved to %s", history_path)

    return history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train gangrene classifier")
    parser.add_argument("--epochs", type=int, default=CLASSIFIER_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=CLASSIFIER_BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=CLASSIFIER_LR)
    args = parser.parse_args()
    train(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
