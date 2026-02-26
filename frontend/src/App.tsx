import React, { useState } from 'react';
import axios from 'axios';
import { AnimatePresence, motion } from 'framer-motion';
import PropertyForm from './components/PropertyForm';
import ResultsDisplay from './components/ResultsDisplay';
import SearchHistory from './components/SearchHistory';
import ParticleBackground from './components/ParticleBackground';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

interface PredictionResult {
  address: string;
  postcode: string;
  beds: number;
  baths: number;
  property_type: string;
  min_value: number;
  avg_value: number;
  max_value: number;
  predicted_rent: number;
  model_loaded: boolean;
  model_type: string;
  timestamp: string;
}

interface FormData {
  postcode: string;
  beds: number;
  baths: number;
  property_type: string;
}

export interface HistoryEntry {
  formData: FormData;
  result: PredictionResult;
}

function App() {
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'unknown' | 'connected' | 'disconnected'>('unknown');
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [lastFormData, setLastFormData] = useState<FormData | null>(null);

  React.useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await axios.get(`${API_URL}/health`, { timeout: 5000 });
        setApiStatus('connected');
        console.log('Backend connected:', response.data);
      } catch (err) {
        setApiStatus('disconnected');
        console.error('Backend not available:', err);
      }
    };
    checkBackend();
  }, []);

  const handleSubmit = async (formData: FormData) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setLastFormData(formData);

    try {
      if (apiStatus === 'disconnected') {
        setError('Backend API is not running. Please start the backend with: python backend/app.py');
        setLoading(false);
        return;
      }

      const response = await axios.post<PredictionResult>(
        `${API_URL}/predict`,
        {
          postcode: formData.postcode.trim(),
          beds: formData.beds,
          baths: formData.baths,
          property_type: formData.property_type,
        },
        { timeout: 30000 }
      );

      setResult(response.data);
      setHistory((prev) => {
        const entry: HistoryEntry = { formData, result: response.data };
        const updated = [entry, ...prev.filter(
          (h) => !(h.formData.postcode === formData.postcode &&
                    h.formData.beds === formData.beds &&
                    h.formData.baths === formData.baths &&
                    h.formData.property_type === formData.property_type)
        )];
        return updated.slice(0, 20);
      });
    } catch (err: any) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.message === 'timeout of 30000ms exceeded') {
        setError('Request timeout. The backend server may not be responding.');
      } else if (err.code === 'ECONNREFUSED') {
        setError('Cannot connect to backend API. The server may be starting up — please try again in 30 seconds.');
        setApiStatus('disconnected');
      } else {
        setError(`Error: ${err.message}`);
      }
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = (entry: HistoryEntry) => {
    setResult(entry.result);
    setError(null);
    setLastFormData(entry.formData);
  };

  return (
    <div className="app">
      <ParticleBackground />

      <header className="app-header">
        <h1>UK Property Valuation</h1>
        <p>AI-powered property value and rental income predictions</p>
        <div className={`api-status ${apiStatus}`}>
          <span className="status-dot"></span>
          {apiStatus === 'connected' && 'API Connected'}
          {apiStatus === 'disconnected' && 'API Disconnected'}
          {apiStatus === 'unknown' && 'Checking API...'}
        </div>
      </header>

      <div className="container">
        <div className="form-column">
          <PropertyForm
            onSubmit={handleSubmit}
            isLoading={loading}
            prefill={lastFormData}
          />
          {history.length > 0 && (
            <SearchHistory history={history} onSelect={handleHistorySelect} />
          )}
        </div>

        <div className="results-column">
          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                key="error"
                className="error-message"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <strong>Error:</strong> {error}
              </motion.div>
            )}

            {loading && (
              <motion.div
                key="loading"
                className="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <div className="spinner"></div>
                <p>Analysing property data...</p>
              </motion.div>
            )}

            {result && !loading && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              >
                <ResultsDisplay result={result} />
              </motion.div>
            )}

            {!result && !error && !loading && (
              <motion.div
                key="placeholder"
                className="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <p>Fill in the property details and click "Get Valuation" to see predicted values.</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <footer className="app-footer">
        <p>Powered by LightGBM trained on Rightmove transaction data</p>
      </footer>
    </div>
  );
}

export default App;
