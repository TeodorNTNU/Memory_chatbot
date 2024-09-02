# # signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import ChatMessage
# 
# @receiver(post_save, sender=ChatMessage)
# def log_message_creation(sender, instance, created, **kwargs):
#     if created:
#         print(f"New message added: {instance.user_response or instance.ai_response}")
#     else:
#         print(f"Message updated: {instance.user_response or instance.ai_response}")
