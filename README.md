# LimbGuard-Cortex

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered diabetic foot assessment platform combining **Vision Transformer (ViT)** for gangrene classification, **NLP-based health advice**, and **Retrieval-Augmented Generation (RAG)** for evidence-based medical guidance.

> **Deployment Ready:** This repository is structured for seamless deployment to **Render** (backend) and **Vercel** (frontend). See the [Deployment](#-deployment) section for step-by-step instructions.

## 🚀 Quick Start

### Prerequisites
- **Backend**: Python 3.8+
- **Frontend**: Node.js 18+
- **Package Managers**: pip, npm

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/DeepashreeSRannore/LimbGuard-Cortex.git
cd LimbGuard-Cortex
```

2. **Set up the backend:**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

3. **Set up the frontend:**
```bash
cd frontend
npm install
cd ..
```

### Running Locally

**Terminal 1 - Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Visit `http://localhost:3000` in your browser.

## 📁 Repository Structure

This repository is organized for deployment to cloud platforms:

```
LimbGuard-Cortex/
├── backend/                      # FastAPI backend (Deploy to Render)
│   ├── src/
│   │   ├── classification/       # ViT-based classifier
│   │   ├── nlp/                  # Health advice generator
│   │   ├── rag/                  # RAG engine with FAISS
│   │   ├── config.py             # Configuration
│   │   ├── train_classifier.py   # Training script
│   │   └── app.py                # Streamlit UI (alternative)
│   ├── tests/                    # Backend tests
│   ├── main.py                   # FastAPI app entry point
│   ├── requirements.txt          # Python dependencies
│   ├── Procfile                  # Process configuration
│   └── README.md                 # Backend documentation
├── frontend/                     # React frontend (Deploy to Vercel)
│   ├── src/
│   │   ├── components/           # React components
│   │   └── services/             # API client
│   ├── public/                   # Static assets
│   ├── package.json              # Node.js dependencies
│   ├── vercel.json               # Vercel configuration
│   ├── .env.local.example        # Development environment template
│   ├── .env.production.example   # Production environment template
│   └── README.md                 # Frontend documentation
├── Dataset/                      # Training data (optional, not in git)
│   ├── normal_feet_images/       # Healthy foot images
│   └── wound-segmentation/       # Wound/ulcer images
├── knowledge_base/               # Medical reference documents for RAG
│   ├── diabetic_foot_guidelines.txt
│   └── wound_assessment_reference.txt
├── README.md                     # Main documentation (this file)
└── DEPLOYMENT.md                 # Detailed deployment guide
```

## 🎯 Features

### Backend (FastAPI + Python)
- **REST API** for image classification
- **Vision Transformer (ViT)** fine-tuned on diabetic foot images
- **NLP Advice Generator** providing context-aware health recommendations
- **RAG Engine** with FAISS for evidence-based medical guidance
- **Demo Mode** for testing without trained model
- **Streamlit UI** as alternative interface

### Frontend (React + TypeScript)
- **Modern Material-UI** design
- **Drag-and-drop** image upload
- **Camera capture** for real-time image capture
- **Real-time predictions** with health advice
- **Error handling** and demo mode support
- **Responsive design** for mobile and desktop

## 🔧 Training the Model

### 1. Build the RAG Index

```bash
python -m backend.src.rag.engine
```

This indexes medical documents from `knowledge_base/` into a FAISS vector store.

### 2. Train the Classifier

```bash
python -m backend.src.train_classifier --epochs 10 --batch-size 16
```

The model expects images in:
- `Dataset/normal_feet_images/` - Normal foot images
- `Dataset/wound-segmentation/data/Medetec_foot_ulcer_224/` - Wound images

Training creates `checkpoints/vit_classifier.pt`.

## 🧪 Testing

**Backend:**
```bash
cd backend
pytest tests/ -v
```

**Frontend:**
```bash
cd frontend
npm test
```

## 🌐 Deployment

This repository is structured for easy deployment to Render (backend) and Vercel (frontend).

### Backend Deployment (Render)

1. **Create a Web Service** on [Render](https://render.com)
2. **Connect your GitHub repository** and select this repo
3. **Configure the service** with these exact settings:
   - **Name**: `limbguard-backend` (or your preferred name)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free tier (or higher for production)

4. **Add Environment Variables** in the Render dashboard:
   - `FRONTEND_URL` = (Your frontend URL, e.g., `https://limbguard.vercel.app`)
   - Note: Leave empty initially, update after frontend deployment

5. **Deploy** and wait for the build to complete
6. **Copy your backend URL** (e.g., `https://limbguard-backend.onrender.com`)

**Verified Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```
This command runs from the `backend/` directory and works with Render's automatic port binding.

**Alternative deployment options:** Heroku, Google Cloud Run, AWS - see [DEPLOYMENT.md](DEPLOYMENT.md)

### Frontend Deployment (Vercel)

**Option 1: Deploy via Vercel Dashboard (Recommended)**

1. **Go to** [vercel.com](https://vercel.com) and sign in
2. **Click** "Add New" → "Project"
3. **Import** your GitHub repository
4. **Configure with these exact settings:**
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

5. **Add Environment Variable** before deploying:
   - Go to "Environment Variables" section
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.onrender.com`
   - Apply to: Production, Preview, and Development

6. **Click "Deploy"** and wait for completion
7. **Copy your frontend URL** (e.g., `https://limbguard-cortex.vercel.app`)

**Option 2: Deploy via Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to repository root
cd LimbGuard-Cortex

# Deploy (follow prompts to set root directory to 'frontend')
vercel

# For production
vercel --prod
```

**Verified Build Settings:**
- Root Directory: `frontend`
- Build Command: `npm run build`  
- Output Directory: `build`

**Alternative: Deploy to Netlify** - See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions

### Post-Deployment Configuration

After deploying both services:

1. **Update Backend CORS:**
   - Go to your Render dashboard
   - Navigate to your backend service
   - Update environment variable: `FRONTEND_URL` = `https://your-frontend-url.vercel.app`
   - Save and redeploy if needed

2. **Verify Frontend API Connection:**
   - Ensure `REACT_APP_API_URL` in Vercel matches your backend URL
   - Redeploy frontend if you need to update this variable

### Deployment Checklist

- [ ] Backend deployed to Render with correct root directory (`backend`)
- [ ] Backend start command verified: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Backend URL obtained (e.g., `https://limbguard-backend.onrender.com`)
- [ ] Frontend deployed to Vercel with correct root directory (`frontend`)
- [ ] Frontend build command verified: `npm run build`
- [ ] Frontend output directory verified: `build`
- [ ] Environment variable set on backend: `FRONTEND_URL`
- [ ] Environment variable set on frontend: `REACT_APP_API_URL`
- [ ] Test deployed app end-to-end (upload an image and verify response)
- [ ] (Optional) Train and upload model checkpoint to backend
- [ ] (Optional) Build RAG index on backend

## ⚙️ Environment Variables

### Backend
```bash
# Optional: Frontend URL for CORS (production only)
FRONTEND_URL=https://your-frontend-url.vercel.app
```

### Frontend
```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8000  # Development
REACT_APP_API_URL=https://your-backend-url.onrender.com  # Production
```

## 📊 API Endpoints

### `GET /`
Health check

### `GET /demo`
Check if running in demo mode

### `POST /predict`
Upload image for prediction

**Request:** `multipart/form-data` with image file

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
    "recommended_action": "...",
    "home_care": "..."
  },
  "rag_guidance": "Based on clinical guidelines..."
}
```

Full API documentation: `http://localhost:8000/docs` (when backend is running)

