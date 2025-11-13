import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usersAPI, chatAPI, uploadAPI } from '../services/api';
import './UserCard.css';

const UserCard = ({ user, showActions = true, onLike }) => {
  const navigate = useNavigate();
  const [liked, setLiked] = useState(user.liked_by_me || false);
  const [loading, setLoading] = useState(false);

  const handleLike = async () => {
    if (loading) return;
    
    setLoading(true);
    try {
      const response = await usersAPI.likeUser(user.id);
      setLiked(true);
      if (response.data.is_mutual) {
        alert("זה התאמה! 💚");
      }
      if (onLike) onLike();
    } catch (error) {
      alert(error.response?.data?.error || "שגיאה בלייק");
    }
    setLoading(false);
  };

  const handleMessage = async () => {
    try {
      const response = await chatAPI.startChat(user.id);
      navigate(`/chat/${response.data.chat.id}`);
    } catch (error) {
      alert("שגיאה בפתיחת צ'אט");
    }
  };

  const handleViewProfile = () => {
    navigate(`/user/${user.id}`);
  };

  const handleContactReferrer = async () => {
    if (user.referred_by?.id) {
      try {
        console.log('[CARD REFERRER CHAT] Starting chat with:', user.referred_by.id);
        const response = await chatAPI.startChat(user.referred_by.id);
        console.log('[CARD REFERRER CHAT] Response:', response.data);
        navigate(`/chat/${response.data.chat.id}`);
      } catch (error) {
        console.error('[CARD REFERRER CHAT] Error:', error.response?.data || error.message);
        alert("שגיאה בפתיחת צ'אט עם הממליץ: " + (error.response?.data?.error || error.message));
      }
    } else {
      console.log('[CARD REFERRER CHAT] No referrer on user:', user);
      alert("משתמש זה לא הומלץ על ידי אף אחד");
    }
  };

  return (
    <div className="user-card">
      <div className="user-card-image">
        {user.profile_image ? (
          <img src={uploadAPI.getImageUrl(user.profile_image)} alt={user.full_name} />
        ) : (
          <div className="user-card-placeholder">
            {user.full_name?.[0] || '👤'}
          </div>
        )}
      </div>
      
      <div className="user-card-content">
        <h3 className="user-card-name">{user.full_name}</h3>
        
        <div className="user-card-info">
          {user.age && <span>גיל: {user.age}</span>}
          {user.location && <span>📍 {user.location}</span>}
          {user.gender && <span>{user.gender === 'male' ? '♂' : user.gender === 'female' ? '♀' : '⚥'}</span>}
        </div>
        
        {user.bio && (
          <p className="user-card-bio">{user.bio}</p>
        )}
        
        {user.social_link && (
          <div className="user-card-social">
            <a 
              href={user.social_link} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                color: 'var(--color-primary)',
                textDecoration: 'underline',
                fontSize: '0.9rem',
                wordBreak: 'break-all'
              }}
            >
              🔗 רשת חברתית
            </a>
          </div>
        )}
        
        {user.referred_by && (
          <div className="user-card-referrer">
            <span>הומלץ על ידי: </span>
            <button 
              className="referrer-link"
              onClick={handleContactReferrer}
            >
              {user.referred_by.name} 💬
            </button>
          </div>
        )}
        
        {showActions && (
          <div className="user-card-actions">
            <button 
              className="btn btn-primary"
              onClick={handleViewProfile}
            >
              צפה בפרופיל
            </button>
            
            {!liked ? (
              <button 
                className="btn btn-like"
                onClick={handleLike}
                disabled={loading}
              >
                {loading ? '...' : '❤️ לייק'}
              </button>
            ) : (
              <button className="btn btn-liked" disabled>
                ✓ אהבתי
              </button>
            )}
            
            <button 
              className="btn btn-secondary"
              onClick={handleMessage}
            >
              💬 שלח הודעה
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserCard;

