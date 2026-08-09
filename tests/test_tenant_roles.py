"""Tests for tenant role catalog and user role assignment."""
import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import UserRole
from apps.accounts.roles import (
    REQUIRED_ROLES,
    assignable_role_choices,
    default_enabled_roles,
    get_enabled_roles,
    set_enabled_roles,
)
from apps.dashboard.forms import UserAccountForm

User = get_user_model()


@pytest.mark.django_db
class TestTenantRoleCatalog:
    def test_default_roles_when_empty(self, company):
        company.enabled_roles = []
        company.save(update_fields=['enabled_roles'])
        roles = get_enabled_roles(company)
        assert UserRole.SUPER_ADMIN in roles
        assert UserRole.EMPLOYEE in roles
        assert set(default_enabled_roles()).issubset(set(roles)) or roles == default_enabled_roles()

    def test_super_admin_can_enable_and_remove_roles(self, company):
        set_enabled_roles(company, [UserRole.SUPER_ADMIN, UserRole.EMPLOYEE, UserRole.MANAGER])
        company.refresh_from_db()
        roles = get_enabled_roles(company)
        assert UserRole.MANAGER in roles
        assert UserRole.RECRUITER not in roles
        for required in REQUIRED_ROLES:
            assert required in roles

    def test_hr_cannot_assign_super_admin(self, company):
        hr = User.objects.create_user(
            username='hr_role',
            email='hr_role@test.com',
            password='Secure@123456',
            company=company,
            role=UserRole.HR_ADMIN,
        )
        choices = dict(assignable_role_choices(hr, company))
        assert UserRole.SUPER_ADMIN not in choices
        assert UserRole.EMPLOYEE in choices

    def test_promote_user_via_form(self, company):
        admin = User.objects.create_user(
            username='sa_role',
            email='sa_role@test.com',
            password='Secure@123456',
            company=company,
            role=UserRole.SUPER_ADMIN,
        )
        staff = User.objects.create_user(
            username='staff_role',
            email='staff_role@test.com',
            password='Secure@123456',
            company=company,
            role=UserRole.EMPLOYEE,
        )
        set_enabled_roles(company, [
            UserRole.SUPER_ADMIN, UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.HR_ADMIN,
        ])
        form = UserAccountForm(
            data={
                'email': staff.email,
                'username': staff.username,
                'first_name': 'Staff',
                'last_name': 'Member',
                'role': UserRole.MANAGER,
                'phone': '',
                'branch': '',
                'is_active': True,
                'password': '',
                'password_confirm': '',
            },
            instance=staff,
            company=company,
            request_user=admin,
        )
        assert form.is_valid(), form.errors
        updated = form.save()
        assert updated.role == UserRole.MANAGER

    def test_roles_catalog_page(self, client, company):
        company.slug = 'acme-corp'
        company.save(update_fields=['slug'])
        admin = User.objects.create_user(
            username='sa_catalog',
            email='sa_catalog@test.com',
            password='Secure@123456',
            company=company,
            role=UserRole.SUPER_ADMIN,
        )
        client.force_login(admin)
        response = client.get('/t/acme-corp/module/settings/roles/')
        assert response.status_code == 200
        assert b'Role Catalog' in response.content

        response = client.post('/t/acme-corp/module/settings/roles/', {
            'enabled_roles': [UserRole.SUPER_ADMIN, UserRole.EMPLOYEE, UserRole.AUDITOR],
        })
        assert response.status_code == 302
        company.refresh_from_db()
        assert UserRole.AUDITOR in get_enabled_roles(company)
