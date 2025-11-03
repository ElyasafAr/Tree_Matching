import { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';
import UserCard from '../components/UserCard';
import './Matches.css';

const Matches = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const response = await usersAPI.getMatches();
      setMatches(response.data.matches);
    } catch (error) {
      console.error('Error loading matches:', error);
    }
    setLoading(false);
  };

  return (
    <div className="matches-container">
      <div className="matches-header">
        <h1>ההתאמות שלי</h1>
        <p>משתמשים שאהבתם זה את זה 💚</p>
      </div>

      {loading ? (
        <div className="loading">טוען התאמות...</div>
      ) : matches.length === 0 ? (
        <div className="no-matches">
          <h2>עדיין אין התאמות</h2>
          <p>המשך לחפש ולתת לייקים למצוא את ההתאמה שלך!</p>
        </div>
      ) : (
        <div className="matches-grid">
          {matches.map(match => (
            <UserCard key={match.id} user={match} showActions={true} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Matches;

