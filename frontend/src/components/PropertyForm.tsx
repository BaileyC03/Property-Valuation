import React, { useState, useEffect } from 'react';
import './PropertyForm.css';

interface FormData {
  postcode: string;
  beds: number;
  baths: number;
  property_type: string;
}

interface PropertyFormProps {
  onSubmit: (data: FormData) => void;
  isLoading: boolean;
  prefill?: FormData | null;
}

const PropertyForm: React.FC<PropertyFormProps> = ({ onSubmit, isLoading, prefill }) => {
  const [formData, setFormData] = useState<FormData>({
    postcode: '',
    beds: 3,
    baths: 1,
    property_type: 'semi-detached',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (prefill) {
      setFormData(prefill);
    }
  }, [prefill]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    const pc = formData.postcode.trim();
    if (!pc) {
      newErrors.postcode = 'Postcode is required';
    } else if (pc.length < 3) {
      newErrors.postcode = 'Enter a valid UK postcode';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePostcodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, postcode: e.target.value }));
    if (errors.postcode) {
      setErrors((prev) => { const n = { ...prev }; delete n.postcode; return n; });
    }
  };

  const stepValue = (field: 'beds' | 'baths', delta: number) => {
    setFormData((prev) => {
      const min = 1;
      const max = field === 'beds' ? 8 : 5;
      const val = Math.min(max, Math.max(min, prev[field] + delta));
      return { ...prev, [field]: val };
    });
  };

  const handleTypeSelect = (type: string) => {
    setFormData((prev) => ({ ...prev, property_type: type }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const propertyTypes = [
    { value: 'detached', label: 'Detached' },
    { value: 'semi-detached', label: 'Semi' },
    { value: 'terraced', label: 'Terraced' },
    { value: 'flat', label: 'Flat' },
  ];

  return (
    <form className="property-form" onSubmit={handleSubmit}>
      <h2>Property Details</h2>

      <div className="form-group">
        <label htmlFor="postcode">Postcode</label>
        <input
          id="postcode"
          type="text"
          name="postcode"
          placeholder="e.g. PO7 5ED, PO2 8RA..."
          value={formData.postcode}
          onChange={handlePostcodeChange}
          disabled={isLoading}
          className={errors.postcode ? 'error' : ''}
          autoComplete="off"
        />
        {errors.postcode && <span className="error-text">{errors.postcode}</span>}
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Bedrooms</label>
          <div className="stepper">
            <button type="button" className="stepper-btn" onClick={() => stepValue('beds', -1)} disabled={isLoading || formData.beds <= 1}>-</button>
            <span className="stepper-value">{formData.beds}</span>
            <button type="button" className="stepper-btn" onClick={() => stepValue('beds', 1)} disabled={isLoading || formData.beds >= 8}>+</button>
          </div>
        </div>

        <div className="form-group">
          <label>Bathrooms</label>
          <div className="stepper">
            <button type="button" className="stepper-btn" onClick={() => stepValue('baths', -1)} disabled={isLoading || formData.baths <= 1}>-</button>
            <span className="stepper-value">{formData.baths}</span>
            <button type="button" className="stepper-btn" onClick={() => stepValue('baths', 1)} disabled={isLoading || formData.baths >= 5}>+</button>
          </div>
        </div>
      </div>

      <div className="form-group">
        <label>Property Type</label>
        <div className="type-selector">
          {propertyTypes.map((t) => (
            <button
              key={t.value}
              type="button"
              className={`type-btn ${formData.property_type === t.value ? 'active' : ''}`}
              onClick={() => handleTypeSelect(t.value)}
              disabled={isLoading}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="submit-btn"
      >
        {isLoading ? 'Getting Valuation...' : 'Get Valuation'}
      </button>
    </form>
  );
};

export default PropertyForm;
