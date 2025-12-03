import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usersAPI, uploadAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import UserCard from '../components/UserCard';
import './BlockedUsers.css';

const BlockedUsers = () => {
  const navigate = useNavigate();
  const { success: showSuccess, error: showError, showConfirm } = useToast();
  const [blockedUsers, setBlockedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [unblocking, setUnblocking] = useState({});

  useEffect(() => {
    loadBlockedUsers();
  }, []);

  const loadBlockedUsers = async () => {
    setLoading(true);
    try {
      const response = await usersAPI.getBlockedUsers();
      setBlockedUsers(response.data.blocked_users || []);
    } catch (error) {
      console.error('Error loading blocked users:', error);
      showError('שגיאה בטעינת משתמשים חסומים');
    } finally {
      setLoading(false);
    }
  };

  const handleUnblock = async (userId, userName) => {
    const confirmed = await showConfirm(
      `האם אתה בטוח שברצונך לבטל את החסימה של ${userName}?`,
      'המשתמש יופיע שוב בחיפוש שלך ותוכל לראות את הפרופיל שלו.',
      null,
      'בטל חסימה',
      'ביטול'
    );

    if (!confirmed) return;

    setUnblocking(prev => ({ ...prev, [userId]: true }));
    try {
      await usersAPI.unblockUser(userId);
      showSuccess('החסימה בוטלה בהצלחה');
      loadBlockedUsers(); // Reload list
    } catch (error) {
      showError(error.response?.data?.error || 'שגיאה בביטול החסימה');
    } finally {
      setUnblocking(prev => ({ ...prev, [userId]: false }));
    }
  };

  if (loading) {
    return (
      <div className="blocked-users-container">
        <div className="loading">טוען משתמשים חסומים...</div>
      </div>
    );
  }

  return (
    <div className="blocked-users-container">
      <div className="blocked-users-header">
        <h1>🚫 משתמשים חסומים</h1>
        <p>רשימת כל המשתמשים שחסמת. תוכל לבטל את החסימה בכל עת.</p>
      </div>

      {blockedUsers.length === 0 ? (
        <div className="no-blocked-users">
          <div className="empty-state">
            <div className="empty-icon">🔓</div>
            <h2>אין משתמשים חסומים</h2>
            <p>לא חסמת אף משתמש עדיין.</p>
            <button 
              onClick={() => navigate('/')} 
              className="btn btn-primary"
            >
              חזור לחיפוש
            </button>
          </div>
        </div>
      ) : (
        <div className="blocked-users-list">
          {blockedUsers.map(user => (
            <div key={user.id} className="blocked-user-item">
              <UserCard 
                user={{ ...user, blocked_by_me: true }} 
                showActions={false}
              />
              <div className="unblock-section">
                <button
                  onClick={() => handleUnblock(user.id, user.full_name)}
                  disabled={unblocking[user.id]}
                  className="btn btn-success"
                >
                  {unblocking[user.id] ? 'מבטל חסימה...' : '🔓 בטל חסימה'}
                </button>
                {user.blocked_at && (
                  <p className="blocked-date">
                    נחסם ב: {new Date(user.blocked_at).toLocaleDateString('he-IL')}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BlockedUsers;

