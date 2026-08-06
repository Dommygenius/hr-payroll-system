from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

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


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'employee', 'status', 'severity']


class WarningViewSet(viewsets.ModelViewSet):
    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'employee', 'warning_type', 'is_active', 'incident']


class SuspensionViewSet(viewsets.ModelViewSet):
    queryset = Suspension.objects.all()
    serializer_class = SuspensionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'employee', 'incident', 'is_paid']


class DisciplinaryHearingViewSet(viewsets.ModelViewSet):
    queryset = DisciplinaryHearing.objects.all()
    serializer_class = DisciplinaryHearingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'incident', 'status', 'chairperson']
