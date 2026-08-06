from django.contrib import admin

from apps.integrations.models import IntegrationLog, IntegrationProvider, WebhookEndpoint


@admin.register(IntegrationProvider)
class IntegrationProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider_type', 'provider_code', 'is_active', 'last_sync']
    list_filter = ['company', 'provider_type', 'is_active']
    search_fields = ['name', 'provider_code']


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ['provider', 'action', 'status', 'created_at']
    list_filter = ['status', 'action']


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'url']
