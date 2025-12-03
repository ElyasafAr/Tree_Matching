import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usersAPI, chatAPI, uploadAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import './UserCard.css';

const UserCard = ({ user, showActions = true, onLike, onBlock }) => {
  const navigate = useNavigate();
  const { success: showSuccess, error: showError, showConfirm } = useToast();
  const [liked, setLiked] = useState(user?.liked_by_me || false);
  const [blocked, setBlocked] = useState(user?.blocked_by_me || false);
  const [loading, setLoading] = useState(false);
  const [blocking, setBlocking] = useState(false);

  // Update blocked state when user changes
  useEffect(() => {
    setBlocked(user?.blocked_by_me || false);
    setLiked(user?.liked_by_me || false);
  }, [user]);

  // Safety check - if user is not provided, don't render
  if (!user) {
    return <div className="user-card">טוען...</div>;
  }

  const handleLike = async () => {
    if (loading || !user?.id) return;
    
    setLoading(true);
    try {
      const response = await usersAPI.likeUser(user.id);
      setLiked(true);
      if (response.data.is_mutual) {
        showSuccess("זה התאמה! 💚");
      }
      if (onLike) onLike();
    } catch (error) {
      showError(error.response?.data?.error || "שגיאה בלייק");
    }
    setLoading(false);
  };

  const handleMessage = async () => {
    if (!user?.id) return;
    try {
      const response = await chatAPI.startChat(user.id);
      navigate(`/chat/${response.data.chat.id}`);
    } catch (error) {
      showError("שגיאה בפתיחת צ'אט");
    }
  };

  const handleViewProfile = () => {
    if (!user?.id) return;
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
        showError("שגיאה בפתיחת צ'אט עם הממליץ: " + (error.response?.data?.error || error.message));
      }
    } else {
      console.log('[CARD REFERRER CHAT] No referrer on user:', user);
      showError("משתמש זה לא הומלץ על ידי אף אחד");
    }
  };

  const handleBlock = async () => {
    if (blocking || !user?.id) return;
    
    const confirmed = await showConfirm(
      `האם אתה בטוח שברצונך לחסום את ${user.full_name}?`,
      'המשתמש לא יופיע בחיפוש שלך ולא תוכל לראות את הפרופיל שלו. תוכל לבטל את החסימה בכל עת.',
      null,
      'חסום',
      'ביטול'
    );
    
    if (!confirmed) return;
    
    setBlocking(true);
    try {
      await usersAPI.blockUser(user.id);
      setBlocked(true);
      setLiked(false); // Remove like if exists
      showSuccess("המשתמש נחסם בהצלחה");
      if (onBlock) onBlock();
      if (onLike) onLike(); // Refresh list
    } catch (error) {
      showError(error.response?.data?.error || "שגיאה בחסימת המשתמש");
    }
    setBlocking(false);
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
        <h3 className="user-card-name">{user.full_name || 'ללא שם'}</h3>
        
        <div className="user-card-info">
          {user.age && <span>גיל: {user.age}</span>}
          {user.location && <span>📍 {user.location}</span>}
          {user.gender && <span>{user.gender === 'male' ? '♂' : user.gender === 'female' ? '♀' : '⚥'}</span>}
        </div>
        
        {user.bio && (
          <p className="user-card-bio">{user.bio}</p>
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
            
            {!blocked ? (
              <button 
                className="btn btn-block"
                onClick={handleBlock}
                disabled={blocking}
              >
                {blocking ? '...' : '🚫 חסום'}
              </button>
            ) : (
              <button className="btn btn-blocked" disabled>
                ✓ חסום
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserCard;

