import React from 'react';
import { motion } from 'framer-motion';
import { formatGBP } from '../hooks/useCountUp';
import { HistoryEntry } from '../App';
import './SearchHistory.css';

interface SearchHistoryProps {
  history: HistoryEntry[];
  onSelect: (entry: HistoryEntry) => void;
}

const SearchHistory: React.FC<SearchHistoryProps> = ({ history, onSelect }) => {
  return (
    <motion.div
      className="search-history"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      <h3>Recent Searches</h3>
      <div className="history-list">
        {history.map((entry, i) => (
          <button
            key={`${entry.formData.postcode}-${entry.formData.beds}-${entry.formData.baths}-${entry.formData.property_type}-${i}`}
            className="history-item"
            onClick={() => onSelect(entry)}
          >
            <div className="history-main">
              <span className="history-postcode">{entry.result.postcode || entry.formData.postcode}</span>
              <span className="history-price">{formatGBP(entry.result.avg_value)}</span>
            </div>
            <div className="history-meta">
              {entry.formData.beds}bed {entry.formData.baths}bath {entry.formData.property_type}
            </div>
          </button>
        ))}
      </div>
    </motion.div>
  );
};

export default SearchHistory;
