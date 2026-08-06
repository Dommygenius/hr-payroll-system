from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.ai_features.views import (
    AIAnalysisJobViewSet,
    ChatbotConversationViewSet,
    ChatbotMessageViewSet,
    ChatbotPostMessageView,
    TriggerAIJobView,
)

router = DefaultRouter()
router.register('jobs', AIAnalysisJobViewSet, basename='ai-analysis-job')
router.register('conversations', ChatbotConversationViewSet, basename='chatbot-conversation')
router.register('messages', ChatbotMessageViewSet, basename='chatbot-message')

urlpatterns = [
    path('chat/', ChatbotPostMessageView.as_view(), name='chatbot-post-message'),
    path('trigger/', TriggerAIJobView.as_view(), name='trigger-ai-job'),
    path('', include(router.urls)),
]
