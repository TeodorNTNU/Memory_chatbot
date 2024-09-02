import React, { useEffect, useState } from 'react';
import { getConversations } from '../services/api';
import '../styles/ConversationList.css'; // Update the path


const ConversationList = ({ onSelectConversation }) => {
  const [conversations, setConversations] = useState([]);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const data = await getConversations();
        setConversations(data);
      } catch (error) {
        console.error('Failed to fetch conversations:', error);
      }
    };

    fetchConversations();
  }, []);

  return (
    <div className="conversation-list">
      <h2>Conversations</h2>
      <ul>
        {conversations.map((conversation) => (
          <li key={conversation.id} onClick={() => onSelectConversation(conversation)}>
            {conversation.title}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ConversationList;
