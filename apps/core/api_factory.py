"""Generate standard DRF viewsets from models."""
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet


def create_serializer(model_class, read_only=None):
    read_only = read_only or ['created_at', 'updated_at', 'created_by', 'updated_by']

    class DynamicSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_class
            fields = '__all__'
            read_only_fields = [
                f for f in read_only
                if hasattr(model_class, f.replace('_id', '')) or f.endswith('_at')
            ]

    DynamicSerializer.__name__ = f'{model_class.__name__}Serializer'
    return DynamicSerializer


def create_viewset(model_class, search_fields=None, filterset_fields=None):
    serializer_class = create_serializer(model_class)

    class DynamicViewSet(CompanyScopedModelViewSet):
        queryset = model_class.objects.all()
        serializer_class = serializer_class
        permission_classes = [IsAuthenticated, IsCompanyMember]
        search_fields = search_fields or []
        filterset_fields = filterset_fields or []

    DynamicViewSet.__name__ = f'{model_class.__name__}ViewSet'
    return DynamicViewSet
