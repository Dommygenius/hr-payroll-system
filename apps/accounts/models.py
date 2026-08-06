import re
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.core.models.base import TimeStampedModel


class UserRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    HR_ADMIN = 'hr_admin', 'HR Administrator'
    PAYROLL_OFFICER = 'payroll_officer', 'Payroll Officer'
    RECRUITER = 'recruiter', 'Recruiter'
    MANAGER = 'manager', 'Manager'
    SUPERVISOR = 'supervisor', 'Supervisor'
    EMPLOYEE = 'employee', 'Employee'
    FINANCE_OFFICER = 'finance_officer', 'Finance Officer'
    DEPT_HEAD = 'dept_head', 'Department Head'
    CASUAL_SUPERVISOR = 'casual_supervisor', 'Casual Supervisor'
    AUDITOR = 'auditor', 'Auditor'


class User(AbstractUser):
    """Custom user model with multi-auth support."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, unique=True, null=True)
    role = models.CharField(
        max_length=30, choices=UserRole.choices, default=UserRole.EMPLOYEE
    )
    company = models.ForeignKey(
        'core.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )
    branch = models.ForeignKey(
        'core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_mfa_enabled = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_password_change = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    theme = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def record_failed_login(self, threshold=5, lockout_minutes=30):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= threshold:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=lockout_minutes)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def reset_failed_logins(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])


class PermissionGroup(TimeStampedModel):
    """Custom permission groups for RBAC."""

    name = models.CharField(max_length=100)
    codename = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list)
    company = models.ForeignKey(
        'core.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='permission_groups'
    )
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserPermissionGroup(TimeStampedModel):
    """Many-to-many through model for user permission groups."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_group_links')
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE, related_name='user_links')

    class Meta:
        unique_together = ['user', 'group']


class APIToken(TimeStampedModel):
    """API token authentication."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_tokens')
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.user.email})'

    @property
    def is_expired(self):
        if self.expires_at and self.expires_at < timezone.now():
            return True
        return False


class AuditLog(TimeStampedModel):
    """Full audit trail."""

    class ActionType(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        VIEW = 'view', 'View'
        EXPORT = 'export', 'Export'
        APPROVE = 'approve', 'Approve'
        REJECT = 'reject', 'Reject'

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ActionType.choices)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    company = models.ForeignKey(
        'core.Company', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['model_name', 'object_id']),
        ]

    def __str__(self):
        return f'{self.action} - {self.model_name} by {self.user}'


class UserSession(TimeStampedModel):
    """Session management tracking."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f'{self.user.email} - {self.session_key[:8]}'
