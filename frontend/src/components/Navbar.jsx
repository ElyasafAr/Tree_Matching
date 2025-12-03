import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState, useEffect } from 'react';
import { chatAPI, usersAPI } from '../services/api';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if (user) {
      // Load unread count initially
      loadUnreadCount();
      
      // Check if user is admin
      checkAdminStatus();
      
      // Poll for new messages every 30 seconds
      const interval = setInterval(loadUnreadCount, 30000);
      return () => clearInterval(interval);
    } else {
      setIsAdmin(false);
    }
  }, [user]);

  const checkAdminStatus = async () => {
    try {
      const response = await usersAPI.checkIsAdmin();
      setIsAdmin(response.data.is_admin);
    } catch (error) {
      console.error('Error checking admin status:', error);
      setIsAdmin(false);
    }
  };

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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
              <Link to="/referrals" className="navbar-item">
                {isMobile ? 'המלצות' : 'ההמלצות שלי'}
              </Link>
              <Link to="/profile" className="navbar-item">פרופיל</Link>
              <Link to="/blocked" className="navbar-item">🚫 חסומים</Link>
              {isAdmin && (
                <Link to="/admin" className="navbar-item navbar-admin" title="דף ניהול">
                  ⚙️ {isMobile ? 'ניהול' : 'ניהול'}
                </Link>
              )}
              <button onClick={handleLogout} className="navbar-item navbar-logout">
                {isMobile ? 'יציאה' : 'התנתק'}
              </button>
            </div>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;

