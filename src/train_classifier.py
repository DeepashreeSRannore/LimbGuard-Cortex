"""Training script for the Vision Transformer gangrene classifier.

Usage::

    python -m src.train_classifier [--epochs N] [--batch-size B] [--lr LR]
"""

import argparse
import os

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


def train(epochs: int = CLASSIFIER_EPOCHS,
          batch_size: int = CLASSIFIER_BATCH_SIZE,
          lr: float = CLASSIFIER_LR):
    """Train the ViT classifier on the LimbGuard dataset."""

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # ── data ───────────────────────────────────────────────────────────
    paths, labels = build_dataset()
    if not paths:
        print("ERROR: No images found.  Check that the Dataset/ folder "
              "contains images under normal_feet_images/ and "
              "wound-segmentation/data/Medetec_foot_ulcer_224/.")
        return

    print(f"Found {len(paths)} images across {NUM_CLASSES} classes.")
    for i, name in enumerate(CLASS_NAMES):
        count = labels.count(i)
        print(f"  {name}: {count}")

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

        print(f"Epoch {epoch}/{epochs} | "
              f"train_loss={train_loss:.4f} | "
              f"val_loss={val_loss:.4f} | "
              f"val_acc={accuracy:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            model.save()
            print("  → checkpoint saved")

    print("Training complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train gangrene classifier")
    parser.add_argument("--epochs", type=int, default=CLASSIFIER_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=CLASSIFIER_BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=CLASSIFIER_LR)
    args = parser.parse_args()
    train(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
