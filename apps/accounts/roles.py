"""Tenant role catalog helpers — enable/disable roles per company."""
from apps.accounts.models import UserRole

# Always available for every tenant (cannot be removed)
REQUIRED_ROLES = (UserRole.SUPER_ADMIN, UserRole.EMPLOYEE)

# Sensible default pack for new tenants (can be expanded by super admin)
DEFAULT_TENANT_ROLES = (
    UserRole.SUPER_ADMIN,
    UserRole.HR_ADMIN,
    UserRole.MANAGER,
    UserRole.SUPERVISOR,
    UserRole.DEPT_HEAD,
    UserRole.PAYROLL_OFFICER,
    UserRole.EMPLOYEE,
)


def all_role_choices():
    return list(UserRole.choices)


def default_enabled_roles():
    return list(DEFAULT_TENANT_ROLES)


def get_enabled_roles(company):
    """Return enabled role values for a company (falls back to defaults)."""
    if company is None:
        return [c[0] for c in UserRole.choices]
    roles = getattr(company, 'enabled_roles', None) or []
    if not roles:
        return default_enabled_roles()
    # Always keep required roles
    normalized = []
    for value, _label in UserRole.choices:
        if value in roles or value in REQUIRED_ROLES:
            if value not in normalized:
                normalized.append(value)
    return normalized or default_enabled_roles()


def set_enabled_roles(company, role_values):
    """Persist enabled roles for a tenant; keeps required roles."""
    valid = {c[0] for c in UserRole.choices}
    selected = [r for r in role_values if r in valid]
    for required in REQUIRED_ROLES:
        if required not in selected:
            selected.insert(0, required)
    # Deduplicate preserving order
    seen = set()
    ordered = []
    for r in selected:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    company.enabled_roles = ordered
    company.save(update_fields=['enabled_roles', 'updated_at'])
    return ordered


def enabled_role_choices(company):
    enabled = set(get_enabled_roles(company))
    return [(value, label) for value, label in UserRole.choices if value in enabled]


def can_configure_tenant_roles(user):
    """Only tenant super admins (or platform superusers) can reshape the role catalog."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    return getattr(user, 'role', None) == UserRole.SUPER_ADMIN


def assignable_role_choices(actor, company, current_role=None):
    """
    Roles the actor may assign within this tenant.
    - Catalog limited to enabled tenant roles (+ current role so edits don't break)
    - Only super_admin / platform superuser may assign super_admin
    """
    enabled = set(get_enabled_roles(company))
    if current_role:
        enabled.add(current_role)

    choices = [(v, label) for v, label in UserRole.choices if v in enabled]

    if not can_configure_tenant_roles(actor):
        choices = [(v, label) for v, label in choices if v != UserRole.SUPER_ADMIN]

    return choices
