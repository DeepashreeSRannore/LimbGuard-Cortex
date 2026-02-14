"""Centralized configuration for LimbGuard-Cortex pipeline."""

import os

# ── Project paths ──────────────────────────────────────────────────────────
# config.py is now at backend/src/config.py, so we need to go up 2 levels to get to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_DIR = os.path.join(PROJECT_ROOT, "Dataset")
WOUND_DATA_DIR = os.path.join(DATASET_DIR, "wound-segmentation", "data",
                              "Medetec_foot_ulcer_224")
NORMAL_DATA_DIR = os.path.join(DATASET_DIR, "normal_feet_images")
KNOWLEDGE_BASE_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
CHECKPOINT_DIR = os.path.join(PROJECT_ROOT, "checkpoints")

# ── Image classification settings ──────────────────────────────────────────
IMAGE_SIZE = 224
NUM_CLASSES = 5  # normal, grade_1, grade_2, grade_3, grade_4
CLASS_NAMES = ["normal", "grade_1", "grade_2", "grade_3", "grade_4"]
VIT_MODEL_NAME = "google/vit-base-patch16-224-in21k"
CLASSIFIER_BATCH_SIZE = 16
CLASSIFIER_EPOCHS = 10
CLASSIFIER_LR = 2e-5

# ── NLP / advice settings ──────────────────────────────────────────────────
NLP_MODEL_NAME = "distilgpt2"
MAX_ADVICE_TOKENS = 256

# ── RAG settings ───────────────────────────────────────────────────────────
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "knowledge_base", "faiss_index")
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50
RAG_TOP_K = 3
