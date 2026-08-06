import pytest

from apps.ai_features.gemini_client import GeminiClient
from apps.ai_features.services import HRChatbotService


@pytest.mark.django_db
class TestGeminiChatbot:
    def test_gemini_client_configured(self, settings):
        settings.GEMINI_API_KEY = 'test-key'
        assert GeminiClient().configured is True

    def test_respond_returns_gemini_when_api_ok(self, admin_user, monkeypatch):
        def fake_generate(*args, **kwargs):
            return {'ok': True, 'text': 'Gemini says: apply via Leave Management.', 'model': 'gemini-3.5-flash'}

        monkeypatch.setattr(GeminiClient, 'generate', fake_generate)
        result = HRChatbotService.respond('How do I apply for leave?', user=admin_user)
        assert result['source'] == 'gemini'
        assert 'Leave Management' in result['text']

    def test_respond_falls_back_when_gemini_fails(self, admin_user, monkeypatch):
        def fake_generate(*args, **kwargs):
            return {'ok': False, 'error': 'quota', 'code': 429}

        monkeypatch.setattr(GeminiClient, 'generate', fake_generate)
        result = HRChatbotService.respond('How do I apply for leave?', user=admin_user)
        assert result['source'] == 'assistant'
        assert 'leave' in result['text'].lower()
