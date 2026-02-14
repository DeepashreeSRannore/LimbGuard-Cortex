"""Retrieval-Augmented Generation engine for LimbGuard-Cortex.

Indexes medical reference documents into a FAISS vector store and retrieves
relevant passages to augment the advice given for abnormal foot images.
"""

import os
import glob
from typing import List, Optional

from backend.src.config import (
    KNOWLEDGE_BASE_DIR,
    FAISS_INDEX_PATH,
    EMBEDDING_MODEL_NAME,
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP,
    RAG_TOP_K,
)


class RAGEngine:
    """Retrieval-Augmented Generation engine backed by FAISS.

    On first use call :meth:`build_index` to process the documents in
    ``knowledge_base/``.  Subsequent calls to :meth:`query` perform a
    similarity search and return the most relevant chunks.
    """

    def __init__(self):
        self._index = None
        self._texts: List[str] = []
        self._embedder = None

    # ── lazy imports (heavy deps) ──────────────────────────────────────
    @staticmethod
    def _import_deps():
        """Import heavy dependencies lazily to keep startup fast."""
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        return SentenceTransformer, faiss, np

    def _get_embedder(self):
        if self._embedder is None:
            SentenceTransformer, _, _ = self._import_deps()
            self._embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        return self._embedder

    # ── document loading ───────────────────────────────────────────────
    @staticmethod
    def _load_text_files(directory: str) -> List[str]:
        """Load all ``.txt`` files under *directory*."""
        docs: List[str] = []
        for path in sorted(glob.glob(os.path.join(directory, "**", "*.txt"), recursive=True)):
            with open(path, encoding="utf-8") as fh:
                docs.append(fh.read())
        return docs

    @staticmethod
    def _load_pdf_files(directory: str) -> List[str]:
        """Load all ``.pdf`` files under *directory* using pypdf."""
        docs: List[str] = []
        for path in sorted(glob.glob(os.path.join(directory, "**", "*.pdf"), recursive=True)):
            try:
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                if text.strip():
                    docs.append(text)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning("Skipping %s: %s", path, exc)
                continue
        return docs

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = RAG_CHUNK_SIZE,
                    overlap: int = RAG_CHUNK_OVERLAP) -> List[str]:
        """Split *text* into overlapping chunks."""
        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return [c.strip() for c in chunks if c.strip()]

    # ── index management ───────────────────────────────────────────────
    def build_index(self, docs_dir: Optional[str] = None):
        """Build (or rebuild) the FAISS index from documents."""
        SentenceTransformer, faiss, np = self._import_deps()

        docs_dir = docs_dir or KNOWLEDGE_BASE_DIR
        raw_docs = self._load_text_files(docs_dir) + self._load_pdf_files(docs_dir)
        if not raw_docs:
            raise FileNotFoundError(
                f"No .txt or .pdf documents found in {docs_dir}. "
                f"Add medical reference documents to the knowledge_base/ "
                f"directory and re-run this command.")

        self._texts = []
        for doc in raw_docs:
            self._texts.extend(self._chunk_text(doc))

        embedder = self._get_embedder()
        embeddings = embedder.encode(self._texts, show_progress_bar=True,
                                     convert_to_numpy=True)
        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatL2(dim)
        self._index.add(embeddings.astype(np.float32))

        # Persist
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(self._index, FAISS_INDEX_PATH)
        texts_path = FAISS_INDEX_PATH + ".texts.txt"
        with open(texts_path, "w", encoding="utf-8") as fh:
            fh.write("\n<SPLIT>\n".join(self._texts))

    def load_index(self):
        """Load a previously-built FAISS index from disk."""
        _, faiss, _ = self._import_deps()

        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(
                f"FAISS index not found at {FAISS_INDEX_PATH}. "
                "Run build_index() first.")
        self._index = faiss.read_index(FAISS_INDEX_PATH)

        texts_path = FAISS_INDEX_PATH + ".texts.txt"
        with open(texts_path, encoding="utf-8") as fh:
            self._texts = fh.read().split("\n<SPLIT>\n")

    # ── query ──────────────────────────────────────────────────────────
    def query(self, question: str, top_k: int = RAG_TOP_K) -> List[str]:
        """Return the *top_k* most relevant document chunks for *question*.

        Loads the index from disk if it has not been loaded yet.
        """
        _, _, np = self._import_deps()

        if self._index is None:
            self.load_index()

        embedder = self._get_embedder()
        q_emb = embedder.encode([question], convert_to_numpy=True).astype(np.float32)
        _, indices = self._index.search(q_emb, top_k)
        return [self._texts[i] for i in indices[0] if 0 <= i < len(self._texts)]


def get_rag_advice(classification: str, rag_engine: Optional[RAGEngine] = None) -> str:
    """Retrieve evidence-based advice for a given gangrene *classification*.

    If no RAG index is available, returns a fallback message.
    """
    if rag_engine is None:
        rag_engine = RAGEngine()

    query_text = (
        f"Medical advice and treatment guidelines for diabetic foot "
        f"gangrene {classification.replace('_', ' ')}. "
        f"What should the patient do? What is the urgency?"
    )

    try:
        chunks = rag_engine.query(query_text)
        context = "\n\n".join(chunks)
        return (
            f"Evidence-based guidance for {classification.replace('_', ' ')}:\n\n"
            f"{context}\n\n"
            "Disclaimer: This information is for reference only. "
            "Always consult a qualified healthcare professional."
        )
    except (FileNotFoundError, ImportError, ModuleNotFoundError):
        return (
            "RAG knowledge base is not available. "
            "Install dependencies (`pip install -r requirements.txt`) and "
            "run `python -m backend.src.rag.engine` to build the index. "
            "In the meantime, please consult a healthcare professional."
        )


if __name__ == "__main__":
    engine = RAGEngine()
    engine.build_index()
    from backend.src.config import FAISS_INDEX_PATH
    print(f"FAISS index built successfully at {FAISS_INDEX_PATH}")
