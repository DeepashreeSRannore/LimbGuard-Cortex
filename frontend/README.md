# LimbGuard-Cortex Frontend

A modern, responsive React frontend application for the LimbGuard-Cortex diabetic foot assessment system. This application provides an intuitive interface for users to upload or capture foot images and receive AI-powered gangrene grade assessments with personalized health advice.

## Features

- **Modern UI**: Built with Material-UI (MUI) for a professional, responsive design
- **Image Upload**: Drag-and-drop or click-to-upload interface
- **Camera Capture**: Direct camera access for real-time image capture
- **Real-time Predictions**: Sends images to the backend API and displays results
- **Comprehensive Advice**: 
  - For healthy feet: Preventive care tips (blood sugar management, skin care, footwear, scheduling)
  - For detected issues: Urgency level, recommended actions, and home care instructions
- **Evidence-Based Guidance**: RAG-powered medical guidance for abnormal classifications
- **Error Handling**: Robust error boundary and user feedback
- **Demo Mode**: Works with or without a trained model

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components and theming
- **Axios** for API communication
- **React Dropzone** for file uploads
- **FastAPI** backend server (included in `api/` directory)

## Project Structure

```
frontend/
├── api/                          # Backend API server
│   ├── server.py                 # FastAPI application
│   └── requirements.txt          # Python dependencies
├── public/                       # Static assets
├── src/
│   ├── components/               # React components
│   │   ├── ErrorBoundary.tsx     # Error handling component
│   │   ├── Header.tsx            # Application header
│   │   ├── ImageUploader.tsx     # Image upload/capture component
│   │   └── ResultsPanel.tsx      # Results display component
│   ├── services/                 # API services
│   │   └── api.ts                # Backend API client
│   ├── App.tsx                   # Main application component
│   ├── types.ts                  # TypeScript type definitions
│   └── index.tsx                 # Application entry point
├── .env                          # Environment variables
├── .env.local.example            # Example environment config
├── package.json                  # Node.js dependencies
└── README.md                     # This file
```

## Prerequisites

- **Node.js** 18.x or higher
- **Python** 3.8 or higher (for the API server)
- **npm** or **yarn** package manager

## Installation

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Install Backend Dependencies

```bash
cd frontend/api
pip install -r requirements.txt
```

The backend also requires the main project dependencies:

```bash
cd ../..  # Return to project root
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Copy the example environment file and configure as needed:

```bash
cd frontend
cp .env.local.example .env.local
```

Edit `.env.local` to set your API URL (default is `http://localhost:8000`):

```env
REACT_APP_API_URL=http://localhost:8000
```

## Running the Application

You need to run both the backend API server and the frontend development server.

### 1. Start the Backend API Server

In one terminal:

```bash
cd frontend/api
python server.py
```

Or using uvicorn directly:

```bash
cd frontend/api
uvicorn server:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

You can verify it's running by visiting `http://localhost:8000/docs` to see the interactive API documentation.

### 2. Start the Frontend Development Server

In another terminal:

```bash
cd frontend
npm start
```

The application will automatically open in your browser at `http://localhost:3000`

## Usage

1. **Upload an Image**: 
   - Drag and drop a foot image onto the upload area, or
   - Click to browse and select an image from your device

2. **Capture an Image**: 
   - Click the "Use Camera" button
   - Allow camera permissions when prompted
   - Click "Capture Image" when ready

3. **View Results**: 
   - The application will send the image to the backend API
   - Classification results will be displayed with a color-coded severity indicator
   - Health advice will be shown based on the classification:
     - **Normal**: Preventive care tips and scheduling recommendations
     - **Grade 1-4**: Urgency level, recommended actions, and home care instructions
   - Evidence-based guidance (RAG) will appear for abnormal classifications

4. **Start New Assessment**: 
   - Click "New Assessment" to reset and analyze another image

## Demo Mode

If the trained model is not available, the application runs in **Demo Mode**:
- Predictions are simulated based on filename patterns
- An info banner indicates demo mode is active
- All UI features work normally for testing purposes

