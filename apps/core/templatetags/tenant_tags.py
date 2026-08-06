from django import template
from django.urls import reverse

from apps.core.tenant import get_portal_path

register = template.Library()


@register.simple_tag(takes_context=True)
def tenant_url(context, viewname, *args, **kwargs):
    """Reverse URL and prefix with /t/<slug>/ when in tenant context."""
    url = reverse(viewname, args=args, kwargs=kwargs)
    request = context.get('request')
    slug = getattr(request, 'tenant_slug', None) if request else None
    if slug:
        return get_portal_path(slug, url)
    return url
