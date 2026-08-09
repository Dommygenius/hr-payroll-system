from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.attendance.models import AttendanceRecord, BiometricDevice, Roster, Shift


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'


class RosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roster
        fields = '__all__'


class BiometricDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricDevice
        fields = '__all__'


class ShiftViewSet(CompanyScopedModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'is_active', 'is_night_shift']


class AttendanceRecordViewSet(CompanyScopedModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'date', 'status', 'shift', 'is_anomaly']


class RosterViewSet(CompanyScopedModelViewSet):
    queryset = Roster.objects.all()
    serializer_class = RosterSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'shift', 'date', 'is_off']


class BiometricDeviceViewSet(CompanyScopedModelViewSet):
    queryset = BiometricDevice.objects.all()
    serializer_class = BiometricDeviceSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'device_id']
    filterset_fields = ['company', 'branch', 'device_type', 'is_active']