To exit demo mode:
1. Train the classifier: `python -m src.train_classifier --epochs 10`
2. Ensure the checkpoint exists at `checkpoints/vit_classifier.pt`
3. Restart the backend server

## Building for Production

Create an optimized production build:

```bash
cd frontend
npm run build
```

The build artifacts will be in the `build/` directory, ready to be deployed to any static hosting service.

To serve the production build locally:

```bash
npm install -g serve
serve -s build -l 3000
```

## Deployment

### Vercel (Recommended)

**Deploy via Vercel Dashboard:**

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
5. Add environment variable:
   - `REACT_APP_API_URL` = Your backend URL (e.g., `https://limbguard-backend.onrender.com`)
6. Click "Deploy"

**Deploy via Vercel CLI:**

```bash
npm install -g vercel
cd frontend
vercel --prod
```

### Netlify

1. Build the application:
   ```bash
   npm run build
   ```

2. Deploy via Netlify Dashboard:
   - Drag and drop the `build/` folder to Netlify
   - Or connect your GitHub repository

3. Set environment variable in Netlify dashboard:
   - `REACT_APP_API_URL` = Your backend URL

The `netlify.toml` configuration file is already included in the frontend directory.

### Environment Variables for Production

**Recommended: Set in Hosting Platform Dashboard**

For Vercel:
1. Go to project settings → Environment Variables
2. Add `REACT_APP_API_URL` = `https://your-backend-url.onrender.com`
3. Apply to Production, Preview, and Development

For Netlify:
1. Go to Site settings → Environment variables
2. Add `REACT_APP_API_URL` = `https://your-backend-url.onrender.com`

**Alternative: Local Production Build Testing**

If you need to test a production build locally, create `.env.production.local`:

```env
REACT_APP_API_URL=https://your-backend-url.onrender.com
NODE_ENV=production
```

Note: This file is only for local testing and should not be committed (it's in `.gitignore`).

## API Endpoints

The backend API provides the following endpoints:

- `GET /`: Health check
- `GET /demo`: Check if running in demo mode
- `POST /predict`: Upload image for prediction
  - Accepts: multipart/form-data with image file
  - Returns: Classification, advice, and RAG guidance

See the API documentation at `http://localhost:8000/docs` when the server is running.

## Error Handling

The application includes comprehensive error handling:

- **Error Boundary**: Catches React component errors and displays a friendly error page
- **API Errors**: Network and server errors are caught and displayed to the user
- **Camera Errors**: Permission and access errors are handled gracefully
- **File Validation**: Only image files are accepted for upload

## Browser Support

The application supports all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

Camera capture requires HTTPS in production (works on localhost in development).

## Troubleshooting

### Backend Connection Issues

If you see "Failed to connect to the prediction service":
1. Ensure the backend server is running on port 8000
2. Check that REACT_APP_API_URL in `.env` is correct
3. Verify no firewall is blocking port 8000

### Camera Not Working

If the camera doesn't activate:
1. Ensure browser permissions are granted for camera access
2. Use HTTPS in production (localhost works in development)
3. Check that your device has a camera available

### Model Not Loading

If you see "Demo Mode" but want real predictions:
1. Train the model: `python -m src.train_classifier --epochs 10`
2. Build the RAG index: `python -m src.rag.engine`
3. Restart the backend server

## Development

### Running Tests

```bash
npm test
```

### Linting

```bash
npm run lint
```

### Code Formatting

The project uses ESLint and TypeScript for code quality.

## Available Scripts (Create React App)

### `npm start`

Runs the app in the development mode at [http://localhost:3000](http://localhost:3000).

### `npm test`

Launches the test runner in interactive watch mode.

### `npm run build`

Builds the app for production to the `build` folder.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

## Security Considerations

- Images are processed locally and sent only to your backend server
- No data is stored or transmitted to third-party services
- CORS is configured to accept requests only from the frontend domain
- Camera access requires user permission

## Medical Disclaimer

⚠️ **Important**: This tool is for **educational and research purposes only**. It does not replace professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical decisions.

## Learn More

- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)
- [Material-UI documentation](https://mui.com/)
