# LimbGuard-Cortex

AI-powered diabetic foot assessment pipeline that combines a **Vision Transformer (ViT)** for gangrene grade classification with **NLP-based health advice** and **Retrieval-Augmented Generation (RAG)** for evidence-based medical guidance.

## Project Structure

```
LimbGuard-Cortex/
├── Dataset/                         # Existing image datasets
│   ├── normal_feet_images/          # Healthy foot images
│   └── wound-segmentation/          # Wound segmentation data (Medetec)
├── frontend/                        # React frontend application (NEW!)
│   ├── api/                         # FastAPI backend server
│   ├── src/                         # React components and services
│   ├── public/                      # Static assets
│   ├── start.sh                     # Easy startup script
│   └── README.md                    # Frontend documentation
├── knowledge_base/                  # Medical reference documents for RAG
│   ├── diabetic_foot_guidelines.txt
│   └── wound_assessment_reference.txt
├── src/
│   ├── config.py                    # Centralized configuration
│   ├── classification/
│   │   ├── model.py                 # ViT-based gangrene classifier
│   │   └── dataset.py               # Dataset loader for foot images
│   ├── nlp/
│   │   └── advisor.py               # Health advice generator (normal & graded)
│   ├── rag/
│   │   └── engine.py                # FAISS-backed RAG for evidence-based advice
│   ├── train_classifier.py          # Training pipeline for the ViT model
│   └── app.py                       # Streamlit web application
├── tests/
│   └── test_pipeline.py             # Unit tests
├── requirements.txt
└── README.md
```

## Components

### A. Image Classification (Vision Transformer)
- Pre-trained `google/vit-base-patch16-224-in21k` fine-tuned on the LimbGuard dataset
- Classifies foot images into: **normal**, **grade 1–4** gangrene
- Located in `src/classification/`

### B. NLP Health Advice
- For **normal** results: generates preventive advice (blood sugar management, skin care, footwear, scheduling)
- For **abnormal** results: provides urgency level and recommended actions
- Located in `src/nlp/`

### C. Retrieval-Augmented Generation (RAG)
- FAISS vector store indexes medical reference documents from `knowledge_base/`
- Sentence-Transformer embeddings (`all-MiniLM-L6-v2`) for semantic search
- Retrieves evidence-based guidance for abnormal classifications
- Located in `src/rag/`

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Build the RAG Index

```bash
python -m src.rag.engine
```

### 3. Train the Classifier

```bash
python -m src.train_classifier --epochs 10 --batch-size 16
```

### 4. Launch the Web App

**Option A: Modern React Frontend (Recommended)**

```bash
cd frontend
./start.sh  # Starts both backend API and React frontend
```

Then visit `http://localhost:3000` in your browser.

**Option B: Streamlit App**

```bash
streamlit run src/app.py
```

The app includes a **Demo mode** (enabled by default) to explore the advice
system without a trained model.

## Training Pipeline

| Stage | Script | Description |
|-------|--------|-------------|
| Image classification | `python -m src.train_classifier` | Fine-tunes ViT on the dataset |
| RAG indexing | `python -m src.rag.engine` | Builds FAISS index from knowledge base |

## Testing

```bash
pytest tests/ -v
```

## Dataset

The project uses images from:
- **normal_feet_images/** – healthy foot photographs
- **Medetec_foot_ulcer_224/** – foot ulcer images (224×224) from AZH Wound & Vascular Center

Images are automatically discovered and labelled by the dataset loader in
`src/classification/dataset.py`.

## Disclaimer

This tool is for **educational and research purposes only**. It does not
replace professional medical advice, diagnosis, or treatment. Always consult
a qualified healthcare provider for medical decisions.