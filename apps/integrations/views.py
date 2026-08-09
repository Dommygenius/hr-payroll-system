from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

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


class IntegrationProviderViewSet(CompanyScopedModelViewSet):
    queryset = IntegrationProvider.objects.all()
    serializer_class = IntegrationProviderSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'provider_code']
    filterset_fields = ['company', 'provider_type', 'is_active']


class IntegrationLogViewSet(CompanyScopedModelViewSet):
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['provider', 'status', 'action']


class WebhookEndpointViewSet(CompanyScopedModelViewSet):
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'url']
    filterset_fields = ['company', 'is_active']
