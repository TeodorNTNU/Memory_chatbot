// App.jsx
import React, { useState, useEffect } from 'react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from '@chatscope/chat-ui-kit-react';
import ConversationList from './components/ConversationList';
import NewConversationButton from './components/NewConversationButton';

import {
  getConversations,
  createConversation,
  sendMessage,
  getChatHistory,
} from './services/api';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  // Fetch conversations when the component mounts
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const data = await getConversations();
        setConversations(data);

        if (data.length > 0) {
          // Set the first conversation as the current one
          setCurrentConversationId(data[0].id);
          fetchChatHistory(data[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch conversations:', error);
      }
    };

    fetchConversations();
  }, []);

  // Fetch chat history for a selected conversation
  const fetchChatHistory = async (conversationId) => {
    try {
      const chatHistory = await getChatHistory(conversationId);
      const formattedMessages = chatHistory.map((chat) => ({
        message: chat.message,
        sender: chat.sender,
        direction: chat.sender === 'user' ? 'outgoing' : 'incoming',
      }));
      setMessages(formattedMessages);
      console.log('Fetched messages:', formattedMessages); // Debugging line
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  // Handle sending a new message
  const handleSend = async (message) => {
    if (!currentConversationId) {
      console.error('No conversation selected');
      return;
    }

    const newMessage = {
      message,
      sender: 'user',
      direction: 'outgoing',
    };
    setMessages((prevMessages) => [...prevMessages, newMessage]);

    try {
      setTyping(true);
      const response = await sendMessage(currentConversationId, message);
      const botMessage = {
        message: response.message,
        sender: 'bot',
        direction: 'incoming',
      };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
      console.log('Updated messages after sending:', messages); // Debugging line
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setTyping(false);
    }
  };

  // Handle selecting a conversation
  const handleSelectConversation = (conversation) => {
    setCurrentConversationId(conversation.id);
    fetchChatHistory(conversation.id);
  };

  // Handle creating a new conversation
  const handleNewConversation = async () => {
    try {
      const initialMessage = "Hello, this is a new conversation.";
      const newConversation = await createConversation(initialMessage);
      setConversations((prevConversations) => [...prevConversations, newConversation]);
      setCurrentConversationId(newConversation.id);
      setMessages([
        {
          message: initialMessage,
          sender: 'user',
          direction: 'outgoing',
        },
      ]);
    } catch (error) {
      console.error('Failed to create new conversation:', error);
    }
  };

  return (
    <div className="App">
      <div className="main-container">
        <div className="conversation-list-container">
          <ConversationList onSelectConversation={handleSelectConversation} />
          <NewConversationButton onNewConversation={handleNewConversation} />
        </div>
        <div className="chat-window-container">
          <MainContainer>
            <ChatContainer>
              <MessageList
                typingIndicator={typing ? <TypingIndicator content="ChatGPT is typing..." /> : null}
                style={{ overflowY: 'auto', height: '100%' }} // Inline style to ensure scrollability
              >
                {messages.map((message, i) => (
                  <Message
                    key={i}
                    model={{
                      message: message.message,
                      sentTime: 'just now',
                      sender: message.sender,
                      direction: message.direction,
                    }}
                  />
                ))}
              </MessageList>
              <MessageInput placeholder="Type your message here" onSend={handleSend} />
            </ChatContainer>
          </MainContainer>
        </div>
      </div>
    </div>
  );
};

export default App;
