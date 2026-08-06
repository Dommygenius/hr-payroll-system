"""API URL routing for HRMS."""
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/', include('apps.accounts.api_urls')),
    path('core/', include('apps.core.api_urls')),
    path('employees/', include('apps.employees.api_urls')),
    path('recruitment/', include('apps.recruitment.api_urls')),
    path('payroll/', include('apps.payroll.api_urls')),
    path('leave/', include('apps.leave.api_urls')),
    path('attendance/', include('apps.attendance.api_urls')),
    path('performance/', include('apps.performance.api_urls')),
    path('relations/', include('apps.relations.api_urls')),
    path('disciplinary/', include('apps.disciplinary.api_urls')),
    path('casuals/', include('apps.casuals.api_urls')),
    path('surveys/', include('apps.surveys.api_urls')),
    path('ai/', include('apps.ai_features.api_urls')),
    path('integrations/', include('apps.integrations.api_urls')),
    path('notifications/', include('apps.notifications.api_urls')),
    path('reports/', include('apps.reports.api_urls')),
]
