# LimbGuard-Cortex Deployment Guide

This guide provides step-by-step instructions for deploying LimbGuard-Cortex to production using popular cloud platforms.

## Overview

LimbGuard-Cortex consists of two components:
1. **Backend**: Python FastAPI server (deploy to Render, Heroku, or Google Cloud Run)
2. **Frontend**: React application (deploy to Vercel or Netlify)

## Prerequisites

- GitHub account with your repository
- Backend hosting account (Render/Heroku/GCP)
- Frontend hosting account (Vercel/Netlify)

## Option 1: Deploy Backend to Render + Frontend to Vercel (Recommended)

### Step 1: Deploy Backend to Render

1. **Sign up** for a free account at [render.com](https://render.com)

2. **Create a new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account and select the `LimbGuard-Cortex` repository
   - Configure the service:
     ```
     Name: limbguard-backend
     Root Directory: backend
     Runtime: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Add Environment Variables**:
   - Click "Environment" tab
   - Add: `FRONTEND_URL` = (leave empty for now, will update after frontend deployment)

4. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL (e.g., `https://limbguard-backend.onrender.com`)

### Step 2: Deploy Frontend to Vercel

1. **Install Vercel CLI** (optional):
   ```bash
   npm install -g vercel
   ```

2. **Deploy via Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New" → "Project"
   - Import your `LimbGuard-Cortex` repository
   - Configure:
     ```
     Framework Preset: Create React App
     Root Directory: frontend
     Build Command: npm run build
     Output Directory: build
     Install Command: npm install
     ```

3. **Add Environment Variable**:
   - In project settings → "Environment Variables"
   - Add: `REACT_APP_API_URL` = `https://limbguard-backend.onrender.com` (your backend URL)

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment
   - Note your frontend URL (e.g., `https://limbguard-cortex.vercel.app`)

### Step 3: Update Backend CORS

1. Go back to Render dashboard
2. Edit your backend service
3. Update environment variable:
   - `FRONTEND_URL` = `https://limbguard-cortex.vercel.app` (your frontend URL)
4. Redeploy the service

### Step 4: Test

Visit your frontend URL and test the application!

## Option 2: Deploy Backend to Heroku + Frontend to Netlify

### Step 1: Deploy Backend to Heroku

1. **Install Heroku CLI**:
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and create app**:
   ```bash
   heroku login
   heroku create limbguard-backend
   ```

3. **Deploy backend**:
   ```bash
   cd backend
   git init
   git add .
   git commit -m "Initial commit"
   heroku git:remote -a limbguard-backend
   git push heroku main
   ```

4. **Set environment variable**:
   ```bash
   heroku config:set FRONTEND_URL=https://your-frontend.netlify.app
   ```

5. **Note your backend URL**: `https://limbguard-backend.herokuapp.com`

### Step 2: Deploy Frontend to Netlify

1. **Build the frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy via Netlify Dashboard**:
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop the `build` folder to Netlify
   - Or use Netlify CLI:
     ```bash
     npm install -g netlify-cli
     netlify deploy --prod --dir=build
     ```

3. **Set environment variable**:
   - In Netlify dashboard → Site settings → Environment variables
   - Add: `REACT_APP_API_URL` = `https://limbguard-backend.herokuapp.com`

4. **Rebuild**:
   - Trigger a redeploy to apply environment variables

### Step 3: Update Backend CORS

Update `FRONTEND_URL` on Heroku:
```bash
heroku config:set FRONTEND_URL=https://your-site.netlify.app
```

## Option 3: Deploy Backend to Google Cloud Run

### Step 1: Set up Google Cloud

1. **Install gcloud CLI**: Follow instructions at https://cloud.google.com/sdk/docs/install

2. **Login and set project**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required APIs**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

### Step 2: Create Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8080

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 3: Deploy to Cloud Run

```bash
cd backend
gcloud run deploy limbguard-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

Note the service URL provided.

### Step 4: Set Environment Variables

```bash
gcloud run services update limbguard-backend \
  --update-env-vars FRONTEND_URL=https://your-frontend.vercel.app
```

## Post-Deployment Checklist

After deploying both backend and frontend:

- [ ] Backend is accessible at its URL
- [ ] Frontend is accessible at its URL
- [ ] Frontend can communicate with backend (test image upload)
- [ ] CORS is properly configured
- [ ] Environment variables are set correctly
- [ ] API documentation is accessible at `<backend-url>/docs`
- [ ] Demo mode works (if no model is trained)

## Optional: Training the Model in Production

If you want to use a trained model instead of demo mode:

1. **Train locally**:
   ```bash
   python -m backend.src.train_classifier --epochs 10
   ```

2. **Upload checkpoint to backend**:
   - For Render: Use persistent disk or object storage
   - For Heroku: Use add-ons like AWS S3
   - For Cloud Run: Use Google Cloud Storage

3. **Restart backend service**

## Environment Variables Reference

### Backend

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FRONTEND_URL` | No | Frontend URL for CORS | `https://app.vercel.app` |
| `PORT` | No | Server port (set by platform) | `8000` |

### Frontend

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REACT_APP_API_URL` | Yes | Backend API URL | `https://api.onrender.com` |

## Troubleshooting

### Backend Issues

**Problem**: Backend won't start
- Check build logs for dependency errors
- Verify Python version is 3.8+
- Ensure all dependencies in requirements.txt are installable

**Problem**: High memory usage
- PyTorch and Transformers are memory-intensive
- Use a paid tier with more RAM (Render: 512MB+ recommended)
- Consider using CPU-only builds to reduce memory

**Problem**: CORS errors
- Verify `FRONTEND_URL` is set correctly
- Ensure no trailing slash in URLs
- Check that frontend URL matches exactly

### Frontend Issues

**Problem**: Frontend can't connect to backend
- Verify `REACT_APP_API_URL` is set
- Check that backend is running and accessible
- Test backend URL directly in browser (`<backend-url>/docs`)

**Problem**: Environment variables not working
- Rebuild/redeploy after setting variables
- Ensure variables start with `REACT_APP_`
- Check that .env is not committed to git

## Monitoring and Logs

### Render
- View logs: Dashboard → Service → Logs tab
- Metrics: Dashboard → Service → Metrics tab

### Heroku
- View logs: `heroku logs --tail -a limbguard-backend`
- Metrics: Dashboard → Resources tab

### Vercel
- View deployment logs: Dashboard → Deployments → Select deployment
- Runtime logs: Dashboard → Logs

### Netlify
- View logs: Dashboard → Deploys → Deploy log

## Scaling Considerations

### Backend
- Start with free tier for testing
- Upgrade to paid tier for production:
  - Render: Starter plan ($7/month)
  - Heroku: Hobby plan ($7/month)
  - Cloud Run: Pay per use (scales automatically)

### Frontend
- Vercel/Netlify free tier is usually sufficient
- Upgrade only if you exceed bandwidth limits

## Security Best Practices

1. **Never commit secrets**: Use environment variables
2. **Use HTTPS**: Ensure both frontend and backend use HTTPS
3. **Limit CORS**: Only allow your frontend domain
4. **Keep dependencies updated**: Regularly update requirements.txt and package.json
5. **Monitor logs**: Watch for unusual activity

## Cost Estimates

### Free Tier (Demo/Testing)
- Backend: Render free tier (750 hours/month)
- Frontend: Vercel/Netlify free tier
- **Total**: $0/month

### Production (Light Usage)
- Backend: Render Starter ($7/month)
- Frontend: Vercel/Netlify free tier
- **Total**: ~$7/month

### Production (Heavy Usage)
- Backend: Render Pro ($25/month) or Cloud Run (pay-per-use)
- Frontend: Vercel Pro ($20/month)
- **Total**: ~$45-100/month

## Support

For deployment issues:
- Check platform-specific documentation
- Review deployment logs
- Open an issue on GitHub
- Consult platform support forums

---

**Next Steps**: After successful deployment, consider setting up:
- Custom domain names
- CI/CD pipelines
- Monitoring and analytics
- Database for user sessions (future enhancement)
