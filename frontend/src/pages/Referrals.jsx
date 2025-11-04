import { useState, useEffect } from 'react';
import { referralsAPI, chatAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';
import './Referrals.css';

const Referrals = () => {
  const [myReferrals, setMyReferrals] = useState([]);
  const [myReferrer, setMyReferrer] = useState(null);
  const [tree, setTree] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [referralsRes, referrerRes, treeRes, statsRes] = await Promise.all([
        referralsAPI.getMyReferrals(),
        referralsAPI.getMyReferrer(),
        referralsAPI.getTree(),
        referralsAPI.getStats()
      ]);

      setMyReferrals(referralsRes.data.referrals);
      setMyReferrer(referrerRes.data.referrer);
      setTree(treeRes.data.tree);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading referrals:', error);
    }
    setLoading(false);
  };

  const handleContactReferrer = async () => {
    if (myReferrer?.id) {
      try {
        const response = await chatAPI.startChat(myReferrer.id);
        navigate(`/chat/${response.data.chat.id}`);
      } catch (error) {
        alert("שגיאה בפתיחת צ'אט");
      }
    }
  };

  const renderTree = (node, level = 0) => {
    if (!node) return null;
    
    return (
      <div className="tree-node" style={{ marginRight: `${level * 2}rem` }}>
        <div className="tree-node-content">
          <span className="tree-node-name">{node.name}</span>
          {node.children_count > 0 && (
            <span className="tree-node-count">({node.children_count})</span>
          )}
        </div>
        {node.children && node.children.length > 0 && (
          <div className="tree-children">
            {node.children.map(child => (
              <div key={child.id}>{renderTree(child, level + 1)}</div>
            ))}
          </div>
        )}
      </div>
    );
  };

  if (loading) return <div className="loading">טוען...</div>;

  return (
    <div className="referrals-container">
      <div className="referrals-header">
        <h1>מערכת ההמלצות</h1>
        <p>ניהול ההמלצות שלך ועץ החיבורים</p>
      </div>

      <div className="referrals-grid">
        <div className="referral-card stats-card">
          <h2>📊 סטטיסטיקות</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{stats?.direct_referrals || 0}</div>
              <div className="stat-label">המלצות ישירות</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats?.total_referrals || 0}</div>
              <div className="stat-label">סה"כ בעץ</div>
            </div>
          </div>
        </div>

        {myReferrer && (
          <div className="referral-card">
            <h2>👤 הממליץ שלי</h2>
            <div className="referrer-details">
              <div className="referrer-avatar">
                {myReferrer.profile_image ? (
                  <img src={myReferrer.profile_image} alt={myReferrer.name} />
                ) : (
                  <div className="avatar-placeholder">{myReferrer.name[0]}</div>
                )}
              </div>
              <div className="referrer-info">
                <h3>{myReferrer.name}</h3>
                {myReferrer.location && <p>📍 {myReferrer.location}</p>}
                {myReferrer.bio && <p className="referrer-bio">{myReferrer.bio}</p>}
              </div>
            </div>
            <button onClick={handleContactReferrer} className="btn btn-primary">
              💬 צור קשר
            </button>
          </div>
        )}

        <div className="referral-card full-width">
          <h2>🌿 ההמלצות שלי</h2>
          {myReferrals.length === 0 ? (
            <p className="no-data">עדיין לא המלצת על אף אחד. שתף את קוד ההמלצה שלך!</p>
          ) : (
            <div className="referrals-list">
              {myReferrals.map(referral => (
                <div key={referral.id} className="referral-item">
                  <div className="referral-avatar">
                    {referral.profile_image ? (
                      <img src={referral.profile_image} alt={referral.name} />
                    ) : (
                      <div className="avatar-placeholder">{referral.name[0]}</div>
                    )}
                  </div>
                  <div className="referral-details">
                    <h4>{referral.name}</h4>
                    <p>
                      {referral.age && `גיל: ${referral.age}`}
                      {referral.location && ` • 📍 ${referral.location}`}
                    </p>
                    <p className="referral-date">
                      הצטרף/ה: {new Date(referral.referred_at).toLocaleDateString('he-IL')}
                    </p>
                  </div>
                  <button 
                    onClick={() => navigate(`/profile/${referral.id}`)}
                    className="btn btn-secondary"
                  >
                    צפה בפרופיל
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="referral-card full-width tree-card">
          <h2>🌳 עץ ההמלצות שלי</h2>
          <p className="tree-hint">ראה את כל רשת ההמלצות שיצרת (עד 3 רמות)</p>
          <div className="tree-container">
            {tree ? renderTree(tree) : <p>אין נתוני עץ</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Referrals;

