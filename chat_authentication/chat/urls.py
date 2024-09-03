from django.urls import path
from . import views

urlpatterns = [
    path('api/handle-message/', views.handle_message, name='handle_message'),
    path('api/get-conversations/', views.get_conversations, name='get_conversations'),  # Updated path
    path('api/create-conversation/', views.create_conversation, name='create_conversation'),  # Updated path
    path('api/chat-history/<int:conversation_id>/', views.ChatHistoryAPIView.as_view(), name='chat-history'),
]
