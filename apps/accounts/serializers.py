from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import APIToken, AuditLog, PermissionGroup, User, UserRole


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'first_name', 'last_name',
            'role', 'company', 'branch', 'avatar', 'is_mfa_enabled',
            'preferred_language', 'timezone', 'theme', 'date_joined',
        ]
        read_only_fields = [
            'id', 'date_joined', 'role', 'company', 'is_mfa_enabled',
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'password', 'first_name', 'last_name',
        ]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        request = self.context.get('request')
        user = User(**validated_data)
        user.role = UserRole.EMPLOYEE
        if request and getattr(request.user, 'is_authenticated', False):
            user.company_id = getattr(request.user, 'company_id', None)
        user.set_password(password)
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'avatar',
            'preferred_language', 'timezone', 'theme',
        ]


class PermissionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionGroup
        fields = '__all__'
        read_only_fields = ['company']


class APITokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIToken
        fields = ['id', 'name', 'key', 'is_active', 'expires_at', 'last_used_at', 'created_at']
        read_only_fields = ['key', 'last_used_at', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = [
            'user', 'company', 'action', 'model_name', 'object_id',
            'object_repr', 'changes', 'ip_address', 'user_agent', 'created_at',
        ]
