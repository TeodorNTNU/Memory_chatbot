import axios from 'axios';

// Set the base URL for the Django backend API
const API_BASE_URL = 'http://localhost:8000/api'; // Replace with your Django backend URL

// Function to get all conversations for the logged-in user
export const getConversations = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/get-conversations/`, {
      headers: {
        Authorization: `Token ${localStorage.getItem('token')}`, // Retrieve the token from localStorage
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching conversations:', error);
    throw error;
  }
};

// Function to create a new conversation
export const createConversation = async (initialMessage) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/create-conversation/`,
      { initial_message: initialMessage },
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('token')}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error creating conversation:', error);
    throw error;
  }
};

// Function to handle sending a message
export const sendMessage = async (conversationId, inputMessage) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/handle-message/`,
      {
        input_message: inputMessage,
        conversation_id: conversationId,
      },
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('token')}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};
