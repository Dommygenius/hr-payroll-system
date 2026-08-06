import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.dashboard.module_config import MODULES

User = get_user_model()


@pytest.fixture
def web_client(db, company):
    user = User.objects.filter(email='admin@acme.com').first()
    if not user:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@acme.com',
            password='Admin@123456',
            company=company,
        )
    client = Client(HTTP_HOST='127.0.0.1')
    client.force_login(user)
    return client


@pytest.mark.django_db
class TestFrontendRoutes:
    def test_all_module_routes_load(self, web_client):
        routes = ['/', '/dashboard/', '/module/reports/', '/module/ai/', '/accounts/profile/']
        for mod, cfg in MODULES.items():
            routes.append(f'/module/{mod}/')
            for tab in cfg['tabs']:
                routes.append(f'/module/{mod}/{tab["key"]}/')
                routes.append(f'/module/{mod}/{tab["key"]}/create/')

        for path in routes:
            response = web_client.get(path)
            assert response.status_code == 200, f'{path} returned {response.status_code}'

    def test_dashboard_has_key_sections(self, web_client):
        response = web_client.get('/')
        assert b'welcome-banner' in response.content
        assert b'stat-card' in response.content

    def test_logout_requires_post(self, web_client):
        response = web_client.get('/accounts/logout/')
        assert response.status_code in (405, 302)

        response = web_client.post('/accounts/logout/')
        assert response.status_code == 302

    def test_password_change_page(self, web_client):
        response = web_client.get('/accounts/password-change/')
        assert response.status_code == 200
