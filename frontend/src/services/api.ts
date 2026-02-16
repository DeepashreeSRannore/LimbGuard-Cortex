import axios from 'axios';
import { PredictionResult, ApiError } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  // Render free tier can take 50+ seconds to wake from cold start
  timeout: 60000,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export const predictImage = async (file: File): Promise<PredictionResult> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<PredictionResult>('/predict', formData);
    return response.data;
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (!error.response) {
        // No response at all — network-level failure
        const isLocalhost = API_BASE_URL.includes('localhost') || API_BASE_URL.includes('127.0.0.1');
        if (isLocalhost && process.env.NODE_ENV === 'production') {
          throw new Error(
            'Backend API URL is not configured for production. ' +
            'Set the REACT_APP_API_URL environment variable in your Vercel dashboard ' +
            'to your Render backend URL (e.g. https://your-app.onrender.com) and redeploy.'
          );
        }
        throw new Error(
          `Cannot connect to backend at ${API_BASE_URL}. ` +
          'The server may be starting up (Render free tier can take up to 60 seconds). ' +
          'Please wait a moment and try again.'
        );
      }
      const apiError = error.response?.data as ApiError;
      throw new Error(
        apiError?.detail || 
        error.message || 
        'Failed to connect to the prediction service.'
      );
    }
    throw new Error('An unexpected error occurred while processing the image.');
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/');
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

export const checkDemoMode = async (): Promise<boolean> => {
  try {
    const response = await api.get('/demo');
    return response.data.demo_mode;
  } catch (error) {
    return true;
  }
};
