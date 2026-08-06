from django.contrib import admin

from apps.ai_features.models import AIAnalysisJob, ChatbotConversation, ChatbotMessage


@admin.register(AIAnalysisJob)
class AIAnalysisJobAdmin(admin.ModelAdmin):
    list_display = ['job_type', 'status', 'requested_by', 'confidence_score', 'created_at']
    list_filter = ['company', 'job_type', 'status']


@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(ChatbotMessage)
class ChatbotMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content', 'created_at']
    list_filter = ['role']
