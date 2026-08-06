"""Dashboard module CRUD helpers."""
from django.db.models import Q


def get_user_company(user):
    return getattr(user, 'company', None)


def scoped_queryset(user, model, extra_filter=None, select_related=None):
    qs = model.objects.all()
    company = get_user_company(user)
    if company and hasattr(model, 'company_id'):
        qs = qs.filter(company=company)
    if extra_filter:
        qs = qs.filter(**extra_filter)
    if select_related:
        qs = qs.select_related(*select_related)
    return qs


def apply_search(qs, search, search_fields):
    if not search or not search_fields:
        return qs
    q = Q()
    for field in search_fields:
        q |= Q(**{f'{field}__icontains': search})
    return qs.filter(q)


def cell_value(obj, attr):
    if attr == 'full_name':
        if hasattr(obj, 'full_name'):
            return obj.full_name
        if hasattr(obj, 'first_name') and hasattr(obj, 'last_name'):
            return f'{obj.first_name} {obj.last_name}'.strip()
    val = getattr(obj, attr, '')
    if val is None:
        return '—'
    if hasattr(val, '__str__') and not isinstance(val, (str, int, float, bool)):
        return str(val)
    if isinstance(val, bool):
        return 'Yes' if val else 'No'
    return val
