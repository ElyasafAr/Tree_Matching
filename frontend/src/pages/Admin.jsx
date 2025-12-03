import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { usersAPI } from '../services/api';
import './Admin.css';

const Admin = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { error: showError, success: showSuccess, showConfirm } = useToast();
  const [isAdmin, setIsAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(false);
  const [activeTab, setActiveTab] = useState('stats'); // 'stats' or 'users'
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [searchName, setSearchName] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    checkAdminStatus();
  }, []);

  const checkAdminStatus = async () => {
    try {
      const response = await usersAPI.checkIsAdmin();
      setIsAdmin(response.data.is_admin);
      
      if (response.data.is_admin) {
        loadStats();
        loadUsers();
      } else {
        showError('אין לך הרשאות גישה לדף זה');
        setTimeout(() => navigate('/'), 2000);
      }
    } catch (error) {
      console.error('Error checking admin status:', error);
      showError('שגיאה בבדיקת הרשאות');
      setTimeout(() => navigate('/'), 2000);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    setLoadingStats(true);
    try {
      const response = await usersAPI.getAdminStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
      if (error.response?.status === 403) {
        showError('אין לך הרשאות גישה לסטטיסטיקות');
        setIsAdmin(false);
      } else {
        showError('שגיאה בטעינת סטטיסטיקות');
      }
    } finally {
      setLoadingStats(false);
    }
  };

  const loadUsers = async () => {
    setLoadingUsers(true);
    try {
      const params = { page, per_page: 20 };
      if (searchName.trim()) {
        params.name = searchName.trim();
      }
      const response = await usersAPI.getAllUsers(params);
      setUsers(response.data.users);
      setTotalPages(response.data.pagination.pages);
    } catch (error) {
      console.error('Error loading users:', error);
      if (error.response?.status === 403) {
        showError('אין לך הרשאות גישה לרשימת משתמשים');
      } else {
        showError('שגיאה בטעינת משתמשים');
      }
    } finally {
      setLoadingUsers(false);
    }
  };

  useEffect(() => {
    if (isAdmin && activeTab === 'users') {
      loadUsers();
    }
  }, [page, searchName, activeTab, isAdmin]);

  const handleSuspend = async (userId, userName) => {
    const confirmed = await showConfirm(
      `האם אתה בטוח שברצונך להשעות את המשתמש "${userName}"?`,
      'המשתמש לא יוכל להתחבר למערכת עד שתבטל את ההשעיה.',
      null,
      'השעה',
      'ביטול'
    );
    if (!confirmed) return;

    try {
      await usersAPI.suspendUser(userId);
      showSuccess('המשתמש הושעה בהצלחה');
      loadUsers();
      loadStats(); // Refresh stats
    } catch (error) {
      showError(error.response?.data?.error || 'שגיאה בהשעיית המשתמש');
    }
  };

  const handleUnsuspend = async (userId, userName) => {
    const confirmed = await showConfirm(
      `האם אתה בטוח שברצונך לבטל את ההשעיה של המשתמש "${userName}"?`,
      null,
      null,
      'בטל השעיה',
      'ביטול'
    );
    if (!confirmed) return;

    try {
      await usersAPI.unsuspendUser(userId);
      showSuccess('השעיית המשתמש בוטלה בהצלחה');
      loadUsers();
      loadStats(); // Refresh stats
    } catch (error) {
      showError(error.response?.data?.error || 'שגיאה בביטול השעיית המשתמש');
    }
  };

  const handleDelete = async (userId, userName) => {
    const confirmed = await showConfirm(
      `⚠️ אזהרה: האם אתה בטוח שברצונך למחוק את המשתמש "${userName}"?`,
      'פעולה זו תמחק את כל הנתונים הקשורים למשתמש (הודעות, צ\'אטים, התאמות, המלצות) ולא ניתן לבטל אותה!',
      null,
      'מחק לצמיתות',
      'ביטול'
    );
    if (!confirmed) return;

    try {
      await usersAPI.deleteUser(userId);
      showSuccess('המשתמש נמחק בהצלחה');
      loadUsers();
      loadStats(); // Refresh stats
    } catch (error) {
      showError(error.response?.data?.error || 'שגיאה במחיקת המשתמש');
    }
  };

  if (loading) {
    return <div className="admin-container"><div className="loading">בודק הרשאות...</div></div>;
  }

  if (!isAdmin) {
    return (
      <div className="admin-container">
        <div className="admin-error">
          <h2>❌ אין הרשאות גישה</h2>
          <p>דף זה זמין רק למנהל המערכת</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>⚙️ דף ניהול</h1>
        <p>ברוך הבא, {user?.full_name}</p>
      </div>

      <div className="admin-tabs">
        <button
          className={`admin-tab ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          📊 סטטיסטיקות
        </button>
        <button
          className={`admin-tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👥 ניהול משתמשים
        </button>
      </div>

      {activeTab === 'users' && (
        <div className="admin-users-section">
          <div className="users-search">
            <input
              type="text"
              placeholder="חיפוש לפי שם..."
              value={searchName}
              onChange={(e) => {
                setSearchName(e.target.value);
                setPage(1);
              }}
              className="users-search-input"
            />
          </div>

          {loadingUsers ? (
            <div className="loading">טוען משתמשים...</div>
          ) : users.length === 0 ? (
            <div className="no-results">לא נמצאו משתמשים</div>
          ) : (
            <>
              <div className="users-table">
                <table>
                  <thead>
                    <tr>
                      <th>שם</th>
                      <th>אימייל</th>
                      <th>גיל</th>
                      <th>מיקום</th>
                      <th>המלצות</th>
                      <th>סטטוס</th>
                      <th>פעולות</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className={u.is_suspended ? 'suspended' : ''}>
                        <td>
                          {u.full_name}
                          {u.is_root && <span className="root-badge">👑 מנהל</span>}
                        </td>
                        <td>{u.email}</td>
                        <td>{u.age || '-'}</td>
                        <td>{u.location || '-'}</td>
                        <td>{u.referrals_count || 0}</td>
                        <td>
                          {u.is_suspended ? (
                            <span className="status-badge suspended-badge">מושעה</span>
                          ) : (
                            <span className="status-badge active-badge">פעיל</span>
                          )}
                        </td>
                        <td>
                          <div className="user-actions">
                            {u.is_suspended ? (
                              <button
                                onClick={() => handleUnsuspend(u.id, u.full_name)}
                                className="btn btn-small btn-success"
                                disabled={u.is_root}
                              >
                                בטל השעיה
                              </button>
                            ) : (
                              <button
                                onClick={() => handleSuspend(u.id, u.full_name)}
                                className="btn btn-small btn-warning"
                                disabled={u.is_root}
                              >
                                השעה
                              </button>
                            )}
                            <button
                              onClick={() => handleDelete(u.id, u.full_name)}
                              className="btn btn-small btn-danger"
                              disabled={u.is_root}
                            >
                              מחק
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="btn btn-secondary"
                  >
                    ← הקודם
                  </button>
                  <span className="pagination-info">
                    עמוד {page} מתוך {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="btn btn-secondary"
                  >
                    הבא →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {activeTab === 'stats' && (

      {loadingStats ? (
        <div className="loading">טוען סטטיסטיקות...</div>
      ) : stats ? (
        <div className="admin-stats">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-value">{stats.total_users}</div>
              <div className="stat-label">סה"כ משתמשים</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">🌳</div>
              <div className="stat-value">{stats.total_referrals}</div>
              <div className="stat-label">סה"כ המלצות</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">❤️</div>
              <div className="stat-value">{stats.total_matches}</div>
              <div className="stat-label">סה"כ לייקים</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">💚</div>
              <div className="stat-value">{stats.total_mutual_matches}</div>
              <div className="stat-label">התאמות הדדיות</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">💬</div>
              <div className="stat-value">{stats.total_chats}</div>
              <div className="stat-label">סה"כ צ'אטים</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">📨</div>
              <div className="stat-value">{stats.total_messages}</div>
              <div className="stat-label">סה"כ הודעות</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">🆕</div>
              <div className="stat-value">{stats.recent_users}</div>
              <div className="stat-label">משתמשים חדשים (7 ימים)</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">🟢</div>
              <div className="stat-value">{stats.active_users}</div>
              <div className="stat-label">משתמשים פעילים (7 ימים)</div>
            </div>
          </div>

          {stats.gender_breakdown && Object.keys(stats.gender_breakdown).length > 0 && (
            <div className="stats-section">
              <h2>📊 פילוח לפי מגדר</h2>
              <div className="gender-breakdown">
                {Object.entries(stats.gender_breakdown).map(([gender, count]) => (
                  <div key={gender} className="gender-item">
                    <span className="gender-label">
                      {gender === 'male' ? '♂ זכר' : gender === 'female' ? '♀ נקבה' : gender === 'other' ? '⚥ אחר' : gender}
                    </span>
                    <span className="gender-count">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="admin-error">
          <p>לא ניתן לטעון סטטיסטיקות</p>
          <button onClick={loadStats} className="btn btn-primary">נסה שוב</button>
        </div>
      )}
      )}
    </div>
  );
};

export default Admin;

