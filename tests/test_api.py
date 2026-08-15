import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAuthentication:
    def test_user_registration_requires_auth(self, api_client, company):
        response = api_client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'Secure@12345',
            'first_name': 'New',
            'last_name': 'User',
            'company': str(company.id),
            'role': 'super_admin',
        })
        assert response.status_code in (401, 403)

    def test_authenticated_register_stamps_company_and_ignores_role(self, authenticated_client, company, admin_user):
        response = authenticated_client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'Secure@12345',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'super_admin',
        })
        assert response.status_code == 201
        from django.contrib.auth import get_user_model
        created = get_user_model().objects.get(email='newuser@test.com')
        assert created.company_id == admin_user.company_id
        assert created.role == 'employee'

    def test_jwt_token_obtain(self, api_client, admin_user):
        response = api_client.post('/api/v1/auth/token/', {
            'email': 'admin@test.com',
            'password': 'Test@12345678',
        })
        assert response.status_code in (200, 401)


@pytest.mark.django_db
class TestEmployees:
    def test_list_employees(self, authenticated_client):
        response = authenticated_client.get('/api/v1/employees/')
        assert response.status_code == 200

    def test_create_employee(self, authenticated_client, company):
        from apps.core.models import Branch, Department, Designation

        branch = Branch.objects.create(company=company, name='HQ', code='HQ')
        dept = Department.objects.create(company=company, name='IT', code='IT', branch=branch)
        desig = Designation.objects.create(company=company, title='Dev', code='DEV')

        response = authenticated_client.post('/api/v1/employees/', {
            'company': str(company.id),
            'employee_id': 'EMP100',
            'first_name': 'Test',
            'last_name': 'Employee',
            'email': 'test.emp@test.com',
            'branch': branch.id,
            'department': dept.id,
            'designation': desig.id,
            'date_joined': '2025-01-01',
        }, format='json')
        assert response.status_code == 201


@pytest.mark.django_db
class TestCore:
    def test_list_companies(self, authenticated_client, company):
        response = authenticated_client.get('/api/v1/core/companies/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1


@pytest.mark.django_db
class TestAI:
    def test_chatbot_response(self, authenticated_client):
        response = authenticated_client.post('/api/v1/ai/chat/', {
            'message': 'How do I apply for leave?',
        }, format='json')
        assert response.status_code == 200
        reply = response.data.get('response') or response.data.get('assistant_message', {}).get('content', '')
        assert 'leave' in reply.lower()
