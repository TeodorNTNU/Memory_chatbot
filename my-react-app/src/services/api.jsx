// services/api.js
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



export const sendMessage = async (conversationId, inputMessage) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/handle-message/`,
      {
        conversation_id: conversationId,
        input_message: inputMessage,
      },
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};


export const getChatHistory = async (conversationId) => {
  try {
      const response = await axios.get(`${API_BASE_URL}/chat-history/${conversationId}/`, {
          headers: {
              Authorization: `Token ${localStorage.getItem('token')}`,
          },
      });
      
      // Check if the fetched data contains 'messages' and if it's an array
      if (response.data && Array.isArray(response.data.messages)) {
          return response.data.messages;
      } else {
          throw new Error('Fetched data is not an array');
      }
  } catch (error) {
      console.error('Error fetching chat history:', error);
      throw error;
  }
};
