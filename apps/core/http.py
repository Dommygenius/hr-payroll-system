"""HTTP helpers for tenant-aware redirects."""
from django.shortcuts import redirect
from django.urls import reverse

from apps.core.tenant import get_portal_path


def tenant_redirect(request, viewname, *args, **kwargs):
    """Redirect to a named URL, prefixed with /t/<slug>/ when in a tenant portal."""
    url = reverse(viewname, args=args, kwargs=kwargs)
    slug = getattr(request, 'tenant_slug', None)
    if not slug:
        company = getattr(getattr(request, 'user', None), 'company', None)
        slug = getattr(company, 'slug', None)
    if slug:
        return redirect(get_portal_path(slug, url))
    return redirect(url)
