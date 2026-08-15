"""Role-based permissions for dashboard actions."""
from apps.accounts.models import UserRole

HR_ATTENDANCE_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.HR_ADMIN,
    UserRole.MANAGER,
    UserRole.SUPERVISOR,
    UserRole.DEPT_HEAD,
}

HR_LEAVE_ROLES = HR_ATTENDANCE_ROLES | {UserRole.PAYROLL_OFFICER}

TASK_MANAGER_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.HR_ADMIN,
    UserRole.MANAGER,
    UserRole.SUPERVISOR,
    UserRole.DEPT_HEAD,
}

USER_ADMIN_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.HR_ADMIN,
}

PAYROLL_WRITE_ROLES = USER_ADMIN_ROLES | {
    UserRole.PAYROLL_OFFICER,
    UserRole.FINANCE_OFFICER,
}

RECRUIT_WRITE_ROLES = USER_ADMIN_ROLES | {UserRole.RECRUITER}

CASUAL_WRITE_ROLES = USER_ADMIN_ROLES | {UserRole.CASUAL_SUPERVISOR}

MODULE_WRITE_ROLES = {
    'employees': HR_ATTENDANCE_ROLES,
    'recruitment': RECRUIT_WRITE_ROLES,
    'payroll': PAYROLL_WRITE_ROLES,
    'attendance': HR_ATTENDANCE_ROLES,
    'performance': TASK_MANAGER_ROLES,
    'relations': HR_ATTENDANCE_ROLES,
    'disciplinary': HR_ATTENDANCE_ROLES,
    'casuals': CASUAL_WRITE_ROLES,
    'surveys': HR_ATTENDANCE_ROLES,
    'settings': USER_ADMIN_ROLES,
}


def _role(user):
    return getattr(user, 'role', UserRole.EMPLOYEE)


def can_manage_attendance(user):
    return user.is_superuser or _role(user) in HR_ATTENDANCE_ROLES


def can_manage_leave(user):
    return user.is_superuser or _role(user) in HR_LEAVE_ROLES


def can_assign_tasks(user):
    return user.is_superuser or _role(user) in TASK_MANAGER_ROLES


def can_manage_users(user):
    return user.is_superuser or _role(user) in USER_ADMIN_ROLES


def can_configure_roles(user):
    """Super admin may enable/disable roles for the tenant."""
    from apps.accounts.roles import can_configure_tenant_roles
    return can_configure_tenant_roles(user)


def can_write_module(user, module, tab=None, action='write'):
    """Whether the user may create/edit/delete records in a dashboard module."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    if _role(user) == UserRole.AUDITOR:
        return False
    if module == 'leave':
        if action in ('approve', 'delete'):
            return can_manage_leave(user)
        return True
    allowed = MODULE_WRITE_ROLES.get(module)
    if allowed is None:
        return True
    return _role(user) in allowed
