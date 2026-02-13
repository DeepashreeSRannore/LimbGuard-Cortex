"""Tests for the LimbGuard-Cortex pipeline.

These tests verify core logic without requiring heavy ML model downloads
or GPU resources.
"""

import os
import sys
import tempfile

import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import CLASS_NAMES, NUM_CLASSES, PROJECT_ROOT  # noqa: E402
from src.nlp.advisor import generate_advice  # noqa: E402


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
        from src.classification.dataset import build_dataset
        paths, labels = build_dataset()
        assert isinstance(paths, list)
        assert isinstance(labels, list)
        assert len(paths) == len(labels)

    def test_foot_dataset_len(self):
        from src.classification.dataset import FootDataset
        # Empty dataset
        ds = FootDataset([], [])
        assert len(ds) == 0


# ── RAG engine tests ──────────────────────────────────────────────────────
class TestRAGEngine:
    def test_chunk_text(self):
        from src.rag.engine import RAGEngine
        text = "A" * 1000
        chunks = RAGEngine._chunk_text(text, chunk_size=200, overlap=50)
        assert len(chunks) > 1
        assert all(len(c) <= 200 for c in chunks)

    def test_load_text_files(self):
        from src.rag.engine import RAGEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "test.txt")
            with open(fpath, "w") as f:
                f.write("test content")
            docs = RAGEngine._load_text_files(tmpdir)
            assert len(docs) == 1
            assert docs[0] == "test content"

    def test_get_rag_advice_fallback(self):
        from src.rag.engine import get_rag_advice
        result = get_rag_advice("grade_1")
        assert "consult" in result.lower() or "knowledge base" in result.lower()


# ── knowledge base tests ──────────────────────────────────────────────────
class TestKnowledgeBase:
    def test_knowledge_base_dir_exists(self):
        from src.config import KNOWLEDGE_BASE_DIR
        assert os.path.isdir(KNOWLEDGE_BASE_DIR)

    def test_knowledge_base_has_documents(self):
        from src.config import KNOWLEDGE_BASE_DIR
        txt_files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith(".txt")]
        assert len(txt_files) >= 1