## 🎨 Classification Grades

The model classifies foot images into 5 categories:

- **Normal**: Healthy foot, no signs of gangrene
- **Grade 1**: Superficial ulcer
- **Grade 2**: Deep ulcer, may involve tendon/bone
- **Grade 3**: Deep ulcer with abscess or osteomyelitis
- **Grade 4**: Gangrene of forefoot or limited area

## 💡 Demo Mode

If no trained model is available, the app runs in **demo mode**:
- Predictions are simulated based on filename patterns
- All features work for testing
- A banner indicates demo mode is active

**To exit demo mode:**
1. Train the classifier (see Training the Model)
2. Ensure `checkpoints/vit_classifier.pt` exists
3. Restart the backend server

## 🔍 Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed: `python --version`
- Install dependencies: `pip install -r backend/requirements.txt`
- Check port 8000 is not in use: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows)

### Frontend won't start
- Ensure Node.js 18+ is installed: `node --version`
- Install dependencies: `npm install` in frontend directory
- Check port 3000 is not in use

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check `REACT_APP_API_URL` in frontend/.env
- Verify CORS settings in backend/main.py
- Check browser console for errors

### Model training fails
- **Out of memory**: Reduce batch size (`--batch-size 8`)
- **No images found**: Ensure Dataset/ folder contains images
- **CUDA error**: Use CPU by setting `CUDA_VISIBLE_DEVICES=""`

### Camera not working
- **Permissions**: Allow camera access in browser
- **HTTPS required**: Camera works on localhost or HTTPS only
- **No camera**: Use file upload instead

## 🏥 Medical Disclaimer

⚠️ **IMPORTANT**: This tool is for **educational and research purposes only**. It does not replace professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical decisions.

## �� Technology Stack

**Backend:**
- FastAPI - Web framework
- PyTorch - Deep learning
- Transformers (Hugging Face) - ViT model
- FAISS - Vector search for RAG
- Sentence Transformers - Embeddings
- Streamlit - Alternative UI

**Frontend:**
- React 19 - UI framework
- TypeScript - Type safety
- Material-UI (MUI) - Component library
- Axios - HTTP client
- React Dropzone - File upload

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Dataset**: Medetec Wound Database & AZH Wound & Vascular Center
- **Models**: Google ViT, Hugging Face Transformers
- **Medical Guidelines**: Referenced in knowledge_base/

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check documentation in backend/README.md and frontend/README.md
- Review the troubleshooting section above

---

**Built with ❤️ for diabetic foot care research and education**
