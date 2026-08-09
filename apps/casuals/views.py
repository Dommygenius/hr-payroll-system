from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.casuals.models import CasualAttendance, CasualPayment, CasualWorker


class CasualWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasualWorker
        fields = '__all__'


class CasualAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasualAttendance
        fields = '__all__'


class CasualPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasualPayment
        fields = '__all__'


class CasualWorkerViewSet(CompanyScopedModelViewSet):
    queryset = CasualWorker.objects.all()
    serializer_class = CasualWorkerSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['first_name', 'last_name', 'worker_id', 'phone', 'id_number']
    filterset_fields = ['company', 'branch', 'supervisor', 'status']


class CasualAttendanceViewSet(CompanyScopedModelViewSet):
    queryset = CasualAttendance.objects.all()
    serializer_class = CasualAttendanceSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'worker', 'date', 'is_paid']


class CasualPaymentViewSet(CompanyScopedModelViewSet):
    queryset = CasualPayment.objects.all()
    serializer_class = CasualPaymentSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'worker', 'is_paid']
