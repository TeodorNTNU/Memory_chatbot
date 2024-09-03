import React, { useState, useCallback } from 'react';
import ConversationList from './components/ConversationList';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import NewChatButton from './components/NewChatButton';
import './App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { getChatHistory, sendMessage } from './services/api'; // Import required functions

const App = () => {
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Function to fetch messages for the selected conversation
  const fetchMessages = useCallback(async () => {
    if (!selectedConversation) return;

    setLoading(true); // Set loading to true before starting the fetch

    try {
      const data = await getChatHistory(selectedConversation.id);
      if (Array.isArray(data)) {
        setMessages(data);
        setError(null); // Clear any previous errors on success
      } else {
        throw new Error('Fetched data is not an array');
      }
    } catch (err) {
      console.error("Error fetching chat history:", err);
      setError('Error fetching chat history');
    } finally {
      setLoading(false); // Set loading to false after the fetch completes or fails
    }
  }, [selectedConversation]);

  // Fetch messages when a new conversation is selected
  const handleSelectConversation = (conversation) => {
    setSelectedConversation(conversation);
    setMessages([]); // Reset messages when a new conversation is selected
    fetchMessages(); // Fetch messages for the selected conversation
  };

  // Handle sending a new message
  const handleNewMessage = async (message) => {
    setLoading(true); // Set loading to true before sending the message

    try {
      const response = await sendMessage(
        selectedConversation ? selectedConversation.id : null,
        message
      );
      if (response && response.response) {
        setError(null); // Clear any previous errors on success

        // Fetch updated chat history after receiving AI response
        fetchMessages();

        if (!selectedConversation) {
          // If no conversation was previously selected, set the new one
          setSelectedConversation({
            id: response.conversation_id,
            title: response.title,
          });
        }
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Failed to fetch AI response:', error);
      setError('Failed to fetch AI response');
    } finally {
      setLoading(false); // Set loading to false after the message is sent or fails
    }
  };

  const handleResetChat = () => {
    setSelectedConversation(null);
    setMessages([]);
    setError(null); // Clear any previous errors on reset
  };

  return (
    <div className="App">
      <h1>Best Chatbot Ever</h1>
      <div className="main-container">

        {/* Sidebar with New Chat Button on top of Conversation List */}
        <div className="sidebar">
          <NewChatButton onResetChat={handleResetChat} />
          <ConversationList 
            onSelectConversation={handleSelectConversation} 
          />
        </div>

        {/* Chat Section */}
        <div className="chat-section">
          <ChatWindow 
            messages={messages} 
            loading={loading} 
            error={error}
          />
          <MessageInput 
            conversationId={selectedConversation ? selectedConversation.id : null} 
            onNewMessage={handleNewMessage}
            setConversationId={setSelectedConversation} // Pass setSelectedConversation as setConversationId
          />
        </div>
      </div>
    </div>
  );
};

export default App;
