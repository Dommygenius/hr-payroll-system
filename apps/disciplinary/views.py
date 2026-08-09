from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.disciplinary.models import DisciplinaryHearing, Incident, Suspension, Warning


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = '__all__'


class WarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warning
        fields = '__all__'


class SuspensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suspension
        fields = '__all__'


class DisciplinaryHearingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplinaryHearing
        fields = '__all__'


class IncidentViewSet(CompanyScopedModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'status', 'severity']


class WarningViewSet(CompanyScopedModelViewSet):
    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'warning_type', 'is_active', 'incident']


class SuspensionViewSet(CompanyScopedModelViewSet):
    queryset = Suspension.objects.all()
    serializer_class = SuspensionSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'incident', 'is_paid']


class DisciplinaryHearingViewSet(CompanyScopedModelViewSet):
    queryset = DisciplinaryHearing.objects.all()
    serializer_class = DisciplinaryHearingSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'incident', 'status', 'chairperson']
