from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

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


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'is_active', 'is_night_shift']


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'employee', 'date', 'status', 'shift', 'is_anomaly']


class RosterViewSet(viewsets.ModelViewSet):
    queryset = Roster.objects.all()
    serializer_class = RosterSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'employee', 'shift', 'date', 'is_off']


class BiometricDeviceViewSet(viewsets.ModelViewSet):
    queryset = BiometricDevice.objects.all()
    serializer_class = BiometricDeviceSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'device_id']
    filterset_fields = ['company', 'branch', 'device_type', 'is_active']
