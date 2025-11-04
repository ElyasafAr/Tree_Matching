import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState, useEffect } from 'react';
import { chatAPI } from '../services/api';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      // Load unread count initially
      loadUnreadCount();
      
      // Poll for new messages every 30 seconds
      const interval = setInterval(loadUnreadCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const loadUnreadCount = async () => {
    try {
      const response = await chatAPI.getUnreadCount();
      setUnreadCount(response.data.unread_count || 0);
    } catch (error) {
      console.error('Error loading unread count:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          🌳 Tree Matching
        </Link>
        
        {user && (
          <>
            <div className="navbar-user-info">
              <span className="navbar-username">שלום, {user.full_name}</span>
            </div>
            
            <div className="navbar-menu">
              <Link to="/" className="navbar-item">חיפוש</Link>
              <Link to="/matches" className="navbar-item">התאמות</Link>
              <Link to="/chat" className="navbar-item navbar-chat">
                צ'אט
                {unreadCount > 0 && (
                  <span className="unread-badge">{unreadCount}</span>
                )}
              </Link>
              <Link to="/referrals" className="navbar-item">ההמלצות שלי</Link>
              <Link to="/profile" className="navbar-item">פרופיל</Link>
              <button onClick={handleLogout} className="navbar-item navbar-logout">
                התנתק
              </button>
            </div>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;

