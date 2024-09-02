# chat/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Conversation, ChatMessage
from .custom_chat_history import DjangoChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from .views import generate_title
from .chatbot import runnable_with_history
from django.db import transaction
import time


class HandleMessageTestCase(APITestCase):
    def setUp(self):
        """
        Set up test data and environment for testing the handle_message view.
        """
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
        # Create a token for the user
        self.token = Token.objects.create(user=self.user)

        # Create a conversation for the user
        self.conversation = Conversation.objects.create(title='Test Conversation', user=self.user)
        
        # Initialize the client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def _invoke_message(self, input_message, conversation_id):
        """
        Helper method to invoke a message using runnable_with_history and return the AI response.
        """
        return runnable_with_history.invoke(
            {"input": input_message},
            config={"configurable": {"session_id": conversation_id}}
        )

    def test_handle_message_retrieve_and_continue_conversation(self):
        """
        Test that retrieving an existing conversation and continuing it works correctly using runnable_with_history.
        """
        # Setup: Create a conversation with initial messages
        conversation_id = str(self.conversation.id)
        input_message_1 = "Tell me about AI."
        input_message_2 = "How does it work?"

        # Simulate first input and AI response
        response_1 = self._invoke_message(input_message_1, conversation_id)
        print(f"First Response Content: {response_1.content}")  # Debug output

        # Assert that the first response was processed
        self.assertIsInstance(response_1, AIMessage)
        self.assertIn("AI", response_1.content)

        # Verify the conversation history before continuing
        history_before = DjangoChatMessageHistory(conversation_id=int(conversation_id)).messages
        print(f"Conversation History Before Continuation: {history_before}")  # Debug output
        self.assertEqual(len(history_before), 2)  # 1 Human + 1 AI

        # Simulate continuation of conversation
        response_2 = self._invoke_message(input_message_2, conversation_id)
        print(f"Second Response Content: {response_2.content}")  # Debug output

        # Assert that the AI remembers the context of the conversation
        self.assertIsInstance(response_2, AIMessage)
        self.assertIn("algorithm", response_2.content)  # More flexible assertion based on context

        # Retrieve stored messages
        stored_messages = ChatMessage.objects.filter(conversation=self.conversation).order_by('timestamp')
        print(f"Stored Messages After Continuation: {[(msg.user_response, msg.ai_response) for msg in stored_messages]}")  # Debug output

        # Verify the number of stored messages
        self.assertEqual(len(stored_messages), 4)  # Initial 2 messages + 2 from this test

        # Verify user and AI messages are stored correctly
        self._assert_stored_message(stored_messages[0], "Tell me about AI.", None)
        self._assert_stored_message(stored_messages[1], None, response_1.content.strip())
        self._assert_stored_message(stored_messages[2], "How does it work?", None)
        self._assert_stored_message(stored_messages[3], None, response_2.content.strip())

    def _assert_stored_message(self, message, expected_user_response, expected_ai_response):
        """
        Helper method to assert stored message contents.
        """
        self.assertEqual(message.user_response, expected_user_response)
        self.assertEqual(message.ai_response, expected_ai_response)

    def test_handle_message_invalid_conversation(self):
        """
        Test handling of an invalid conversation ID using runnable_with_history.
        """
        response = self.client.post(
            reverse('handle_message'),
            {'input_message': 'Tell me something about AI.', 'conversation_id': '9999'},  # Non-existent ID
            format='json'
        )
        print(f"Response Content: {response.content}")  # Debug output
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.json())

    def test_handle_message_missing_input(self):
        """
        Test handling of a request with missing input fields using runnable_with_history.
        """
        response = self.client.post(
            reverse('handle_message'),
            {'conversation_id': str(self.conversation.id)},  # Missing input_message
            format='json'
        )
        print(f"Response Content: {response.content}")  # Debug output
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def tearDown(self):
        """
        Clean up after tests.
        """
        self.client.credentials()  # Reset client authentication