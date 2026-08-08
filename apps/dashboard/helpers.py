"""Dashboard module CRUD helpers."""
from django.db.models import Q


def get_user_company(user):
    return getattr(user, 'company', None)


def get_request_company(request):
    """Prefer the portal tenant; fall back to the authenticated user's company."""
    tenant = getattr(request, 'tenant', None)
    if tenant is not None:
        return tenant
    return get_user_company(getattr(request, 'user', None))


def scoped_queryset(user, model, extra_filter=None, select_related=None, company=None):
    """Company-scoped queryset. Never returns other tenants' rows when company is known."""
    qs = model.objects.all()
    company = company or get_user_company(user)
    if company and hasattr(model, 'company_id'):
        qs = qs.filter(company=company)
    elif hasattr(model, 'company_id') and company is None:
        # Unscoped users must not see all tenant data
        qs = qs.none()
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
    if attr in ('reason', 'rejection_reason', 'completion_comment', 'notes', 'description'):
        text = str(val).strip()
        if not text:
            return '—'
        return text if len(text) <= 80 else text[:77] + '…'
    if hasattr(val, '__str__') and not isinstance(val, (str, int, float, bool)):
        return str(val)
    if isinstance(val, bool):
        return 'Yes' if val else 'No'
    return val


def detail_fields_payload(obj, detail_fields):
    """Build read-only detail rows for the select-to-inspect panel."""
    if not detail_fields:
        return []
    rows = []
    for attr, label in detail_fields:
        value = cell_value(obj, attr)
        if value == '' or value is None:
            value = '—'
        rows.append({
            'attr': attr,
            'label': label,
            'value': value,
            'is_status': attr.endswith('_status') or attr == 'status',
        })
    return rows
