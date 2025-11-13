import { useState, useEffect } from 'react';
import { usersAPI, uploadAPI } from '../services/api';
import UserCard from '../components/UserCard';
import ISRAEL_LOCATIONS from '../data/locations';
import './Home.css';

const Home = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    gender: '',
    min_age: '',
    max_age: '',
    location: ''
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadUsers();
    setSelectedUser(null); // Reset selection when filters or page change
  }, [filters, page]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 12 };
      
      // Add only non-empty filters
      if (filters.gender && filters.gender.trim()) {
        params.gender = filters.gender;
      }
      if (filters.min_age && filters.min_age !== '') {
        params.min_age = filters.min_age;
      }
      if (filters.max_age && filters.max_age !== '') {
        params.max_age = filters.max_age;
      }
      if (filters.location && filters.location.trim()) {
        params.location = filters.location;
      }
      
      console.log('[SEARCH] Sending params:', params);
      
      const response = await usersAPI.search(params);
      setUsers(response.data.users);
      setTotalPages(response.data.pagination.pages);
      
      console.log('[SEARCH] Received users:', response.data.users.length);
    } catch (error) {
      console.error('Error loading users:', error);
    }
    setLoading(false);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(1); // Reset to first page when filters change
  };

  const handleClearFilters = () => {
    setFilters({
      gender: '',
      min_age: '',
      max_age: '',
      location: ''
    });
    setPage(1);
  };

  return (
    <div className="home-container">
      <div className="home-header">
        <h1>חיפוש משתמשים</h1>
        <p>מצא את ההתאמה המושלמת שלך</p>
      </div>

      <div className="filters-container">
        <div className="filters">
          <select
            name="gender"
            value={filters.gender}
            onChange={handleFilterChange}
            className="filter-input"
          >
            <option value="">כל המגדרים</option>
            <option value="male">זכר</option>
            <option value="female">נקבה</option>
            <option value="other">אחר</option>
          </select>

          <input
            type="number"
            name="min_age"
            value={filters.min_age}
            onChange={handleFilterChange}
            placeholder="גיל מינימום"
            className="filter-input"
            min="18"
          />

          <input
            type="number"
            name="max_age"
            value={filters.max_age}
            onChange={handleFilterChange}
            placeholder="גיל מקסימום"
            className="filter-input"
            max="120"
          />

          <select
            name="location"
            value={filters.location}
            onChange={handleFilterChange}
            className="filter-input"
          >
            <option value="">כל המיקומים</option>
            {ISRAEL_LOCATIONS.map((loc) => (
              <option key={loc.value} value={loc.value}>
                {loc.label}
              </option>
            ))}
          </select>

          <button onClick={handleClearFilters} className="filter-clear">
            נקה סינון
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading">טוען משתמשים...</div>
      ) : users.length === 0 ? (
        <div className="no-results">
          <p>לא נמצאו משתמשים התואמים את הסינון</p>
        </div>
      ) : (
        <div className="search-layout">
          <div className="user-detail-panel">
            {selectedUser ? (
              <div className="user-detail-content">
                <UserCard user={selectedUser} showActions={true} onLike={loadUsers} />
              </div>
            ) : (
              <div className="no-user-selected">
                <h3>👆 בחר משתמש מהרשימה</h3>
                <p>לחץ על משתמש מהרשימה כדי לראות פרטים מלאים</p>
              </div>
            )}
          </div>

          <div className="users-sidebar">
            <h3>תוצאות חיפוש ({users.length})</h3>
            <div className="users-list-compact">
              {users.map(user => (
                <div
                  key={user.id}
                  className={`user-list-item ${selectedUser?.id === user.id ? 'active' : ''}`}
                  onClick={() => setSelectedUser(user)}
                >
                  <div className="user-list-avatar">
                    {user.profile_image ? (
                      <img src={uploadAPI.getImageUrl(user.profile_image)} alt={user.full_name} />
                    ) : (
                      <div className="avatar-placeholder-small">
                        {user.full_name?.[0] || '👤'}
                      </div>
                    )}
                  </div>
                  <div className="user-list-info">
                    <div className="user-list-name">{user.full_name}</div>
                    <div className="user-list-details">
                      {user.age && <span>גיל: {user.age}</span>}
                      {user.location && <span>📍 {user.location}</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {totalPages > 1 && (
              <div className="pagination-compact">
                <button 
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="pagination-btn-small"
                >
                  ←
                </button>
                
                <span className="pagination-info-small">
                  {page}/{totalPages}
                </span>
                
                <button 
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="pagination-btn-small"
                >
                  →
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;

