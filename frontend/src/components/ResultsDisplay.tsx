import React from 'react';
import { motion } from 'framer-motion';
import { useCountUp, formatGBP } from '../hooks/useCountUp';
import './ResultsDisplay.css';

interface PredictionResult {
  address: string;
  geocoded_address?: string;
  beds: number;
  baths: number;
  property_type: string;
  min_value: number;
  avg_value: number;
  max_value: number;
  predicted_rent: number;
  model_loaded: boolean;
  timestamp: string;
}

interface ResultsDisplayProps {
  result: PredictionResult;
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.15,
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  }),
};

const CONDITIONS = [
  { label: 'Needs Work', factor: 0.82, color: '#f87171' },
  { label: 'Fair', factor: 0.92, color: '#fbbf24' },
  { label: 'Good', factor: 1.0, color: '#34d399' },
  { label: 'Excellent', factor: 1.10, color: '#7c8cff' },
];

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  const range = result.max_value - result.min_value;
  const avgPercent = range > 0 ? ((result.avg_value - result.min_value) / range) * 100 : 50;

  const animatedAvg = useCountUp(result.avg_value, 1800);
  const animatedMin = useCountUp(result.min_value, 1400);
  const animatedMax = useCountUp(result.max_value, 1400);
  const animatedRent = useCountUp(result.predicted_rent, 1600);
  const animatedAnnual = useCountUp(result.predicted_rent * 12, 1600);

  return (
    <div className="results-display">
      <motion.div
        className="results-card main-card"
        custom={0}
        initial="hidden"
        animate="visible"
        variants={cardVariants}
      >
        <h2>Valuation Results</h2>

        <div className="address-section">
          <p className="input-address">
            <strong>Address:</strong> {result.address}
          </p>
          {result.geocoded_address && result.geocoded_address !== result.address && (
            <p className="geocoded-address">
              <em>Located: {result.geocoded_address}</em>
            </p>
          )}
        </div>

        <div className="property-details">
          <div className="detail-item">
            <span className="label">Beds</span>
            <span className="value">{result.beds}</span>
          </div>
          <div className="detail-item">
            <span className="label">Baths</span>
            <span className="value">{result.baths}</span>
          </div>
          <div className="detail-item">
            <span className="label">Type</span>
            <span className="value" style={{ fontSize: '1rem' }}>{result.property_type || 'Semi-detached'}</span>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="results-card valuation-card"
        custom={1}
        initial="hidden"
        animate="visible"
        variants={cardVariants}
      >
        <h3>Estimated Property Value</h3>

        <div className="value-range">
          <div className="range-bar">
            <div className="range-fill" style={{ width: `${avgPercent}%` }}></div>
          </div>
          <div className="range-labels">
            <span>
              <strong>Min:</strong> {formatGBP(animatedMin)}
            </span>
            <span>
              <strong>Max:</strong> {formatGBP(animatedMax)}
            </span>
          </div>
        </div>

        <div className="average-price">
          <p className="label">Average Estimated Value</p>
          <p className="amount">{formatGBP(animatedAvg)}</p>
          <p className="range-text">
            Range: {formatGBP(result.min_value)} - {formatGBP(result.max_value)}
          </p>
        </div>
      </motion.div>

      <motion.div
        className="results-card condition-card"
        custom={2}
        initial="hidden"
        animate="visible"
        variants={cardVariants}
      >
        <h3>Value by Condition</h3>
        <div className="condition-grid">
          {CONDITIONS.map((c) => {
            const val = Math.round(result.avg_value * c.factor);
            return (
              <div key={c.label} className="condition-item">
                <span className="condition-label" style={{ color: c.color }}>{c.label}</span>
                <span className="condition-value">{formatGBP(val)}</span>
                <span className="condition-pct" style={{ color: c.color }}>
                  {c.factor >= 1 ? '+' : ''}{Math.round((c.factor - 1) * 100)}%
                </span>
              </div>
            );
          })}
        </div>
      </motion.div>

      <motion.div
        className="results-card rental-card"
        custom={3}
        initial="hidden"
        animate="visible"
        variants={cardVariants}
      >
        <h3>Monthly Rental Income</h3>
        <p className="rental-amount">{formatGBP(animatedRent)}</p>
        <p className="rental-note">
          Based on property characteristics and regional data
        </p>
        <p className="annual-estimate">
          Annual estimate: <strong>{formatGBP(animatedAnnual)}</strong>
        </p>
      </motion.div>

      {!result.model_loaded && (
        <motion.div
          className="warning-card"
          custom={4}
          initial="hidden"
          animate="visible"
          variants={cardVariants}
        >
          <p>
            <strong>Note:</strong> Using default values. ML model not loaded.
            Train the model with: <code>python ml/train_model.py</code>
          </p>
        </motion.div>
      )}

      <motion.div
        className="info-footer"
        custom={4}
        initial="hidden"
        animate="visible"
        variants={cardVariants}
      >
        <p>
          <small>
            Prediction made: {new Date(result.timestamp).toLocaleString('en-GB')}
          </small>
        </p>
        <p>
          <small>
            Predictions are estimates based on historical data. For accurate valuations, consult a professional surveyor.
          </small>
        </p>
      </motion.div>
    </div>
  );
};

export default ResultsDisplay;
