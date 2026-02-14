"""FastAPI backend for LimbGuard-Cortex predictions.

This server provides a REST API endpoint for foot image classification.
It wraps the existing ViT-based gangrene classifier and NLP advice generator.

Usage:
    uvicorn backend.main:app --reload --port 8000
    
    Or from the backend directory:
    uvicorn main:app --reload --port 8000
"""

import os
import sys
import io
import logging
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
from torchvision import transforms

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.src.config import CLASS_NAMES, CHECKPOINT_DIR, IMAGE_SIZE
from backend.src.nlp.advisor import generate_advice
from backend.src.rag.engine import get_rag_advice, RAGEngine

app = FastAPI(
    title="LimbGuard-Cortex API",
    description="Diabetic foot assessment API",
    version="1.0.0"
)

# Enable CORS for React frontend
# Allow localhost for development and production domains
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production origins from environment variable
production_origin = os.getenv("FRONTEND_URL")
if production_origin:
    allowed_origins.append(production_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for model and RAG engine
_classifier = None
_rag_engine = None


def load_classifier():
    """Load the trained ViT classifier."""
    global _classifier
    if _classifier is not None:
        return _classifier
    
    try:
        from backend.src.classification.model import GangreneClassifier
        ckpt = os.path.join(CHECKPOINT_DIR, "vit_classifier.pt")
        if not os.path.exists(ckpt):
            return None
        model = GangreneClassifier()
        model.load(ckpt)
        _classifier = model
        logger.info("Classifier loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading classifier: {e}")
        return None


def load_rag_engine():
    """Load the RAG engine."""
    global _rag_engine
    if _rag_engine is not None:
        return _rag_engine
    
    try:
        engine = RAGEngine()
        engine.load_index()
        _rag_engine = engine
        logger.info("RAG engine loaded successfully")
        return engine
    except Exception as e:
        logger.error(f"Error loading RAG engine: {e}")
        return None


def classify_image(image: Image.Image, model) -> str:
    """Run the ViT classifier on the image and return predicted class."""
    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    tensor = transform(image.convert("RGB"))
    return model.predict(tensor)


def get_demo_prediction(filename: str) -> str:
    """Return a simulated prediction based on filename patterns."""
    filename_lower = filename.lower()
    if "normal" in filename_lower or "healthy" in filename_lower:
        return "normal"
    elif "grade_4" in filename_lower or "severe" in filename_lower:
        return "grade_4"
    elif "grade_3" in filename_lower:
        return "grade_3"
    elif "grade_2" in filename_lower:
        return "grade_2"
    elif "grade_1" in filename_lower or "wound" in filename_lower:
        return "grade_1"
    # Default to normal for demo
    return "normal"


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "LimbGuard-Cortex API is running"}


@app.get("/demo")
async def demo_status():
    """Check if we're running in demo mode."""
    model = load_classifier()
    return {"demo_mode": model is None}


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Predict gangrene grade from an uploaded foot image.
    
    Returns:
        dict: Contains classification, advice, and RAG guidance
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and parse image
        contents = await file.read()
        try:
            image = Image.open(io.BytesIO(contents))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Try to load model, fall back to demo mode if not available
        model = load_classifier()
        demo_mode = model is None
        
        if demo_mode:
            # Demo mode: simulate classification based on filename
            classification = get_demo_prediction(file.filename or "")
        else:
            # Real mode: use trained model
            classification = classify_image(image, model)
        
        # Generate advice
        advice = generate_advice(classification)
        
        # Get RAG-based guidance for abnormal results
        rag_guidance = None
        if classification != "normal":
            rag_engine = load_rag_engine()
            if rag_engine is not None:
                rag_guidance = get_rag_advice(classification, rag_engine)
        
        return {
            "success": True,
            "demo_mode": demo_mode,
            "classification": classification,
            "display_name": classification.replace("_", " ").title(),
            "advice": advice,
            "rag_guidance": rag_guidance,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
