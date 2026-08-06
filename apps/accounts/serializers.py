from rest_framework import serializers

from apps.accounts.models import APIToken, AuditLog, PermissionGroup, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'first_name', 'last_name',
            'role', 'company', 'branch', 'avatar', 'is_mfa_enabled',
            'preferred_language', 'timezone', 'theme', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'password', 'first_name', 'last_name',
            'role', 'company', 'branch',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
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
