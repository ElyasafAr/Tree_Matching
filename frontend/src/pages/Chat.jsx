import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { chatAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Chat.css';

const Chat = () => {
  const { chatId } = useParams();
  const { user: currentUser } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (chatId) {
      loadChatMessages(chatId);
    }
  }, [chatId]);

  // Auto-refresh messages every 5 seconds
  useEffect(() => {
    if (selectedChat) {
      const interval = setInterval(() => {
        loadChatMessages(selectedChat.id, false);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedChat]);

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
        const chat = conversations.find(c => c.id === parseInt(id));
        setSelectedChat(chat);
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
      alert("שגיאה בשליחת הודעה");
    }
  };

  if (loading) return <div className="loading">טוען שיחות...</div>;

  return (
    <div className="chat-container">
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

      <div className="chat-main">
        {!selectedChat ? (
          <div className="no-chat-selected">
            <h3>בחר שיחה מהרשימה</h3>
          </div>
        ) : (
          <>
            <div className="chat-header">
              <h3>{selectedChat.other_user?.name}</h3>
            </div>

            <div className="messages-container">
              {messages.map(msg => (
                <div
                  key={msg.id}
                  className={`message ${msg.sender_id === currentUser.id ? 'sent' : 'received'}`}
                >
                  <div className="message-content">{msg.content}</div>
                  <div className="message-time">
                    {new Date(msg.sent_at).toLocaleTimeString('he-IL', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              ))}
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
    </div>
  );
};

export default Chat;

