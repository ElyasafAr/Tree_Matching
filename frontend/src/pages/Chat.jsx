import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { chatAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Chat.css';

const Chat = () => {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);

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
      alert("שגיאה בשליחת הודעה");
    }
  };

  const handleDeleteChat = async () => {
    if (!selectedChat) return;
    
    if (!confirm(`האם אתה בטוח שברצונך למחוק את השיחה עם ${selectedChat.other_user?.name}?`)) {
      return;
    }

    try {
      await chatAPI.deleteChat(selectedChat.id);
      setSelectedChat(null);
      setMessages([]);
      loadConversations();
      navigate('/chat');
      alert('השיחה נמחקה בהצלחה');
    } catch (error) {
      alert('שגיאה במחיקת השיחה');
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

