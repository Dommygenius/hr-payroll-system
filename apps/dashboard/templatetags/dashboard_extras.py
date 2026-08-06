from django import template

register = template.Library()

STATUS_MAP = {
    'active': 'active', 'approved': 'approved', 'open': 'open', 'paid': 'paid',
    'completed': 'completed', 'present': 'present', 'hired': 'active',
    'pending': 'pending', 'draft': 'pending', 'review': 'pending', 'probation': 'pending',
    'screening': 'pending', 'interview': 'pending', 'new': 'pending',
    'rejected': 'rejected', 'terminated': 'rejected', 'absent': 'rejected',
    'suspended': 'rejected', 'cancelled': 'rejected', 'closed': 'rejected',
    'on_leave': 'pending', 'late': 'pending', 'half_day': 'pending',
}


@register.filter
def status_badge(value):
    if value is None or value == '—':
        return value
    text = str(value).strip()
    key = text.lower().replace(' ', '_')
    css = STATUS_MAP.get(key, 'default')
    display = text.replace('_', ' ')
    return f'<span class="status-badge status-{css}">{display}</span>'


@register.filter
def is_status_column(col_key):
    status_cols = {'status', 'employment_status', 'priority', 'severity', 'warning_type'}
    return col_key in status_cols
