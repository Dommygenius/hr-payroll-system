import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def company(db):
    from apps.core.models import Company
    return Company.objects.create(name='Test Corp', slug='acme-corp')


@pytest.fixture
def admin_user(db, company):
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='Test@12345678',
        company=company,
        role='super_admin',
        is_staff=True,
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
