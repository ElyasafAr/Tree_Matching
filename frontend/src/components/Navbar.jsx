import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

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
          <div className="navbar-menu">
            <Link to="/" className="navbar-item">חיפוש</Link>
            <Link to="/matches" className="navbar-item">התאמות</Link>
            <Link to="/chat" className="navbar-item">צ'אט</Link>
            <Link to="/referrals" className="navbar-item">ההמלצות שלי</Link>
            <Link to="/profile" className="navbar-item">פרופיל</Link>
            <button onClick={handleLogout} className="navbar-item navbar-logout">
              התנתק
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;

