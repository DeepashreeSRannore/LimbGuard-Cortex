import React from 'react';
import { Box, Typography, Alert } from '@mui/material';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';

const Header: React.FC = () => {
  return (
    <Box sx={{ mb: 4, textAlign: 'center' }}>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mb: 2 }}>
        <LocalHospitalIcon sx={{ fontSize: 48, color: 'primary.main', mr: 2 }} />
        <Typography variant="h3" component="h1" color="primary">
          LimbGuard-Cortex
        </Typography>
      </Box>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        AI-Powered Diabetic Foot Assessment
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto', mb: 2 }}>
        Upload or capture a foot image to receive a gangrene grade assessment and personalized health advice
      </Typography>
      <Alert severity="warning" sx={{ maxWidth: 800, mx: 'auto' }}>
        <strong>Medical Disclaimer:</strong> This tool is for educational and research purposes only.
        It does not replace professional medical advice, diagnosis, or treatment. 
        Always consult a qualified healthcare provider for medical decisions.
      </Alert>
    </Box>
  );
};

export default Header;
