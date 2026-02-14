import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container } from '@mui/material';
import { ErrorBoundary } from './components/ErrorBoundary';
import Header from './components/Header';
import ImageUploader from './components/ImageUploader';
import ResultsPanel from './components/ResultsPanel';
import { PredictionResult } from './types';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: '#ff9800',
    },
    error: {
      main: '#f44336',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
});

function App() {
  const [result, setResult] = React.useState<PredictionResult | null>(null);
  const [loading, setLoading] = React.useState(false);

  const handlePrediction = (predictionResult: PredictionResult) => {
    setResult(predictionResult);
  };

  const handleReset = () => {
    setResult(null);
  };

  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Header />
          <ImageUploader 
            onPrediction={handlePrediction}
            onLoadingChange={setLoading}
            loading={loading}
          />
          {result && (
            <ResultsPanel 
              result={result} 
              onReset={handleReset}
            />
          )}
        </Container>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
