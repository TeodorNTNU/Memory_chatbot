// ConversationList.jsx
import React, { useEffect, useState } from 'react';
import { getConversations } from '../services/api'; // Import the API function
import '../styles/ConversationList.css'; // Ensure the path to the CSS file is correct

const ConversationList = ({ onSelectConversation }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const data = await getConversations();
        setConversations(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch conversations:', error);
        setError('Failed to load conversations');
        setLoading(false);
      }
    };

    fetchConversations();
  }, []);

  return (
    <div className="conversation-list-container">
      <div className="conversation-list">
        <h2>Conversations</h2>
        {/* Show loading state */}
        {loading && <p>Loading conversations...</p>}

        {/* Show error message if there's an error */}
        {error && <p className="error">{error}</p>}

        {/* Render conversation list if loaded and no error */}
        <ul>
          {!loading && !error && conversations.map((conversation) => (
            <li 
              key={conversation.id} 
              onClick={() => onSelectConversation(conversation)}
              className="conversation-item"
            >
              {conversation.title}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ConversationList;
