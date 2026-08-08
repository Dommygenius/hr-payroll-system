import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.ai_features.gemini_client import GeminiClient
from apps.ai_features.services import HRChatbotService
from apps.employees.models import Employee
from apps.leave.models import LeaveRequest, LeaveType


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


@pytest.mark.django_db
class TestLeaveDutyAssist:
    def _seed_pending(self, company):
        leave_type = LeaveType.objects.create(
            company=company, name='Annual Leave', code='AL', days_per_year=21,
        )
        employee = Employee.objects.create(
            company=company,
            employee_id='E100',
            first_name='Ada',
            last_name='Lovelace',
            email='ada@test.com',
            date_joined=date.today() - timedelta(days=365),
        )
        LeaveRequest.objects.create(
            company=company,
            employee=employee,
            leave_type=leave_type,
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=9),
            days_requested=Decimal('3.0'),
            reason='Family event out of town',
            status=LeaveRequest.Status.PENDING,
        )
        return employee

    def test_context_includes_pending_approvals_for_manager(self, admin_user):
        self._seed_pending(admin_user.company)
        ctx = HRChatbotService._user_context(admin_user)
        assert ctx['can_manage_leave'] is True
        assert ctx['pending_approvals_count'] == 1
        assert 'Ada' in ctx['pending_approvals'][0]['employee']
        assert 'Family event' in ctx['pending_approvals'][0]['reason']

    def test_summarize_pending_leave_fallback(self, admin_user, monkeypatch):
        self._seed_pending(admin_user.company)

        def fake_generate(*args, **kwargs):
            return {'ok': False, 'error': 'offline'}

        monkeypatch.setattr(GeminiClient, 'generate', fake_generate)
        result = HRChatbotService.respond('Summarize pending leave', user=admin_user)
        assert result['source'] == 'assistant'
        assert 'Pending leave approvals' in result['text']
        assert 'Ada Lovelace' in result['text']
        assert 'Family event out of town' in result['text']

    def test_draft_approval_note_fallback(self, admin_user, monkeypatch):
        self._seed_pending(admin_user.company)

        def fake_generate(*args, **kwargs):
            return {'ok': False, 'error': 'offline'}

        monkeypatch.setattr(GeminiClient, 'generate', fake_generate)
        result = HRChatbotService.respond('Draft an approval note', user=admin_user)
        assert 'Draft approval note' in result['text']
        assert 'Approved' in result['text']
        assert 'Family event' in result['text']

    def test_draft_rejection_note_fallback(self, admin_user, monkeypatch):
        self._seed_pending(admin_user.company)

        def fake_generate(*args, **kwargs):
            return {'ok': False, 'error': 'offline'}

        monkeypatch.setattr(GeminiClient, 'generate', fake_generate)
        result = HRChatbotService.respond('Draft a rejection note', user=admin_user)
        assert 'Draft rejection note' in result['text']
        assert 'Unable to approve' in result['text']
