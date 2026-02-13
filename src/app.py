"""Streamlit application for LimbGuard-Cortex.

Provides a web interface where users can upload foot images, receive a
gangrene grade classification, and get evidence-based medical advice.

Usage::

    streamlit run src/app.py
"""

import os
import sys

import streamlit as st
from PIL import Image

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import CLASS_NAMES, CHECKPOINT_DIR  # noqa: E402
from src.nlp.advisor import generate_advice  # noqa: E402
from src.rag.engine import get_rag_advice, RAGEngine  # noqa: E402

# ── page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="LimbGuard-Cortex", page_icon="🦶", layout="centered")

st.title("🦶 LimbGuard-Cortex")
st.markdown(
    "Upload a foot image to receive a gangrene grade assessment and "
    "personalised health advice."
)


# ── helpers ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_classifier():
    """Load the trained ViT classifier (returns *None* if unavailable)."""
    try:
        import torch
        from src.classification.model import GangreneClassifier
        ckpt = os.path.join(CHECKPOINT_DIR, "vit_classifier.pt")
        if not os.path.exists(ckpt):
            return None
        model = GangreneClassifier()
        model.load(ckpt)
        return model
    except Exception:
        return None


@st.cache_resource
def load_rag_engine():
    """Load the RAG engine (returns *None* if index missing)."""
    try:
        engine = RAGEngine()
        engine.load_index()
        return engine
    except Exception:
        return None


def classify_image(image: Image.Image, model) -> str:
    """Run the ViT classifier on *image* and return the predicted class."""
    import torch
    from torchvision import transforms
    from src.config import IMAGE_SIZE

    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    tensor = transform(image.convert("RGB"))
    return model.predict(tensor)


# ── sidebar ────────────────────────────────────────────────────────────────
st.sidebar.header("About")
st.sidebar.info(
    "**LimbGuard-Cortex** uses a Vision Transformer to classify foot images "
    "and provides evidence-based medical guidance.\n\n"
    "⚠️ This tool is for **educational purposes only** and does not replace "
    "professional medical advice."
)

# Demo mode selector
demo_mode = st.sidebar.checkbox("Demo mode (simulate classification)", value=True)
if demo_mode:
    demo_class = st.sidebar.selectbox("Simulated classification", CLASS_NAMES)

# ── main area ──────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload a foot image", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded image", use_container_width=True)

    with st.spinner("Analysing image…"):
        if demo_mode:
            classification = demo_class
        else:
            model = load_classifier()
            if model is None:
                st.error(
                    "Trained model not found. Train the classifier first with "
                    "`python -m src.train_classifier`, or enable **Demo mode** "
                    "in the sidebar."
                )
                st.stop()
            classification = classify_image(image, model)

    # ── results ────────────────────────────────────────────────────────
    st.subheader("Classification Result")
    color = "green" if classification == "normal" else "red"
    st.markdown(f"**Predicted grade:** :{color}[{classification.replace('_', ' ').title()}]")

    st.subheader("Health Advice")
    advice = generate_advice(classification)
    for key, value in advice.items():
        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

    # RAG-augmented advice for abnormal results
    if classification != "normal":
        st.subheader("📚 Evidence-Based Guidance (RAG)")
        rag_engine = load_rag_engine()
        rag_text = get_rag_advice(classification, rag_engine)
        st.markdown(rag_text)
