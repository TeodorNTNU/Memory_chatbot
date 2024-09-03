// MessageInput.jsx
import React, { useState } from 'react';
import { sendMessage } from '../services/api'; // Import the sendMessage function
import '../styles/MessageInput.css';

const MessageInput = ({ conversationId, onNewMessage, setConversationId }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSendMessage = async () => {
    console.log("Send message triggered");  // Add this line
    if (!inputMessage.trim()) return; // Don't send if the input is empty

    // Prevent duplicate requests by checking if a message is already being sent
    if (isSending) return;

    setIsSending(true);

    try {
      // Display the user message immediately
      onNewMessage(inputMessage);

      // Send message (the function handles creating a new conversation if needed)
      const response = await sendMessage(conversationId, inputMessage);

      // If a new conversation was created, update the conversationId in the parent component
      if (!conversationId && response.conversation_id) {
        setConversationId({ id: response.conversation_id, title: response.title }); // Update with new conversation object
      }

      setInputMessage(''); // Clear the input after sending
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.'); // Show user-friendly error message
    } finally {
      setIsSending(false); // Reset sending status after completion
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="message-input">
      <textarea
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message here..."
        rows={2}
        className="input-textarea"
      />
      <button onClick={handleSendMessage} disabled={isSending} className="send-button">
        Send
      </button>
    </div>
  );
};

export default MessageInput;

