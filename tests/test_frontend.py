import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.dashboard.module_config import MODULES

User = get_user_model()
TENANT_PREFIX = '/t/acme-corp'


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
    elif not user.company_id:
        user.company = company
        user.save(update_fields=['company'])
    company.slug = 'acme-corp'
    company.save(update_fields=['slug'])
    client = Client(HTTP_HOST='127.0.0.1')
    client.force_login(user)
    return client


@pytest.mark.django_db
class TestFrontendRoutes:
    def test_all_module_routes_load(self, web_client):
        routes = [
            f'{TENANT_PREFIX}/dashboard/',
            f'{TENANT_PREFIX}/module/reports/',
            f'{TENANT_PREFIX}/module/ai/',
            f'{TENANT_PREFIX}/accounts/profile/',
        ]
        for mod, cfg in MODULES.items():
            routes.append(f'{TENANT_PREFIX}/module/{mod}/')
            for tab in cfg['tabs']:
                routes.append(f'{TENANT_PREFIX}/module/{mod}/{tab["key"]}/')
                if not tab.get('special'):
                    routes.append(f'{TENANT_PREFIX}/module/{mod}/{tab["key"]}/create/')

        for path in routes:
            response = web_client.get(path)
            assert response.status_code == 200, f'{path} returned {response.status_code}'

    def test_dashboard_has_key_sections(self, web_client):
        response = web_client.get(f'{TENANT_PREFIX}/dashboard/')
        assert b'welcome-banner' in response.content
        assert b'stat-card' in response.content

    def test_logout_requires_post(self, web_client):
        response = web_client.get(f'{TENANT_PREFIX}/accounts/logout/')
        assert response.status_code in (405, 302)

        response = web_client.post(f'{TENANT_PREFIX}/accounts/logout/')
        assert response.status_code == 302

    def test_password_change_page(self, web_client):
        response = web_client.get(f'{TENANT_PREFIX}/accounts/password-change/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestSaaSTenant:
    def test_tenant_registration_creates_portal(self, client):
        response = client.post('/register/', {
            'company_name': 'Beta HR Ltd',
            'company_slug': 'beta-hr',
            'first_name': 'Jane',
            'last_name': 'Admin',
            'admin_email': 'jane@betahr.com',
            'password1': 'Secure@123456',
            'password2': 'Secure@123456',
        }, HTTP_HOST='127.0.0.1')
        assert response.status_code == 200
        from apps.core.models import Company
        assert Company.objects.filter(slug='beta-hr').exists()
        assert b'Go to my dashboard' in response.content

    def test_tenant_portal_loads(self, client):
        client.post('/register/', {
            'company_name': 'Gamma Inc',
            'company_slug': 'gamma-inc',
            'first_name': 'Tom',
            'last_name': 'Owner',
            'admin_email': 'tom@gammainc.com',
            'password1': 'Secure@123456',
            'password2': 'Secure@123456',
        }, HTTP_HOST='127.0.0.1')
        response = client.get('/t/gamma-inc/dashboard/', HTTP_HOST='127.0.0.1')
        assert response.status_code in (200, 302)
