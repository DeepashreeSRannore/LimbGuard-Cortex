import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  Button,
  Divider,
  Alert,
  Stack,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { PredictionResult } from '../types';

interface ResultsPanelProps {
  result: PredictionResult;
  onReset: () => void;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ result, onReset }) => {
  const isNormal = result.classification === 'normal';

  const getSeverityIcon = () => {
    if (isNormal) return <CheckCircleIcon />;
    if (result.classification === 'grade_1' || result.classification === 'grade_2')
      return <WarningIcon />;
    return <ErrorIcon />;
  };

  const getUrgencyColor = (urgency?: string) => {
    if (!urgency) return 'default';
    if (urgency.includes('CRITICAL')) return 'error';
    if (urgency.includes('HIGH')) return 'error';
    if (urgency.includes('MODERATE')) return 'warning';
    return 'info';
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Assessment Results</Typography>
          <Button
            variant="outlined"
            startIcon={<RestartAltIcon />}
            onClick={onReset}
          >
            New Assessment
          </Button>
        </Box>

        {result.demo_mode && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <strong>Demo Mode Active:</strong> These results are simulated. 
            Train and deploy the model for real predictions.
          </Alert>
        )}

        {/* Classification Result */}
        <Card
          sx={{
            mb: 3,
            bgcolor: isNormal ? 'success.light' : 'error.light',
            color: isNormal ? 'success.contrastText' : 'error.contrastText',
          }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              {getSeverityIcon()}
              <Typography variant="h6" sx={{ ml: 1 }}>
                Classification: {result.display_name}
              </Typography>
            </Box>
            {result.advice.urgency && (
              <Chip
                label={`Urgency: ${result.advice.urgency}`}
                color={getUrgencyColor(result.advice.urgency)}
                sx={{ mt: 1 }}
              />
            )}
          </CardContent>
        </Card>

        {/* Status */}
        {result.advice.status && (
          <Alert
            severity={isNormal ? 'success' : 'warning'}
            icon={isNormal ? <CheckCircleIcon /> : <WarningIcon />}
            sx={{ mb: 3 }}
          >
            <Typography variant="body1">
              <strong>Status:</strong> {result.advice.status}
            </Typography>
          </Alert>
        )}

        {/* Health Advice */}
        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Health Advice
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Stack spacing={2}>
          {/* For normal results, show preventive care */}
          {isNormal && (
            <>
              {result.advice.sugar_maintenance && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary" gutterBottom>
                      Blood Sugar Maintenance
                    </Typography>
                    <Typography variant="body2">
                      {result.advice.sugar_maintenance}
                    </Typography>
                  </CardContent>
                </Card>
              )}

              {result.advice.skin_care && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary" gutterBottom>
                      Skin Care
                    </Typography>
                    <Typography variant="body2">
                      {result.advice.skin_care}
                    </Typography>
                  </CardContent>
                </Card>
              )}

              {result.advice.footwear && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary" gutterBottom>
                      Footwear Recommendations
                    </Typography>
                    <Typography variant="body2">
                      {result.advice.footwear}
                    </Typography>
                  </CardContent>
                </Card>
              )}

              {result.advice.scheduling && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary" gutterBottom>
                      Follow-up Scheduling
                    </Typography>
                    <Typography variant="body2">
                      {result.advice.scheduling}
                    </Typography>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {/* For abnormal results, show action items */}
          {!isNormal && (
            <>
              {result.advice.recommended_action && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" color="error" gutterBottom>
                      ⚠️ Recommended Action
                    </Typography>
                    <Typography variant="body2">
                      {result.advice.recommended_action}
                    </Typography>
                  </CardContent>
                </Card>
              )}

              {result.advice.home_care && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary" gutterBottom>
                      Home Care Instructions
                    </Typography>
                    <Typography variant="body2">
                      {result.advice.home_care}
                    </Typography>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </Stack>

        {/* RAG Guidance for abnormal results */}
        {result.rag_guidance && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              📚 Evidence-Based Guidance
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Card>
              <CardContent>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                  {result.rag_guidance}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        )}

        {/* Safety Notice */}
        <Alert severity="warning" sx={{ mt: 3 }}>
          <Typography variant="body2">
            <strong>Important:</strong> This assessment is not a substitute for professional medical advice.
            {!isNormal && (
              <> Please consult with a healthcare provider immediately, especially if you notice any worsening symptoms.</>
            )}
            {isNormal && (
              <> Continue regular foot examinations and maintain good diabetic foot care practices.</>
            )}
          </Typography>
        </Alert>
      </Paper>
    </Box>
  );
};

export default ResultsPanel;
