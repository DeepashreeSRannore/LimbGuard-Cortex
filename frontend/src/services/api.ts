import axios from 'axios';
import { PredictionResult, ApiError } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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
      if (!error.response && error.message === 'Network Error') {
        throw new Error(
          `Cannot connect to backend at ${API_BASE_URL}. ` +
          'Please ensure the backend server is running and the REACT_APP_API_URL environment variable is set correctly.'
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
