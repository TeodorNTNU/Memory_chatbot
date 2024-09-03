from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
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
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging
import uuid
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser


logger = logging.getLogger(__name__)

# Load the tokenizer and model for title generation
tokenizer = AutoTokenizer.from_pretrained("czearing/article-title-generator")
model = AutoModelForSeq2SeqLM.from_pretrained("czearing/article-title-generator")


def generate_title(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=100, truncation=True)
    outputs = model.generate(**inputs, max_length=64, num_beams=5, early_stopping=True)
    generated_title = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_title



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_message(request):
    """
    Handle a chat message from the user, invoking the LLM with message history.
    If no conversation ID is provided, create a new conversation with a temporary title.
    """
    logger.info("handle_message function called")

    user = request.user
    input_message = request.data.get('input_message')
    session_id = request.data.get('conversation_id')

    logger.debug(f"Received input_message: {input_message}, session_id: {session_id}")

    if not input_message:
        logger.warning("Input message is missing")
        return JsonResponse({'error': 'Input message is required.'}, status=400)

    # Check if a conversation ID is provided
    if session_id:
        try:
            conversation = Conversation.objects.get(id=session_id, user=user)
            logger.info(f"Fetched existing conversation with ID: {session_id}")
        except Conversation.DoesNotExist:
            logger.warning(f"Conversation with ID {session_id} not found for user {user}")
            return JsonResponse({'error': 'Conversation not found.'}, status=404)
    else:
        # Generate a unique temporary title using UUID
        temporary_title = f"temporary_title_{uuid.uuid4().hex[:8]}"
        
        # Attempt to create a new conversation with a unique title
        try:
            conversation = Conversation.objects.create(user=user, title=temporary_title)
            session_id = conversation.id
            logger.info(f"Created a new conversation with ID: {session_id} and title: '{temporary_title}'")
        except Exception as e:
            logger.exception("Error occurred while creating a new conversation")
            return JsonResponse({"error": "Internal server error while creating conversation."}, status=500)

    try:
        logger.info(f"Invoking model with session ID: {str(session_id)} and input_message: {input_message}")

        # Invoke the model with the correct session ID
        response = runnable_with_history.invoke(
            {"input": input_message},
            config={"configurable": {"session_id": str(session_id)}}
        )

        logger.debug(f"Model response: {response.content}")

          # If a new conversation was created with "temporary_title", update it based on the AI response
        if "temporary_title" in conversation.title:
            generated_title = generate_title(response.content)
            
            # Ensure the title is unique by appending a random UUID if necessary
            if Conversation.objects.filter(title=generated_title).exists():
                generated_title = f"{generated_title}_{uuid.uuid4().hex[:8]}"
            
            conversation.title = generated_title
            conversation.save()
            logger.info(f"Updated conversation title to: {generated_title}")

        return JsonResponse({
            'response': response.content, 
            'conversation_id': session_id, 
            'title': conversation.title
        }, status=200)

    except Exception as e:
        logger.exception("Error occurred while handling message")
        return JsonResponse({'error': str(e)}, status=500)




class ChatHistoryAPIView(APIView):
    def get(self, request, conversation_id):
        try:
            # Fetch the conversation using get_object_or_404
            conversation = get_object_or_404(Conversation, id=conversation_id)

            # Serialize the conversation data
            conversation_data = ConversationSerializer(conversation).data

            # Fetch and serialize messages associated with the conversation
            messages = ChatMessage.objects.filter(conversation=conversation)
            messages_data = ChatMessageSerializer(messages, many=True).data

            # Combine conversation and message data in the response
            response_data = {
                'conversation': conversation_data,
                'messages': messages_data,
            }

            return JsonResponse(response_data, safe=False, status=200)

        except Exception as e:
            logger.exception("Error fetching chat history")
            return JsonResponse({'error': 'Internal server error while fetching chat history.'}, status=500)



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



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    """
    Create a new conversation and store it in the database with a generated title.
    """
    user = request.user
    initial_message = request.data.get('initial_message', None)  # Allow initial_message to be optional
    default_title = "temporary_title"
    try:
        # Create a placeholder title first
        new_conversation = Conversation.objects.create(user=user, title=default_title)

        if initial_message:
            # Generate a title based on the AI's first response to the initial message
            ai_response = "AI response based on initial_message"  # Placeholder AI response
            title = generate_title(ai_response)
            new_conversation.title = title
            new_conversation.save()

            # Store the initial message in ChatMessage
            ChatMessage.objects.create(conversation=new_conversation, user_response=initial_message, ai_response=ai_response)
        else:
            # If no initial message, keep the title as "Temporary Title" or handle differently
            title = default_title

        # Serialize the response
        response_data = {
            "conversation_id": new_conversation.id,
            "response": "New conversation created.",
            "title": title
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Log the exception details for debugging
        logger.exception("Error occurred while creating a new conversation")
        return Response({"error": "Internal server error while creating conversation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def create_conversation(request):
#     """
#     Create a new conversation with a title based on the AI response.
#     """
#     user = request.user
#     initial_message = request.data.get('initial_message')
# 
#     if not initial_message:
#         logger.error("Initial message is missing from request data.")
#         return JsonResponse({'error': 'Initial message is required to create a new conversation.'}, status=400)
# 
#     try:
#         # Step 1: Create a new conversation entry with a unique title placeholder
#         generated_title = generate_title(initial_message)  # Generating title based on initial input message
#         new_conversation = Conversation.objects.create(title=generated_title, user=user)
#         session_id = str(new_conversation.id)
#         logger.info(f"New Conversation Created: {new_conversation.id} with session ID {session_id}")
# 
#         # Step 2: Generate the AI response based on the initial user message
#         response = runnable_with_history.invoke(
#             {"input": initial_message},
#             config={"configurable": {"session_id": session_id}}  # Use the new conversation ID as the session id
#         )
#         ai_response = response.content
#         logger.info(f"AI Response Generated: {ai_response}")
#     except Exception as e:
#         logger.exception(f"Error generating AI response or creating conversation: {str(e)}")
#         return JsonResponse({'error': f"Error processing conversation: {str(e)}"}, status=500)
# 
#     try:
#         # Step 3: Add the initial message and AI response to the conversation history
#         chat_history = DjangoChatMessageHistory(conversation_id=new_conversation.id)
# 
#         # Check if the message exists before adding it
#         existing_messages = chat_history.messages
#         if not any(msg.content == initial_message for msg in existing_messages):
#             chat_history.add_message(HumanMessage(content=initial_message))
#             logger.info(f"Stored User Message: {initial_message}")
#         else:
#             logger.info(f"User Message Already Stored: {initial_message}")
# 
#         if not any(msg.content == ai_response for msg in existing_messages):
#             chat_history.add_message(AIMessage(content=ai_response))
#             logger.info(f"Stored AI Message: {ai_response}")
#         else:
#             logger.info(f"AI Message Already Stored: {ai_response}")
# 
#     except Exception as e:
#         logger.exception(f"Error storing messages: {str(e)}")
#         return JsonResponse({'error': f"Error storing messages: {str(e)}"}, status=500)
# 
#     return JsonResponse({'conversation_id': new_conversation.id, 'title': generated_title}, status=201)