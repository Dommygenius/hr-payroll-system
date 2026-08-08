"""Tenant resolution middleware for SaaS multi-tenancy."""
import re

from django.http import Http404
from django.shortcuts import redirect

from apps.core.models import Company


TENANT_PATH_RE = re.compile(r'^/t/(?P<slug>[-\w]+)(?P<rest>/.*)?$', re.I)


class TenantMiddleware:
    """
    Resolve tenant from /t/<slug>/ path prefix or subdomain.
    Strips prefix so existing URL routing continues to work.
    Enforces that authenticated users only access their own company portal.
    """

    PUBLIC_PATHS = (
        '/accounts/login/',
        '/accounts/logout/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        request.tenant_slug = None

        tenant = self._from_subdomain(request)
        if tenant is None:
            tenant, rest = self._from_path(request.path)
            if tenant is not None:
                request.path = rest or '/'
                request.path_info = rest or '/'

        if tenant is not None:
            if not tenant.is_active:
                raise Http404('This organization is not active.')
            request.tenant = tenant
            request.tenant_slug = tenant.slug

        # Redirect authenticated users into their own /t/<slug>/ portal
        if (
            not request.tenant
            and getattr(request, 'user', None) is not None
            and request.user.is_authenticated
            and not request.path.startswith('/api/')
            and not request.path.startswith('/admin/')
            and request.path not in ('/register/',)
        ):
            company = getattr(request.user, 'company', None)
            if company and self._should_prefix_path(request.path):
                from apps.core.tenant import get_portal_path
                return redirect(get_portal_path(company.slug, request.path))

        # Block cross-tenant portal access BEFORE the view runs (prevents data leaks)
        if (
            request.tenant
            and getattr(request, 'user', None) is not None
            and request.user.is_authenticated
            and not request.user.is_superuser
            and request.path not in self.PUBLIC_PATHS
        ):
            user_company = getattr(request.user, 'company', None)
            if user_company and user_company.id != request.tenant.id:
                from apps.core.tenant import get_portal_path
                return redirect(get_portal_path(user_company.slug, '/dashboard/'))

        return self.get_response(request)

    @staticmethod
    def _should_prefix_path(path: str) -> bool:
        prefixes = ('/', '/dashboard', '/module', '/accounts', '/attendance')
        return any(path == p or path.startswith(f'{p}/') for p in prefixes)

    def _from_path(self, path: str):
        match = TENANT_PATH_RE.match(path)
        if not match:
            return None, path
        slug = match.group('slug')
        rest = match.group('rest') or '/'
        try:
            company = Company.objects.get(slug=slug)
        except Company.DoesNotExist as exc:
            raise Http404('Organization not found.') from exc
        return company, rest

    def _from_subdomain(self, request):
        from django.conf import settings
        use_subdomains = getattr(settings, 'HRMS_USE_SUBDOMAIN_TENANTS', False)
        domain = getattr(settings, 'HRMS_TENANT_DOMAIN', '')
        if not use_subdomains or not domain:
            return None
        host = request.get_host().split(':')[0].lower()
        if not host.endswith(f'.{domain}') or host == domain:
            return None
        slug = host[: -(len(domain) + 1)]
        if not slug or slug == 'www':
            return None
        try:
            return Company.objects.get(slug=slug, is_active=True)
        except Company.DoesNotExist:
            raise Http404('Organization not found.')
