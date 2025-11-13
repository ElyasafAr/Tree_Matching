import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { usersAPI, uploadAPI, chatAPI } from '../services/api';
import UserCard from '../components/UserCard';
import ISRAEL_LOCATIONS from '../data/locations';
import './Profile.css';

const Profile = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { user: currentUser, updateUser } = useAuth();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});
  const [uploadingImage, setUploadingImage] = useState(false);
  const fileInputRef = useRef(null);

  const isOwnProfile = !userId || parseInt(userId) === currentUser?.id;

  useEffect(() => {
    if (isOwnProfile) {
      setUser(currentUser);
      setFormData(currentUser || {});
      setLoading(false);
    } else {
      loadUserProfile();
    }
  }, [userId, currentUser]);

  const loadUserProfile = async () => {
    setLoading(true);
    try {
      const response = await usersAPI.getProfile(userId);
      setUser(response.data.user);
    } catch (error) {
      console.error('Error loading profile:', error);
    }
    setLoading(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await usersAPI.updateProfile(formData);
      updateUser(response.data.user);
      setUser(response.data.user);
      setEditing(false);
      alert("הפרופיל עודכן בהצלחה");
    } catch (error) {
      alert("שגיאה בעדכון הפרופיל");
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      alert('הקובץ גדול מדי. גודל מקסימלי: 5MB');
      return;
    }

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('סוג קובץ לא נתמך. יש להעלות תמונה (PNG, JPG, GIF, WEBP)');
      return;
    }

    setUploadingImage(true);
    try {
      const response = await uploadAPI.uploadProfileImage(file);
      const updatedUser = { ...currentUser, profile_image: response.data.image_url };
      updateUser(updatedUser);
      setUser(updatedUser);
      setFormData(updatedUser);
      alert('תמונת הפרופיל הועלתה בהצלחה!');
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('שגיאה בהעלאת התמונה');
    } finally {
      setUploadingImage(false);
    }
  };

  const handleDeleteImage = async () => {
    if (!confirm('האם אתה בטוח שברצונך למחוק את תמונת הפרופיל?')) return;

    try {
      await uploadAPI.deleteProfileImage();
      const updatedUser = { ...currentUser, profile_image: null };
      updateUser(updatedUser);
      setUser(updatedUser);
      setFormData(updatedUser);
      alert('תמונת הפרופיל נמחקה בהצלחה');
    } catch (error) {
      console.error('Error deleting image:', error);
      alert('שגיאה במחיקת התמונה');
    }
  };

  if (loading) return <div className="loading">טוען...</div>;
  if (!user) return <div className="loading">משתמש לא נמצא</div>;

  if (!isOwnProfile) {
    return (
        <div className="profile-container">
        <div className="profile-view">
          <div className="profile-header">
            <h1>פרופיל משתמש</h1>
            <button
              onClick={async () => {
                try {
                  const response = await chatAPI.startChat(user.id);
                  navigate(`/chat/${response.data.chat.id}`);
                } catch (error) {
                  alert("שגיאה בפתיחת צ'אט: " + (error.response?.data?.error || error.message));
                }
              }}
              className="btn btn-primary"
            >
              💬 צור קשר
            </button>
          </div>

          <div className="profile-info">
            {/* Display UserCard for quick actions */}
            <div style={{ marginBottom: '2rem' }}>
              <UserCard user={user} showActions={true} />
            </div>

            {/* Full profile information */}
            <div className="info-section">
              <h2>📋 פרטים</h2>
              <div className="info-grid">
                <div className="info-item">
                  <strong>שם:</strong> {user.full_name}
                </div>
                {user.age && (
                  <div className="info-item">
                    <strong>גיל:</strong> {user.age}
                  </div>
                )}
                {user.gender && (
                  <div className="info-item">
                    <strong>מגדר:</strong> {user.gender === 'male' ? 'זכר' : user.gender === 'female' ? 'נקבה' : 'אחר'}
                  </div>
                )}
                {user.location && (
                  <div className="info-item">
                    <strong>מיקום:</strong> {user.location}
                  </div>
                )}
                {user.height && (
                  <div className="info-item">
                    <strong>גובה:</strong> {user.height} ס"מ
                  </div>
                )}
                {user.employment_status && (
                  <div className="info-item">
                    <strong>מצב תעסוקתי:</strong> {user.employment_status}
                  </div>
                )}
              </div>
            </div>

            {user.bio && (
              <div className="info-section">
                <h2>💭 על עצמי</h2>
                <p style={{ whiteSpace: 'pre-wrap' }}>{user.bio}</p>
              </div>
            )}

            {user.interests && (
              <div className="info-section">
                <h2>🎯 תחומי עניין</h2>
                <p>{user.interests}</p>
              </div>
            )}

            {user.referred_by && (
              <div className="info-section">
                <h2>👤 הומלץ על ידי</h2>
                <div className="referrer-info">
                  <p>
                    <strong>
                      <button
                        onClick={() => navigate(`/profile/${user.referred_by.id}`)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: 'var(--color-primary)',
                          cursor: 'pointer',
                          textDecoration: 'underline',
                          fontSize: 'inherit',
                          fontFamily: 'inherit',
                          fontWeight: 'bold',
                          padding: 0
                        }}
                      >
                        {user.referred_by.name}
                      </button>
                    </strong>
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (editing) {
    return (
      <div className="profile-container">
        <div className="profile-edit">
          <h1>עריכת פרופיל</h1>
          
          {/* Profile Image Upload Section */}
          <div className="profile-image-section">
            <div className="profile-image-container">
              {user.profile_image ? (
                <img 
                  src={uploadAPI.getImageUrl(user.profile_image)} 
                  alt="תמונת פרופיל" 
                  className="profile-image-preview"
                />
              ) : (
                <div className="profile-image-placeholder">
                  <span className="placeholder-icon">👤</span>
                  <p>אין תמונת פרופיל</p>
                </div>
              )}
            </div>
            <div className="profile-image-actions">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                onChange={handleImageUpload}
                style={{ display: 'none' }}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="btn btn-secondary"
                disabled={uploadingImage}
              >
                {uploadingImage ? 'מעלה...' : user.profile_image ? 'החלף תמונה' : 'העלה תמונה'}
              </button>
              {user.profile_image && (
                <button
                  type="button"
                  onClick={handleDeleteImage}
                  className="btn btn-danger"
                  disabled={uploadingImage}
                >
                  מחק תמונה
                </button>
              )}
              <p className="image-hint">תמונה עד 5MB (PNG, JPG, GIF, WEBP)</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label>גיל</label>
              <input
                type="number"
                name="age"
                value={formData.age || ''}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label>מגדר</label>
              <select
                name="gender"
                value={formData.gender || ''}
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
              <label>מיקום</label>
              <select
                name="location"
                value={formData.location || ''}
                onChange={handleChange}
                className="form-input"
              >
                <option value="">בחר מיקום</option>
                {ISRAEL_LOCATIONS.map((loc) => (
                  <option key={loc.value} value={loc.value}>
                    {loc.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>גובה (ס"מ)</label>
              <input
                type="number"
                name="height"
                value={formData.height || ''}
                onChange={handleChange}
                className="form-input"
                placeholder="למשל: 175"
                min="100"
                max="250"
              />
            </div>

            <div className="form-group">
              <label>מצב תעסוקתי</label>
              <select
                name="employment_status"
                value={formData.employment_status || ''}
                onChange={handleChange}
                className="form-input"
              >
                <option value="">בחר מצב תעסוקתי</option>
                <option value="עובד/ת">עובד/ת</option>
                <option value="סטודנט/ית">סטודנט/ית</option>
                <option value="עובד/ת וסטודנט/ית">עובד/ת וסטודנט/ית</option>
                <option value="בחיפוש עבודה">בחיפוש עבודה</option>
                <option value="עצמאי/ת">עצמאי/ת</option>
                <option value="בפנסיה">בפנסיה</option>
                <option value="אחר">אחר</option>
              </select>
            </div>

            <div className="form-group">
              <label>טלפון</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone || ''}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label>כתובת</label>
              <input
                type="text"
                name="address"
                value={formData.address || ''}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label>על עצמי</label>
              <textarea
                name="bio"
                value={formData.bio || ''}
                onChange={handleChange}
                className="form-input"
                rows="6"
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary">שמור</button>
              <button 
                type="button" 
                onClick={() => setEditing(false)}
                className="btn btn-secondary"
              >
                ביטול
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-view">
        <div className="profile-header">
          <h1>הפרופיל שלי</h1>
          <button 
            onClick={() => setEditing(true)} 
            className="btn btn-primary profile-edit-btn"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.875rem 1.75rem',
              fontSize: 'var(--font-size-base)',
              fontWeight: 'var(--font-weight-semibold)',
              background: 'var(--gradient-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: 'var(--shadow-colored)'
            }}
          >
            ✏️ ערוך פרופיל
          </button>
        </div>

        <div className="profile-info">
          <div className="info-section profile-details-group">
            <h2>📋 כל הפרטים</h2>
            <div className="info-grid">
              <div className="info-item">
                <strong>שם:</strong> {user.full_name}
              </div>
              <div className="info-item">
                <strong>אימייל:</strong> {user.email}
              </div>
              <div className="info-item">
                <strong>טלפון:</strong> {user.phone || 'לא מוגדר'}
              </div>
              <div className="info-item">
                <strong>גיל:</strong> {user.age || 'לא מוגדר'}
              </div>
              <div className="info-item">
                <strong>מגדר:</strong> {user.gender === 'male' ? 'זכר' : user.gender === 'female' ? 'נקבה' : user.gender || 'לא מוגדר'}
              </div>
              <div className="info-item">
                <strong>מיקום:</strong> {user.location || 'לא מוגדר'}
              </div>
              {user.height && (
                <div className="info-item">
                  <strong>גובה:</strong> {user.height} ס"מ
                </div>
              )}
              {user.employment_status && (
                <div className="info-item">
                  <strong>מצב תעסוקתי:</strong> {user.employment_status}
                </div>
              )}
              <div className="info-item">
                <strong>כתובת:</strong> {user.address || 'לא מוגדר'}
              </div>
              {user.bio && (
                <div className="info-item info-item-full">
                  <strong>על עצמי:</strong>
                  <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>{user.bio}</p>
                </div>
              )}
            </div>
          </div>

          <div className="info-section">
            <h2>קוד ההמלצה שלי</h2>
            <div className="referral-code">
              <code>{user.referral_code}</code>
              <button 
                onClick={async () => {
                  try {
                    if (navigator.clipboard && navigator.clipboard.writeText) {
                      await navigator.clipboard.writeText(user.referral_code);
                      alert("קוד הועתק ללוח!");
                    } else {
                      // Fallback for older browsers
                      const textArea = document.createElement('textarea');
                      textArea.value = user.referral_code;
                      textArea.style.position = 'fixed';
                      textArea.style.left = '-999999px';
                      document.body.appendChild(textArea);
                      textArea.select();
                      try {
                        document.execCommand('copy');
                        alert("קוד הועתק ללוח!");
                      } catch (err) {
                        alert("לא ניתן להעתיק אוטומטית. הקוד הוא: " + user.referral_code);
                      }
                      document.body.removeChild(textArea);
                    }
                  } catch (err) {
                    // Final fallback - show the code
                    alert("לא ניתן להעתיק אוטומטית. הקוד הוא: " + user.referral_code);
                  }
                }}
                className="btn btn-small"
              >
                📋 העתק קוד
              </button>
            </div>
            <div className="referral-link" style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(255, 107, 157, 0.05)', borderRadius: '8px', border: '1px solid rgba(255, 107, 157, 0.2)' }}>
              <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>
                🔗 לינק לשיתוף:
              </p>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <code style={{ flex: 1, minWidth: '200px', padding: '0.5rem', background: 'white', borderRadius: '4px', fontSize: '0.85rem', wordBreak: 'break-all' }}>
                  {window.location.origin}/register?ref={user.referral_code}
                </code>
                <button 
                  onClick={async () => {
                    const referralLink = `${window.location.origin}/register?ref=${user.referral_code}`;
                    try {
                      if (navigator.clipboard && navigator.clipboard.writeText) {
                        await navigator.clipboard.writeText(referralLink);
                        alert("לינק הועתק ללוח!");
                      } else {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = referralLink;
                        textArea.style.position = 'fixed';
                        textArea.style.left = '-999999px';
                        document.body.appendChild(textArea);
                        textArea.select();
                        try {
                          document.execCommand('copy');
                          alert("לינק הועתק ללוח!");
                        } catch (err) {
                          alert("לא ניתן להעתיק אוטומטית. הלינק הוא: " + referralLink);
                        }
                        document.body.removeChild(textArea);
                      }
                    } catch (err) {
                      alert("לא ניתן להעתיק אוטומטית. הלינק הוא: " + referralLink);
                    }
                  }}
                  className="btn btn-small"
                  style={{ whiteSpace: 'nowrap' }}
                >
                  📋 העתק לינק
                </button>
              </div>
            </div>
            <p className="referral-hint">שתף קוד זה או את הלינק עם חברים כדי שיוכלו להצטרף</p>
          </div>

          {user.referred_by && (
            <div className="info-section">
              <h2>הומלצתי על ידי</h2>
              <div className="referrer-info">
                <p>
                  <strong>
                    <button
                      onClick={() => navigate(`/profile/${user.referred_by.id}`)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--color-primary)',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        fontSize: 'inherit',
                        fontFamily: 'inherit',
                        fontWeight: 'bold',
                        padding: 0
                      }}
                    >
                      {user.referred_by.name}
                    </button>
                  </strong>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;

