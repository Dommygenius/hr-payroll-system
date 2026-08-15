from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.core.models import Company
from apps.employees.models import Employee

User = get_user_model()


@pytest.mark.django_db
class TestApiTenantHardening:
    def test_cannot_patch_own_company_or_role(self, authenticated_client, admin_user):
        other = Company.objects.create(name='Other Co', slug='other-co')
        response = authenticated_client.patch(
            f'/api/v1/auth/users/{admin_user.pk}/',
            {'company': other.pk, 'role': 'employee'},
            format='json',
        )
        assert response.status_code in (200, 400)
        admin_user.refresh_from_db()
        assert admin_user.company_id != other.pk
        assert admin_user.role == 'super_admin'

    def test_company_api_is_read_only(self, authenticated_client, company):
        response = authenticated_client.patch(
            f'/api/v1/core/companies/{company.pk}/',
            {'is_active': False, 'slug': 'hijacked'},
            format='json',
        )
        assert response.status_code == 405
        company.refresh_from_db()
        assert company.is_active is True
        assert company.slug == 'acme-corp'


@pytest.mark.django_db
class TestPortalIsolation:
    def test_user_without_company_cannot_enter_tenant_portal(self, company):
        company.slug = 'acme-corp'
        company.save(update_fields=['slug'])
        stray = User.objects.create_user(
            username='stray',
            email='stray@example.com',
            password='Secure@123456',
            role=UserRole.EMPLOYEE,
        )
        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(stray)
        response = client.get('/t/acme-corp/dashboard/')
        assert response.status_code == 403

    def test_employee_cannot_create_payroll(self, company):
        company.slug = 'acme-corp'
        company.save(update_fields=['slug'])
        emp_user = User.objects.create_user(
            username='emp1',
            email='emp1@acme.com',
            password='Secure@123456',
            company=company,
            role=UserRole.EMPLOYEE,
        )
        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(emp_user)
        response = client.get('/t/acme-corp/module/payroll/runs/create/')
        assert response.status_code == 403

    def test_lockout_blocks_login(self, company):
        User.objects.create_user(
            username='locked',
            email='locked@acme.com',
            password='Secure@123456',
            company=company,
            role=UserRole.HR_ADMIN,
            failed_login_attempts=9,
            locked_until=timezone.now() + timedelta(minutes=30),
        )
        client = Client(HTTP_HOST='127.0.0.1')
        response = client.post(
            '/t/acme-corp/accounts/login/',
            {'username': 'locked@acme.com', 'password': 'Secure@123456'},
        )
        assert response.status_code != 303
        assert '_auth_user_id' not in client.session


@pytest.mark.django_db
class TestXssEscape:
    def test_script_in_employee_name_is_escaped(self, admin_user, company):
        Employee.objects.create(
            company=company,
            employee_id='XSS-1',
            first_name='</script><script>alert(1)</script>',
            last_name='N',
            email='xss@acme.com',
            date_joined='2024-01-01',
        )
        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(admin_user)
        response = client.get('/t/acme-corp/module/employees/list/')
        assert response.status_code == 200
        content = response.content.decode()
        assert '</script><script>alert(1)</script>' not in content
        assert '\\u003c' in content
