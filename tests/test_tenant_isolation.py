import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.ai_features.services import HRChatbotService
from apps.core.models import Company
from apps.core.tenant import bootstrap_tenant
from apps.employees.models import Employee
from apps.leave.models import LeaveBalance, LeaveType

User = get_user_model()


@pytest.mark.django_db
class TestTenantIsolation:
    def test_bootstrap_creates_isolated_tenant_data(self):
        company, user = bootstrap_tenant(
            company_name='Newly Ltd',
            slug='newly',
            admin_email='admin@newly.test',
            password='Secure@123456',
            first_name='Neo',
            last_name='Admin',
        )
        assert company.slug == 'newly'
        assert user.company_id == company.id
        assert Employee.objects.filter(company=company, user=user).exists()
        assert LeaveType.objects.filter(company=company).count() >= 3
        assert LeaveBalance.objects.filter(company=company, employee__user=user).exists()

    def test_ai_context_never_includes_other_tenant(self, company):
        """Acme context must not appear for Newly admin."""
        acme = company
        acme.name = 'Acme Corporation'
        acme.slug = 'acme-corp'
        acme.save()

        newly, newly_user = bootstrap_tenant(
            company_name='Newly Ltd',
            slug='newly',
            admin_email='boss@newly.test',
            password='Secure@123456',
            first_name='New',
            last_name='Boss',
        )

        # Seed an Acme employee that shares a lookalike email domain — still shouldn't leak
        Employee.objects.create(
            company=acme,
            employee_id='ACME-1',
            first_name='Acme',
            last_name='Worker',
            email='worker@acme.com',
            date_joined='2024-01-01',
        )

        ctx = HRChatbotService._user_context(newly_user)
        assert ctx['company_name'] == 'Newly Ltd'
        assert ctx['company_slug'] == 'newly'
        assert ctx.get('employee_name') == 'New Boss'
        assert 'Acme' not in (ctx.get('employee_name') or '')
        balances = ctx.get('leave_balances') or []
        assert balances  # Newly has its own leave balances
        assert all('Acme' not in b['type'] for b in balances)

    def test_cross_tenant_portal_redirects(self, company):
        company.slug = 'acme-corp'
        company.save(update_fields=['slug'])
        acme_user = User.objects.create_user(
            username='acmeadmin2',
            email='acmeadmin2@acme.com',
            password='Secure@123456',
            company=company,
            role='hr_admin',
        )
        newly, newly_user = bootstrap_tenant(
            company_name='Newly Ltd',
            slug='newly',
            admin_email='ceo@newly.test',
            password='Secure@123456',
        )

        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(acme_user)
        # Acme user trying to open Newly portal must be redirected to Acme
        response = client.get('/t/newly/dashboard/', follow=False)
        assert response.status_code == 302
        assert '/t/acme-corp/' in response['Location']

        client.logout()
        client.force_login(newly_user)
        response = client.get('/t/acme-corp/dashboard/', follow=False)
        assert response.status_code == 302
        assert '/t/newly/' in response['Location']

    def test_email_lookup_cannot_cross_companies(self, company):
        """Same email string on another company must not be used for AI context."""
        company.slug = 'acme-corp'
        company.name = 'Acme Corporation'
        company.save()

        newly, newly_user = bootstrap_tenant(
            company_name='Newly Ltd',
            slug='newly',
            admin_email='shared@example.com',
            password='Secure@123456',
            first_name='New',
            last_name='Owner',
        )

        # Fake Acme employee with same email (edge case)
        Employee.objects.create(
            company=company,
            employee_id='SHARED-1',
            first_name='Acme',
            last_name='Clone',
            email='shared@example.com',
            date_joined='2024-01-01',
        )

        ctx = HRChatbotService._user_context(newly_user)
        assert ctx['company_name'] == 'Newly Ltd'
        assert ctx.get('employee_name') == 'New Owner'
        assert ctx.get('employee_name') != 'Acme Clone'
