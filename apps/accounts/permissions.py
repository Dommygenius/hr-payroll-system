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
