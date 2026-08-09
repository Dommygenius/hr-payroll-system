"""API and dashboard isolation / production-hardening tests."""
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.core.models import Company
from apps.core.tenant import bootstrap_tenant
from apps.employees.models import Employee
from apps.leave.models import LeaveRequest, LeaveType

User = get_user_model()


@pytest.mark.django_db
class TestAPITenantIsolation:
    def test_employee_list_does_not_leak_other_tenant(self, company):
        company.slug = 'acme-corp'
        company.save(update_fields=['slug'])

        acme_user = User.objects.create_user(
            username='acme_api',
            email='acme_api@test.com',
            password='Secure@123456',
            company=company,
            role='hr_admin',
        )
        Employee.objects.create(
            company=company,
            employee_id='ACME-10',
            first_name='Acme',
            last_name='Staff',
            email='staff@acme.test',
            date_joined=date(2024, 1, 1),
        )

        newly, newly_user = bootstrap_tenant(
            company_name='Newly Ltd',
            slug='newly-api',
            admin_email='api@newly.test',
            password='Secure@123456',
            first_name='New',
            last_name='Boss',
        )

        client = APIClient()
        client.force_authenticate(user=newly_user)
        response = client.get('/api/v1/employees/')
        assert response.status_code == 200
        ids = [row.get('employee_id') for row in response.data.get('results', response.data)]
        assert 'ACME-10' not in ids
        assert all(
            (row.get('company') == str(newly.id) or row.get('company') == newly.id)
            for row in response.data.get('results', response.data)
            if isinstance(row, dict) and 'company' in row
        )

        # Cross-tenant company list must only show own company
        companies = client.get('/api/v1/core/companies/')
        assert companies.status_code == 200
        results = companies.data.get('results', companies.data)
        assert len(results) == 1
        assert results[0]['slug'] == 'newly-api'

        # Acme user cannot see Newly employees either
        client.force_authenticate(user=acme_user)
        response = client.get('/api/v1/employees/')
        assert response.status_code == 200
        emails = [row.get('email') for row in response.data.get('results', response.data)]
        assert 'api@newly.test' not in emails

    def test_leave_request_create_stamps_user_company(self, company):
        user = User.objects.create_user(
            username='leave_api',
            email='leave_api@test.com',
            password='Secure@123456',
            company=company,
            role='hr_admin',
        )
        emp = Employee.objects.create(
            company=company,
            employee_id='E-L1',
            first_name='Lee',
            last_name='Ave',
            email='lee@test.com',
            date_joined=date(2024, 1, 1),
        )
        lt = LeaveType.objects.create(company=company, name='Annual', code='AN', days_per_year=20)
        other = Company.objects.create(name='Other Co', slug='other-co')

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/v1/leave/requests/', {
            'company': str(other.id),  # attempt overwrite
            'employee': str(emp.id),
            'leave_type': str(lt.id),
            'start_date': '2026-09-01',
            'end_date': '2026-09-03',
            'days_requested': '3.0',
            'reason': 'Family trip',
            'status': 'pending',
        }, format='json')
        assert response.status_code in (200, 201)
        req = LeaveRequest.objects.get(pk=response.data['id'])
        assert req.company_id == company.id
        assert req.company_id != other.id


@pytest.mark.django_db
class TestDashboardFailClosed:
    def test_module_routes_for_tenant_user(self, client, company):
        company.slug = 'acme-corp'
        company.save(update_fields=['slug'])
        user = User.objects.create_user(
            username='dash_user',
            email='dash_user@test.com',
            password='Secure@123456',
            company=company,
            role='hr_admin',
        )
        client.force_login(user)
        for path in (
            '/t/acme-corp/dashboard/',
            '/t/acme-corp/module/employees/',
            '/t/acme-corp/module/leave/requests/',
            '/t/acme-corp/module/ai/',
            '/t/acme-corp/accounts/profile/',
        ):
            response = client.get(path)
            assert response.status_code == 200, path
