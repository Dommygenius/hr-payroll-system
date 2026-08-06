from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    APITokenViewSet,
    AuditLogViewSet,
    MFASetupView,
    MFAVerifyView,
    PermissionGroupViewSet,
    ProfileView,
    RegisterView,
    UserViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('permission-groups', PermissionGroupViewSet)
router.register('api-tokens', APITokenViewSet, basename='api-token')
router.register('audit-logs', AuditLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('mfa/setup/', MFASetupView.as_view(), name='mfa-setup'),
    path('mfa/verify/', MFAVerifyView.as_view(), name='mfa-verify'),
]
