from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.employees.models import Employee, EmployeeContract, EmployeeDocument, EmployeeHistory


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class EmployeeContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeContract
        fields = '__all__'


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = '__all__'


class EmployeeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeHistory
        fields = '__all__'


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.filter(is_deleted=False)
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    filterset_fields = ['company', 'branch', 'department', 'employment_status', 'employment_type']


class EmployeeContractViewSet(viewsets.ModelViewSet):
    queryset = EmployeeContract.objects.all()
    serializer_class = EmployeeContractSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'is_active']


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'document_type']


class EmployeeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmployeeHistory.objects.all()
    serializer_class = EmployeeHistorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'event_type']
