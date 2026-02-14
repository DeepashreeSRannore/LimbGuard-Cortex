"""Tests for the LimbGuard-Cortex pipeline.

These tests verify core logic without requiring heavy ML model downloads
or GPU resources.
"""

import os
import sys
import tempfile

import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.src.config import CLASS_NAMES, NUM_CLASSES, PROJECT_ROOT  # noqa: E402
from backend.src.nlp.advisor import generate_advice  # noqa: E402


# ── config tests ───────────────────────────────────────────────────────────
class TestConfig:
    def test_class_names_length(self):
        assert len(CLASS_NAMES) == NUM_CLASSES

    def test_class_names_include_normal(self):
        assert "normal" in CLASS_NAMES

    def test_project_root_exists(self):
        assert os.path.isdir(PROJECT_ROOT)


# ── NLP advisor tests ─────────────────────────────────────────────────────
class TestAdvisor:
    def test_normal_advice_keys(self):
        advice = generate_advice("normal")
        assert "status" in advice
        assert "sugar_maintenance" in advice
        assert "skin_care" in advice
        assert "scheduling" in advice

    def test_normal_advice_status(self):
        advice = generate_advice("normal")
        assert "normal" in advice["status"].lower()

    @pytest.mark.parametrize("grade", ["grade_1", "grade_2", "grade_3", "grade_4"])
    def test_grade_advice_keys(self, grade):
        advice = generate_advice(grade)
        assert "status" in advice
        assert "urgency" in advice
        assert "recommended_action" in advice
        assert "home_care" in advice

    @pytest.mark.parametrize("grade,urgency", [
        ("grade_1", "LOW-MODERATE"),
        ("grade_2", "MODERATE"),
        ("grade_3", "HIGH"),
        ("grade_4", "CRITICAL"),
    ])
    def test_grade_urgency(self, grade, urgency):
        advice = generate_advice(grade)
        assert advice["urgency"] == urgency

    def test_unknown_classification(self):
        advice = generate_advice("unknown_label")
        assert "unknown" in advice["status"].lower()

    def test_case_insensitive(self):
        advice = generate_advice("  Normal  ")
        assert "normal" in advice["status"].lower()


# ── dataset tests ──────────────────────────────────────────────────────────
class TestDataset:
    def test_build_dataset_returns_lists(self):
        from backend.src.classification.dataset import build_dataset
        paths, labels = build_dataset()
        assert isinstance(paths, list)
        assert isinstance(labels, list)
        assert len(paths) == len(labels)

    def test_foot_dataset_len(self):
        from backend.src.classification.dataset import FootDataset
        # Empty dataset
        ds = FootDataset([], [])
        assert len(ds) == 0


# ── RAG engine tests ──────────────────────────────────────────────────────
class TestRAGEngine:
    def test_chunk_text(self):
        from backend.src.rag.engine import RAGEngine
        text = "A" * 1000
        chunks = RAGEngine._chunk_text(text, chunk_size=200, overlap=50)
        assert len(chunks) > 1
        assert all(len(c) <= 200 for c in chunks)

    def test_load_text_files(self):
        from backend.src.rag.engine import RAGEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "test.txt")
            with open(fpath, "w") as f:
                f.write("test content")
            docs = RAGEngine._load_text_files(tmpdir)
            assert len(docs) == 1
            assert docs[0] == "test content"

    def test_get_rag_advice_fallback(self):
        from backend.src.rag.engine import get_rag_advice
        result = get_rag_advice("grade_1")
        assert "consult" in result.lower() or "knowledge base" in result.lower()


# ── model tests ────────────────────────────────────────────────────────────
class TestModel:
    def test_classifier_init_from_scratch(self):
        """Model initialises from config when pre-trained weights are unavailable."""
        from backend.src.classification.model import GangreneClassifier
        # Use a non-existent model name to trigger the from-scratch fallback
        model = GangreneClassifier(model_name="nonexistent/model-name")
        assert model is not None
        # Should have the correct number of output labels
        assert model.model.config.num_labels == NUM_CLASSES

    def test_classifier_forward(self):
        """Forward pass produces logits of the expected shape."""
        import torch
        from backend.src.classification.model import GangreneClassifier
        model = GangreneClassifier(model_name="nonexistent/model-name")
        dummy = torch.randn(1, 3, 224, 224)
        output = model(dummy)
        assert output.logits.shape == (1, NUM_CLASSES)

    def test_classifier_predict(self):
        """predict() returns a valid class name."""
        import torch
        from backend.src.classification.model import GangreneClassifier
        model = GangreneClassifier(model_name="nonexistent/model-name")
        dummy = torch.randn(3, 224, 224)
        pred = model.predict(dummy)
        assert pred in CLASS_NAMES


# ── knowledge base tests ──────────────────────────────────────────────────
class TestKnowledgeBase:
    def test_knowledge_base_dir_exists(self):
        from backend.src.config import KNOWLEDGE_BASE_DIR
        assert os.path.isdir(KNOWLEDGE_BASE_DIR)

    def test_knowledge_base_has_documents(self):
        from backend.src.config import KNOWLEDGE_BASE_DIR
        txt_files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith(".txt")]
        assert len(txt_files) >= 1
