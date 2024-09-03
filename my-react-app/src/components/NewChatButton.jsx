// NewChatButton.jsx
import React from 'react';
import '../styles/NewChatButton.css'; // Make sure to create this CSS file for styling the button

const NewChatButton = ({ onResetChat }) => {
  return (
    <div className="new-chat-button-container">
      <button 
        className="start-new-chat-btn" 
        onClick={onResetChat}
        title="Start New Conversation"
      >
        +
      </button>
    </div>
  );
};

export default NewChatButton;
