from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist
from .models import ChatMessage, Conversation
from .serializers import ChatMessageSerializer, ConversationSerializer
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
from .chatbot import runnable_with_history
from .custom_chat_history import DjangoChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

# Load the tokenizer and model for title generation
tokenizer = AutoTokenizer.from_pretrained("czearing/article-title-generator")
model = AutoModelForSeq2SeqLM.from_pretrained("czearing/article-title-generator")

def generate_title(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=64, num_beams=5, early_stopping=True)
    generated_title = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_title


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_message(request):
    """
    Handle a chat message from the user, invoking the LLM with message history.
    """
    user = request.user
    input_message = request.data.get('input_message')
    conversation_id = request.data.get('conversation_id')

    if not input_message or conversation_id is None:
        return JsonResponse({'error': 'Input message and conversation ID are required.'}, status=400)

    try:
        # Ensure the conversation_id is an integer
        if not isinstance(conversation_id, int):
            raise ValueError("Invalid conversation ID format. It must be an integer.")

        # Log for debugging
        logger.info(f"Handling message for user {user.username}, conversation ID: {conversation_id}")

        # Invoke the model with the message and history
        response = runnable_with_history.invoke(
            {"input": input_message},
            config={"configurable": {"session_id": str(conversation_id)}}  # Convert to string if needed
        )

        return JsonResponse({'response': response.content}, status=200)
    except Exception as e:
        logger.exception("Error occurred while handling message")
        return JsonResponse({'error': 'Internal server error. Please try again later.'}, status=500)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_conversations(request):
    """
    Retrieve all existing conversations for the authenticated user.
    """
    user = request.user
    conversations = Conversation.objects.filter(user=user)
    serialized_conversations = ConversationSerializer(conversations, many=True)
    return JsonResponse(serialized_conversations.data, safe=False)


# Ensure you have a way to retrieve the session ID (conversation ID) from the user request
# For example, you might retrieve it from a request parameter or user session
def get_conversation_id_from_request(request):
    # Extract conversation ID from request data (for example, request.GET or request.POST)
    conversation_id = request.GET.get('conversation_id')  # or however you pass the ID
    if not conversation_id:
        raise ValueError("Conversation ID is required")
    return int(conversation_id)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    """
    Create a new conversation with a title based on the AI response.
    """
    user = request.user
    initial_message = request.data.get('initial_message')

    if not initial_message:
        logger.error("Initial message is missing from request data.")
        return JsonResponse({'error': 'Initial message is required to create a new conversation.'}, status=400)

    try:
        # Step 1: Create a new conversation entry with a unique title placeholder
        generated_title = generate_title(initial_message)  # Generating title based on initial input message
        new_conversation = Conversation.objects.create(title=generated_title, user=user)
        session_id = str(new_conversation.id)
        logger.info(f"New Conversation Created: {new_conversation.id} with session ID {session_id}")

        # Step 2: Generate the AI response based on the initial user message
        response = runnable_with_history.invoke(
            {"input": initial_message},
            config={"configurable": {"session_id": session_id}}  # Use the new conversation ID as the session id
        )
        ai_response = response.content
        logger.info(f"AI Response Generated: {ai_response}")
    except Exception as e:
        logger.exception(f"Error generating AI response or creating conversation: {str(e)}")
        return JsonResponse({'error': f"Error processing conversation: {str(e)}"}, status=500)

    try:
        # Step 3: Add the initial message and AI response to the conversation history
        chat_history = DjangoChatMessageHistory(conversation_id=new_conversation.id)

        # Check if the message exists before adding it
        existing_messages = chat_history.messages
        if not any(msg.content == initial_message for msg in existing_messages):
            chat_history.add_message(HumanMessage(content=initial_message))
            logger.info(f"Stored User Message: {initial_message}")
        else:
            logger.info(f"User Message Already Stored: {initial_message}")

        if not any(msg.content == ai_response for msg in existing_messages):
            chat_history.add_message(AIMessage(content=ai_response))
            logger.info(f"Stored AI Message: {ai_response}")
        else:
            logger.info(f"AI Message Already Stored: {ai_response}")

    except Exception as e:
        logger.exception(f"Error storing messages: {str(e)}")
        return JsonResponse({'error': f"Error storing messages: {str(e)}"}, status=500)

    return JsonResponse({'conversation_id': new_conversation.id, 'title': generated_title}, status=201)