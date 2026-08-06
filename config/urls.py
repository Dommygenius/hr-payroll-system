"""URL configuration for HRMS project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.accounts.saas_views import saas_landing_view, tenant_register_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', tenant_register_view, name='tenant-register'),
    path('', saas_landing_view, name='saas-landing'),
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('api/v1/', include('config.api_urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'HRMS Administration'
admin.site.site_title = 'HRMS Admin'
admin.site.index_title = 'Human Resource Management System'
