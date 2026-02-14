import React, { useState, useRef, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Stack,
  Chip,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import ImageIcon from '@mui/icons-material/Image';
import { PredictionResult } from '../types';
import { predictImage } from '../services/api';

interface ImageUploaderProps {
  onPrediction: (result: PredictionResult) => void;
  onLoadingChange: (loading: boolean) => void;
  loading: boolean;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({
  onPrediction,
  onLoadingChange,
  loading,
}) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [demoMode, setDemoMode] = useState<boolean>(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const streamRef = useRef<MediaStream | null>(null);

  const handleImageUpload = async (file: File) => {
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    onLoadingChange(true);
    try {
      const result = await predictImage(file);
      setDemoMode(result.demo_mode);
      onPrediction(result);
    } catch (err: any) {
      setError(err.message || 'Failed to process image. Please try again.');
    } finally {
      onLoadingChange(false);
    }
  };

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        handleImageUpload(acceptedFiles[0]);
      }
    },
    []
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
    },
    multiple: false,
    disabled: loading,
  });

  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
      }
    } catch (err) {
      setError('Failed to access camera. Please check permissions and try again.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const captureImage = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0);
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'camera-capture.jpg', {
              type: 'image/jpeg',
            });
            handleImageUpload(file);
            stopCamera();
          }
        }, 'image/jpeg');
      }
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom align="center">
        Upload or Capture Foot Image
      </Typography>

      {demoMode && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <strong>Demo Mode:</strong> The trained model is not available. 
          Predictions are simulated based on filename patterns.
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!cameraActive && (
        <Box
          {...getRootProps()}
          sx={{
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.400',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            bgcolor: isDragActive ? 'action.hover' : 'background.paper',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'action.hover',
            },
          }}
        >
          <input {...getInputProps()} />
          <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop the image here' : 'Drag & drop an image here'}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            or click to select a file
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Supported formats: JPEG, PNG
          </Typography>
        </Box>
      )}

      {cameraActive && (
        <Box sx={{ textAlign: 'center', mb: 2 }}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{
              width: '100%',
              maxWidth: '500px',
              borderRadius: '8px',
              marginBottom: '16px',
            }}
          />
          <Stack direction="row" spacing={2} justifyContent="center">
            <Button
              variant="contained"
              color="primary"
              onClick={captureImage}
              disabled={loading}
            >
              Capture Image
            </Button>
            <Button variant="outlined" onClick={stopCamera}>
              Cancel
            </Button>
          </Stack>
        </Box>
      )}

      {!cameraActive && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button
            variant="outlined"
            startIcon={<CameraAltIcon />}
            onClick={startCamera}
            disabled={loading}
          >
            Use Camera
          </Button>
        </Box>
      )}

      {preview && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="subtitle1" gutterBottom>
            Preview
          </Typography>
          <Box
            component="img"
            src={preview}
            alt="Preview"
            sx={{
              maxWidth: '100%',
              maxHeight: 300,
              borderRadius: 2,
              boxShadow: 2,
            }}
          />
        </Box>
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <CircularProgress />
          <Typography variant="body1" sx={{ ml: 2 }}>
            Analyzing image...
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default ImageUploader;
