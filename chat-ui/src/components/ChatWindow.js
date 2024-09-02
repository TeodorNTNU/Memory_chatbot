import React from 'react';
import '../styles/ChatWindow.css'; // Update the path


const ChatWindow = ({ messages }) => {
  return (
    <div className="chat-window">
      <h2>Chat</h2>
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={msg.user_response ? 'message user' : 'message ai'}>
            {msg.user_response || msg.ai_response}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatWindow;