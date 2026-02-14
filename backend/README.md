# LimbGuard-Cortex Backend

FastAPI backend for diabetic foot assessment, powered by Vision Transformer (ViT) for gangrene classification, NLP for health advice generation, and RAG for evidence-based medical guidance.

## Features

- **REST API**: FastAPI endpoints for image prediction and health checks
- **ViT Classifier**: Fine-tuned Vision Transformer for gangrene grade classification
- **NLP Advice Generator**: Context-aware health recommendations
- **RAG Engine**: FAISS-backed retrieval for evidence-based medical guidance
- **Demo Mode**: Works without trained model for testing
- **CORS Support**: Configured for frontend integration

## Project Structure

```
backend/
├── src/
│   ├── classification/
│   │   ├── model.py              # ViT classifier implementation
│   │   └── dataset.py            # Dataset loader for foot images
│   ├── nlp/
│   │   └── advisor.py            # Health advice generator
│   ├── rag/
│   │   └── engine.py             # RAG engine with FAISS
│   ├── config.py                 # Centralized configuration
│   ├── train_classifier.py       # Training script for ViT model
│   └── app.py                    # Streamlit UI (alternative interface)
├── tests/
│   └── test_pipeline.py          # Unit tests
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for training

## Installation

1. **Install dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

2. **Set up the RAG index** (optional, for evidence-based guidance):

```bash
cd ..  # Go to project root
python -m backend.src.rag.engine
```

This will index the medical documents in `knowledge_base/` into a FAISS vector store.

3. **Train the classifier** (optional, for real predictions):

```bash
python -m backend.src.train_classifier --epochs 10 --batch-size 16
```

The trained model will be saved to `checkpoints/vit_classifier.pt`.

## Running the Backend

### Production Mode (Recommended)

From the project root:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Or from the backend directory:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Development Mode (with auto-reload)

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## API Endpoints

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "LimbGuard-Cortex API is running"
}
```

### `GET /demo`
Check if the server is running in demo mode (no trained model).

**Response:**
```json
{
  "demo_mode": true
}
```

### `POST /predict`
Upload a foot image for gangrene classification.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Image file (JPG, JPEG, PNG)

**Response:**
```json
{
  "success": true,
  "demo_mode": false,
  "classification": "grade_2",
  "display_name": "Grade 2",
  "advice": {
    "status": "Gangrene detected – grade 2.",
    "urgency": "MODERATE",
    "recommended_action": "A deeper wound has been detected...",
    "home_care": "Keep the wound covered with a sterile, moist dressing..."
  },
  "rag_guidance": "Based on clinical guidelines, grade 2 diabetic foot ulcers..."
}
```

## Environment Variables

Set these environment variables for production deployment:

- `FRONTEND_URL`: URL of your frontend (for CORS), e.g., `https://your-frontend.vercel.app`

Example:
```bash
export FRONTEND_URL=https://limbguard-cortex.vercel.app
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Demo Mode

If the trained model checkpoint (`checkpoints/vit_classifier.pt`) is not available, the backend runs in **demo mode**:

- Predictions are simulated based on filename patterns
- All API endpoints work normally
- Frontend displays a demo mode banner

To exit demo mode:
1. Train the classifier (see Installation step 3)
2. Ensure `checkpoints/vit_classifier.pt` exists
3. Restart the backend server

## Training the Classifier

The training script supports the following options:

```bash
python -m backend.src.train_classifier [OPTIONS]

Options:
  --epochs N          Number of training epochs (default: 10)
  --batch-size B      Batch size (default: 16)
  --lr LR            Learning rate (default: 2e-5)
```

Example:
```bash
python -m backend.src.train_classifier --epochs 20 --batch-size 32 --lr 1e-5
```

The script expects images in:
- `Dataset/normal_feet_images/` - Normal foot images
- `Dataset/wound-segmentation/data/Medetec_foot_ulcer_224/` - Wound images

## Testing

Run the test suite:

```bash
cd backend
pytest tests/ -v
```

## Deployment

### Render

1. Create a new **Web Service** on Render
2. Connect your GitHub repository
3. Set the following:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable:
   - `FRONTEND_URL`: Your frontend URL (e.g., from Vercel)

### Heroku

1. Create a `Procfile` in the backend directory:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
heroku create your-app-name
git subtree push --prefix backend heroku main
```

### Google Cloud Run

1. Create a `Dockerfile` in the backend directory:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
gcloud run deploy limbguard-backend --source . --platform managed
```

## Alternative UI (Streamlit)

The backend includes a Streamlit-based UI as an alternative to the React frontend:

```bash
streamlit run backend/src/app.py
```

This provides a simpler interface for local testing and demonstrations.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure you're running commands from the project root and that the project root is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m backend.src.train_classifier
```

### Model Not Loading

If you see "Demo Mode" but want real predictions:
1. Check that `checkpoints/vit_classifier.pt` exists
2. Verify the checkpoint was created successfully during training
3. Check file permissions
4. Restart the backend server

### CORS Errors

If the frontend can't connect to the backend:
1. Ensure `FRONTEND_URL` environment variable is set in production
2. Check that the frontend URL matches exactly (including protocol)
3. Verify no trailing slashes in the URL

### Out of Memory (Training)

If training fails with OOM errors:
1. Reduce batch size: `--batch-size 8`
2. Use CPU instead of GPU (slower but more memory)
3. Reduce image dataset size

## Medical Disclaimer

⚠️ **Important**: This tool is for **educational and research purposes only**. It does not replace professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical decisions.

## License

See the main repository README for license information.
