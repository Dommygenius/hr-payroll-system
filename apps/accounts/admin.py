from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import APIToken, AuditLog, PermissionGroup, User, UserPermissionGroup, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'company', 'is_active', 'is_mfa_enabled']
    list_filter = ['role', 'company', 'is_active', 'is_mfa_enabled']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HRMS', {
            'fields': (
                'phone', 'role', 'company', 'branch', 'avatar',
                'is_mfa_enabled', 'preferred_language', 'timezone', 'theme',
            ),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('HRMS', {'fields': ('email', 'phone', 'role', 'company')}),
    )


@admin.register(PermissionGroup)
class PermissionGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'company', 'is_system']
    search_fields = ['name', 'codename']


@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'expires_at', 'last_used_at']
    list_filter = ['is_active']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'model_name', 'object_repr', 'created_at']
    list_filter = ['action', 'model_name']
    search_fields = ['object_repr', 'user__email']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'changes', 'ip_address']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'device_type', 'is_active', 'last_activity']
    list_filter = ['is_active']
