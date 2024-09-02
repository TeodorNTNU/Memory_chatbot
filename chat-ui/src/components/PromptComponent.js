import React, { useState } from 'react';
import { sendMessage, createConversation } from '../services/api';
import '../styles/PromptComponent.css'; // Update the path


const PromptComponent = ({ conversationId, onNewMessage, onNewConversation }) => {
  const [inputMessage, setInputMessage] = useState('');

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    try {
      let response;
      if (conversationId) {
        // Continue existing conversation
        response = await sendMessage(conversationId, inputMessage);
      } else {
        // Create a new conversation
        response = await createConversation(inputMessage);
        onNewConversation(response.conversation_id); // Pass the new conversation ID to the parent
      }

      onNewMessage({
        user_response: inputMessage,
        ai_response: response.response,
      });

      setInputMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  return (
    <div className="prompt-component">
      <textarea
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        placeholder="Type your message here..."
      />
      <button onClick={handleSendMessage}>Send</button>
    </div>
  );
};

export default PromptComponent;
