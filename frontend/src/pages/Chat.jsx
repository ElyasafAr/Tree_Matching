import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { chatAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import './Chat.css';

const Chat = () => {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const { error: showError, success: showSuccess, showConfirm } = useToast();
  const [conversations, setConversations] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);
  
  // Get user's timezone from browser
  const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  
  // Helper function to check if two dates are on the same day (in user's timezone)
  const isSameDay = (date1, date2) => {
    // Compare dates in user's timezone by converting to date strings
    const d1Str = date1.toLocaleDateString('en-CA', { timeZone: userTimeZone }); // YYYY-MM-DD format
    const d2Str = date2.toLocaleDateString('en-CA', { timeZone: userTimeZone });
    return d1Str === d2Str;
  };
  
  // Helper function to parse UTC date string correctly
  const parseUTCDate = (utcTimeString) => {
    if (!utcTimeString) return null;
    
    // Ensure the string is treated as UTC
    let timeString = utcTimeString;
    if (!timeString.endsWith('Z')) {
      const hasTimezoneOffset = /[+-]\d{2}:\d{2}$/.test(timeString);
      if (!hasTimezoneOffset) {
        timeString = timeString + 'Z';
      }
    }
    
    const date = new Date(timeString);
    return isNaN(date.getTime()) ? null : date;
  };
  
  // Helper function to format date and time according to user's timezone
  const formatMessageTime = (utcTimeString) => {
    if (!utcTimeString) return '';
    
    const messageDate = parseUTCDate(utcTimeString);
    if (!messageDate) {
      console.error('[TIMEZONE ERROR] Invalid date string:', utcTimeString);
      return '';
    }
    
    const now = new Date();
    
    const timeStr = messageDate.toLocaleTimeString('he-IL', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: userTimeZone
    });
    
    // If message is from today, show only time
    if (isSameDay(messageDate, now)) {
      return timeStr;
    }
    
    // Create yesterday date in user's timezone
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // If message is from yesterday
    if (isSameDay(messageDate, yesterday)) {
      return `אתמול, ${timeStr}`;
    }
    
    // Calculate days difference in user's timezone
    const messageDateStr = messageDate.toLocaleDateString('en-CA', { timeZone: userTimeZone });
    const todayStr = now.toLocaleDateString('en-CA', { timeZone: userTimeZone });
    const messageParts = messageDateStr.split('-').map(Number);
    const todayParts = todayStr.split('-').map(Number);
    const messageDayObj = new Date(messageParts[0], messageParts[1] - 1, messageParts[2]);
    const todayObj = new Date(todayParts[0], todayParts[1] - 1, todayParts[2]);
    const daysDiff = Math.floor((todayObj - messageDayObj) / (1000 * 60 * 60 * 24));
    
    // If message is from this week (last 7 days)
    if (daysDiff <= 7) {
      const dayName = messageDate.toLocaleDateString('he-IL', {
        weekday: 'long',
        timeZone: userTimeZone
      });
      return `${dayName}, ${timeStr}`;
    }
    
    // For older messages, show full date and time
    const dateStr = messageDate.toLocaleDateString('he-IL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      timeZone: userTimeZone
    });
    return `${dateStr}, ${timeStr}`;
  };
  
  // Helper function to check if we should show a date separator
  const shouldShowDateSeparator = (currentMsg, previousMsg) => {
    if (!previousMsg) return true; // First message always shows date
    
    const currentDate = parseUTCDate(currentMsg.sent_at);
    const previousDate = parseUTCDate(previousMsg.sent_at);
    
    if (!currentDate || !previousDate) return false;
    
    return !isSameDay(currentDate, previousDate);
  };
  
  // Helper function to format date separator
  const formatDateSeparator = (utcTimeString) => {
    if (!utcTimeString) return '';
    
    const messageDate = parseUTCDate(utcTimeString);
    if (!messageDate) return '';
    
    const now = new Date();
    
    // If message is from today
    if (isSameDay(messageDate, now)) {
      return 'היום';
    }
    
    // Create yesterday date in user's timezone
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // If message is from yesterday
    if (isSameDay(messageDate, yesterday)) {
      return 'אתמול';
    }
    
    // Calculate days difference in user's timezone
    const messageDateStr = messageDate.toLocaleDateString('en-CA', { timeZone: userTimeZone });
    const todayStr = now.toLocaleDateString('en-CA', { timeZone: userTimeZone });
    const messageParts = messageDateStr.split('-').map(Number);
    const todayParts = todayStr.split('-').map(Number);
    const messageDayObj = new Date(messageParts[0], messageParts[1] - 1, messageParts[2]);
    const todayObj = new Date(todayParts[0], todayParts[1] - 1, todayParts[2]);
    const daysDiff = Math.floor((todayObj - messageDayObj) / (1000 * 60 * 60 * 24));
    
    // If message is from this week
    if (daysDiff <= 7) {
      return messageDate.toLocaleDateString('he-IL', {
        weekday: 'long',
        timeZone: userTimeZone
      });
    }
    
    // For older messages, show full date
    return messageDate.toLocaleDateString('he-IL', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      timeZone: userTimeZone
    });
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    // When chatId changes or conversations are loaded, load the specific chat
    if (chatId) {
      if (conversations.length > 0) {
        // Conversations already loaded, load the chat
        loadChatMessages(chatId);
      } else {
        // Wait for conversations to load first
        const checkAndLoad = async () => {
          if (conversations.length === 0) {
            await loadConversations();
          }
          loadChatMessages(chatId);
        };
        checkAndLoad();
      }
    }
  }, [chatId, conversations.length]);

  // Auto-refresh messages every 5 seconds
  useEffect(() => {
    if (selectedChat) {
      const interval = setInterval(() => {
        loadChatMessages(selectedChat.id, false);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedChat]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      const response = await chatAPI.getConversations();
      setConversations(response.data.conversations);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
    setLoading(false);
  };

  const loadChatMessages = async (id, setAsSelected = true) => {
    try {
      const response = await chatAPI.getMessages(id);
      setMessages(response.data.messages);
      if (setAsSelected) {
        // Try to find chat in conversations list
        let chat = conversations.find(c => c.id === parseInt(id));
        
        // If chat not found in list (new chat), reload conversations to get it
        if (!chat) {
          const convResponse = await chatAPI.getConversations();
          const updatedConversations = convResponse.data.conversations;
          setConversations(updatedConversations);
          chat = updatedConversations.find(c => c.id === parseInt(id));
        }
        
        if (chat) {
          setSelectedChat(chat);
        } else {
          console.error('Chat not found even after reloading conversations');
        }
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedChat) return;

    try {
      await chatAPI.sendMessage(selectedChat.other_user_id, newMessage);
      setNewMessage('');
      loadChatMessages(selectedChat.id, false);
      loadConversations(); // Refresh to update last message
    } catch (error) {
      showError("שגיאה בשליחת הודעה");
    }
  };

  const handleDeleteChat = async () => {
    if (!selectedChat) return;
    
    const confirmed = await showConfirm(
      `האם אתה בטוח שברצונך למחוק את השיחה עם ${selectedChat.other_user?.name}?`,
      null,
      null,
      'מחק',
      'ביטול'
    );
    
    if (!confirmed) {
      return;
    }

    try {
      await chatAPI.deleteChat(selectedChat.id);
      setSelectedChat(null);
      setMessages([]);
      loadConversations();
      navigate('/chat');
      showSuccess('השיחה נמחקה בהצלחה');
    } catch (error) {
      showError('שגיאה במחיקת השיחה');
    }
  };

  const handleViewProfile = () => {
    if (selectedChat?.other_user?.id) {
      navigate(`/user/${selectedChat.other_user.id}`);
    }
  };

  if (loading) return <div className="loading">טוען שיחות...</div>;

  return (
    <div className="chat-container">
      <div className="chat-main">
        {!selectedChat ? (
          <div className="no-chat-selected">
            <h3>בחר שיחה מהרשימה</h3>
          </div>
        ) : (
          <>
            <div className="chat-header">
              <h3>{selectedChat.other_user?.name}</h3>
              <div className="chat-header-actions">
                <button 
                  className="chat-header-btn"
                  onClick={handleViewProfile}
                  title="צפה בפרופיל"
                >
                  👤 פרופיל
                </button>
                <button 
                  className="chat-header-btn delete-btn"
                  onClick={handleDeleteChat}
                  title="מחק שיחה"
                >
                  🗑️ מחק
                </button>
              </div>
            </div>

            <div className="messages-container">
              {messages.map((msg, index) => {
                const previousMsg = index > 0 ? messages[index - 1] : null;
                const showDateSeparator = shouldShowDateSeparator(msg, previousMsg);
                
                return (
                  <div key={msg.id}>
                    {showDateSeparator && (
                      <div className="date-separator">
                        <span>{formatDateSeparator(msg.sent_at)}</span>
                      </div>
                    )}
                    <div
                      className={`message ${msg.sender_id === currentUser.id ? 'sent' : 'received'}`}
                    >
                      <div className="message-content">{msg.content}</div>
                      <div className="message-time">
                        {formatMessageTime(msg.sent_at)}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSendMessage} className="message-form">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="כתוב הודעה..."
                className="message-input"
              />
              <button type="submit" className="send-button">
                שלח 📤
              </button>
            </form>
          </>
        )}
      </div>

      <div className="chat-sidebar">
        <h2>שיחות</h2>
        {conversations.length === 0 ? (
          <div className="no-conversations">
            <p>עדיין אין שיחות</p>
          </div>
        ) : (
          <div className="conversations-list">
            {conversations.map(conv => (
              <div
                key={conv.id}
                className={`conversation-item ${selectedChat?.id === conv.id ? 'active' : ''}`}
                onClick={() => loadChatMessages(conv.id)}
              >
                <div className="conversation-avatar">
                  {conv.other_user?.profile_image ? (
                    <img src={conv.other_user.profile_image} alt={conv.other_user.name} />
                  ) : (
                    <div className="avatar-placeholder">{conv.other_user?.name[0]}</div>
                  )}
                </div>
                <div className="conversation-info">
                  <div className="conversation-name">{conv.other_user?.name}</div>
                  {conv.last_message && (
                    <div className="conversation-preview">
                      {conv.last_message.content.substring(0, 50)}...
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;

