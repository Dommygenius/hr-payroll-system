"""SaaS tenant URL helpers."""
from django.conf import settings
from django.urls import reverse


def get_portal_path(slug: str, path: str = '/') -> str:
    """Build tenant-scoped path, e.g. /t/acme-corp/dashboard/."""
    path = path if path.startswith('/') else f'/{path}'
    return f'/t/{slug}{path}'


def get_portal_url(slug: str, path: str = '/dashboard/', request=None) -> str:
    """Full absolute URL for a tenant portal."""
    relative = get_portal_path(slug, path)
    if request is not None:
        return request.build_absolute_uri(relative)
    base = getattr(settings, 'HRMS_PUBLIC_BASE_URL', '').rstrip('/')
    if base:
        return f'{base}{relative}'
    return relative


def reverse_tenant(viewname: str, tenant_slug: str, *args, **kwargs) -> str:
    """Reverse a named URL and prefix with tenant path."""
    url = reverse(viewname, args=args, kwargs=kwargs)
    return get_portal_path(tenant_slug, url)


def bootstrap_tenant(company_name: str, slug: str, admin_email: str, password: str,
                     first_name: str = '', last_name: str = ''):
    """Create company, HQ branch, and tenant admin user."""
    from django.contrib.auth import get_user_model
    from django.db import transaction

    from apps.accounts.models import UserRole
    from apps.core.models import Branch, Company

    User = get_user_model()
    username = admin_email.split('@')[0]
    base_username = username
    n = 1
    while User.objects.filter(username=username).exists():
        username = f'{base_username}{n}'
        n += 1

    with transaction.atomic():
        company = Company.objects.create(
            name=company_name,
            slug=slug,
            email=admin_email,
            is_active=True,
        )
        branch = Branch.objects.create(
            company=company,
            name='Head Office',
            code='HQ',
            is_headquarters=True,
            is_active=True,
        )
        user = User.objects.create_user(
            username=username,
            email=admin_email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            company=company,
            branch=branch,
            role=UserRole.HR_ADMIN,
            is_staff=True,
        )
    return company, user
