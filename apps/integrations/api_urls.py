from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.integrations.views import (
    IntegrationLogViewSet,
    IntegrationProviderViewSet,
    WebhookEndpointViewSet,
)

router = DefaultRouter()
router.register('providers', IntegrationProviderViewSet, basename='integration-provider')
router.register('logs', IntegrationLogViewSet, basename='integration-log')
router.register('webhooks', WebhookEndpointViewSet, basename='webhook-endpoint')

urlpatterns = [path('', include(router.urls))]
