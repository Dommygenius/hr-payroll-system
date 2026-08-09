from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.integrations.models import IntegrationLog, IntegrationProvider, WebhookEndpoint


class IntegrationProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationProvider
        fields = '__all__'
        extra_kwargs = {
            'credentials': {'write_only': True},
        }


class IntegrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationLog
        fields = '__all__'
        read_only_fields = [f.name for f in IntegrationLog._meta.fields]


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = '__all__'
        extra_kwargs = {
            'secret': {'write_only': True},
        }


class IntegrationProviderViewSet(CompanyScopedModelViewSet):
    queryset = IntegrationProvider.objects.all()
    serializer_class = IntegrationProviderSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'provider_code']
    filterset_fields = ['company', 'provider_type', 'is_active']


class IntegrationLogViewSet(CompanyScopedModelViewSet):
    queryset = IntegrationLog.objects.select_related('provider').all()
    serializer_class = IntegrationLogSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['provider', 'status', 'action']
    company_lookup = 'provider__company_id'


class WebhookEndpointViewSet(CompanyScopedModelViewSet):
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'url']
    filterset_fields = ['company', 'is_active']
