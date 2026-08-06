from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.integrations.models import IntegrationLog, IntegrationProvider, WebhookEndpoint


class IntegrationProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationProvider
        fields = '__all__'


class IntegrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationLog
        fields = '__all__'


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = '__all__'


class IntegrationProviderViewSet(viewsets.ModelViewSet):
    queryset = IntegrationProvider.objects.all()
    serializer_class = IntegrationProviderSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'provider_code']
    filterset_fields = ['company', 'provider_type', 'is_active']


class IntegrationLogViewSet(viewsets.ModelViewSet):
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['provider', 'status', 'action']


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'url']
    filterset_fields = ['company', 'is_active']
