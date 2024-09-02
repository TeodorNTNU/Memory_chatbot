import React, { useState } from 'react';
import ConversationList from './components/ConversationList';
import ChatWindow from './components/ChatWindow';
import PromptComponent from './components/PromptComponent';
import './App.css';

const App = () => {
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [messages, setMessages] = useState([]);

  const handleSelectConversation = (conversation) => {
    setSelectedConversationId(conversation.id);
    setMessages(conversation.messages || []); // Set existing messages
  };

  const handleNewMessage = (newMessage) => {
    setMessages((prevMessages) => [...prevMessages, newMessage]);
  };

  const handleNewConversation = (conversationId) => {
    setSelectedConversationId(conversationId);
    setMessages([]); // Start with an empty message list for new conversation
  };

  return (
    <div className="app">
      <div className="sidebar">
        <ConversationList onSelectConversation={handleSelectConversation} />
      </div>
      <div className="main">
        <ChatWindow messages={messages} />
        <PromptComponent
          conversationId={selectedConversationId}
          onNewMessage={handleNewMessage}
          onNewConversation={handleNewConversation}
        />
      </div>
    </div>
  );
};

export default App;
