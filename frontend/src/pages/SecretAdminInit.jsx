import { useState } from 'react';
import axios from 'axios';
import './Auth.css';

const SecretAdminInit = () => {
  const [adminPassword, setAdminPassword] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  const handleMigration = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_URL}/admin/migrate-add-email-hash`, {
        admin_password: adminPassword || 'TreeMatching2024!'
      });
      alert('✅ Migration successful! Column added.');
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Migration failed');
    }
    
    setLoading(false);
  };

  const handleReset = async () => {
    if (!window.confirm('⚠️ WARNING: This will DELETE ALL DATA! Continue?')) {
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_URL}/admin/reset-database-DANGER`);
      alert('✅ Database reset successful!');
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Reset failed');
    }
    
    setLoading(false);
  };

  const handleCreateFirstUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/api/secret-initialize-system`, {
        admin_password: adminPassword,
        email,
        password,
        full_name: fullName
      });
      
      setResult(response.data);
      alert(`✅ User created!\nReferral Code: ${response.data.referral_code}\n\nSave this code!`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create user');
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card" style={{ maxWidth: '600px' }}>
        <h1 style={{ color: '#ff6b6b' }}>⚠️ Admin: System Initialization</h1>
        <p style={{ fontSize: '0.9rem', color: '#666' }}>
          This page is for initial system setup only. Do not share this URL!
        </p>

        <hr style={{ margin: '20px 0' }} />

        <div style={{ marginBottom: '30px' }}>
          <h3>Step 0: Run Migration (First Time Only)</h3>
          <p style={{ fontSize: '0.85rem', color: '#666', marginBottom: '10px' }}>
            Adds email_hash column to database. Run this once before creating users.
          </p>
          <button 
            onClick={handleMigration}
            className="auth-button"
            style={{ backgroundColor: '#3498db' }}
            disabled={loading}
          >
            🔧 Run Migration
          </button>
        </div>

        <hr style={{ margin: '20px 0' }} />

        <div style={{ marginBottom: '30px' }}>
          <h3>Step 1: Reset Database (Optional)</h3>
          <button 
            onClick={handleReset}
            className="auth-button"
            style={{ backgroundColor: '#ff6b6b' }}
            disabled={loading}
          >
            🗑️ Delete All Data
          </button>
        </div>

        <hr style={{ margin: '20px 0' }} />

        <h3>Step 2: Create First User</h3>
        <form onSubmit={handleCreateFirstUser} className="auth-form">
          <div className="form-group">
            <label>Admin Setup Password</label>
            <input
              type="password"
              value={adminPassword}
              onChange={(e) => setAdminPassword(e.target.value)}
              required
              className="form-input"
              placeholder="Default: TreeMatching2024!"
            />
            <small style={{ color: '#666', fontSize: '0.8rem' }}>
              Set ADMIN_SETUP_PASSWORD in Railway Variables to change
            </small>
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="form-input"
            />
          </div>

          <button 
            type="submit" 
            className="auth-button"
            disabled={loading}
          >
            {loading ? 'Creating...' : '🌱 Create First User'}
          </button>
        </form>

        {error && (
          <div className="auth-error" style={{ marginTop: '20px' }}>
            {error}
          </div>
        )}

        {result && (
          <div style={{ 
            marginTop: '20px', 
            padding: '15px', 
            backgroundColor: '#d4edda', 
            border: '1px solid #c3e6cb',
            borderRadius: '5px'
          }}>
            <h4 style={{ color: '#155724', marginTop: 0 }}>✅ Success!</h4>
            <p><strong>Referral Code:</strong> <code style={{ 
              fontSize: '1.2rem', 
              backgroundColor: '#fff', 
              padding: '5px 10px',
              borderRadius: '3px'
            }}>{result.referral_code}</code></p>
            <p><strong>User ID:</strong> {result.user_id}</p>
            <p style={{ color: '#856404', marginTop: '15px' }}>
              ⚠️ Save this referral code! Others need it to register.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SecretAdminInit;

