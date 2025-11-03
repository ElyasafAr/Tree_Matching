import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import './Auth.css';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    phone: '',
    age: '',
    gender: '',
    location: '',
    bio: '',
    referral_code: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [referrerName, setReferrerName] = useState('');
  const [validatingCode, setValidatingCode] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Validate referral code when it changes
    if (name === 'referral_code' && value.length >= 6) {
      validateReferralCode(value);
    } else if (name === 'referral_code') {
      setReferrerName('');
    }
  };

  const validateReferralCode = async (code) => {
    setValidatingCode(true);
    try {
      const response = await authAPI.validateReferralCode(code);
      if (response.data.valid) {
        setReferrerName(response.data.referrer_name);
        setError('');
      } else {
        setReferrerName('');
        setError('קוד המלצה לא תקין');
      }
    } catch (error) {
      setReferrerName('');
    }
    setValidatingCode(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('הסיסמאות אינן תואמות');
      return;
    }

    if (formData.password.length < 6) {
      setError('הסיסמה חייבת להיות לפחות 6 תווים');
      return;
    }

    if (!referrerName) {
      setError('יש להזין קוד המלצה תקין');
      return;
    }

    setLoading(true);

    // Remove confirmPassword before sending
    const { confirmPassword, ...dataToSend } = formData;
    const result = await register(dataToSend);
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card auth-card-large">
        <h1 className="auth-title">🌳 Tree Matching</h1>
        <h2 className="auth-subtitle">הרשמה</h2>
        
        {error && <div className="auth-error">{error}</div>}
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="full_name">שם מלא *</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="email">אימייל *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password">סיסמה *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="form-input"
                minLength="6"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmPassword">אימות סיסמה *</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="form-input"
                minLength="6"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="phone">טלפון</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="age">גיל</label>
              <input
                type="number"
                id="age"
                name="age"
                value={formData.age}
                onChange={handleChange}
                className="form-input"
                min="18"
                max="120"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="gender">מגדר</label>
              <select
                id="gender"
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                className="form-input"
              >
                <option value="">בחר מגדר</option>
                <option value="male">זכר</option>
                <option value="female">נקבה</option>
                <option value="other">אחר</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="location">מיקום</label>
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                className="form-input"
                placeholder="עיר/אזור"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="bio">על עצמי</label>
            <textarea
              id="bio"
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              className="form-input form-textarea"
              rows="4"
              placeholder="ספר/י קצת על עצמך..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="referral_code">קוד המלצה * (חובה)</label>
            <input
              type="text"
              id="referral_code"
              name="referral_code"
              value={formData.referral_code}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="הזן קוד המלצה מחבר"
            />
            {validatingCode && <small>בודק קוד...</small>}
            {referrerName && (
              <small className="referrer-valid">
                ✓ הומלץ על ידי: {referrerName}
              </small>
            )}
          </div>
          
          <button 
            type="submit" 
            className="auth-button"
            disabled={loading || !referrerName}
          >
            {loading ? 'נרשם...' : 'הרשם'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>
            כבר רשום? <Link to="/login">התחבר</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;

