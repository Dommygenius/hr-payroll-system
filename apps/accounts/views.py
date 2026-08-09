import secrets

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import APIToken, AuditLog, PermissionGroup
from apps.accounts.serializers import (
    APITokenSerializer,
    AuditLogSerializer,
    PermissionGroupSerializer,
    UserCreateSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)
from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet, CompanyScopedReadOnlyModelViewSet

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class UserViewSet(CompanyScopedModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    filterset_fields = ['role', 'company', 'branch', 'is_active']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class PermissionGroupViewSet(CompanyScopedModelViewSet):
    queryset = PermissionGroup.objects.all()
    serializer_class = PermissionGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'codename']
    filterset_fields = ['company', 'is_system']


class APITokenViewSet(viewsets.ModelViewSet):
    serializer_class = APITokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return APIToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            key=secrets.token_hex(32),
        )


class AuditLogViewSet(CompanyScopedReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    filterset_fields = ['user', 'action', 'model_name', 'company']
    search_fields = ['object_repr', 'model_name']


class MFASetupView(APIView):
    def post(self, request):
        import base64
        import io

        import qrcode
        from django_otp.plugins.otp_totp.models import TOTPDevice

        device, created = TOTPDevice.objects.get_or_create(
            user=request.user, name='default', defaults={'confirmed': False}
        )
        if created:
            device.save()

        uri = device.config_url
        qr = qrcode.make(uri)
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        qr_b64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({'provisioning_uri': uri, 'qr_code': qr_b64})


class MFAVerifyView(APIView):
    def post(self, request):
        token = request.data.get('token')
        from django_otp.plugins.otp_totp.models import TOTPDevice

        device = TOTPDevice.objects.filter(user=request.user).first()
        if device and device.verify_token(token):
            device.confirmed = True
            device.save()
            request.user.is_mfa_enabled = True
            request.user.save(update_fields=['is_mfa_enabled'])
            return Response({'detail': 'MFA enabled successfully.'})
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile_view(request):
    """Web profile page for dashboard users."""
    return render(request, 'accounts/profile.html', {'profile_user': request.user})
