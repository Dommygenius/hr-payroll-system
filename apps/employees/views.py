from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet, CompanyScopedReadOnlyModelViewSet
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


class EmployeeViewSet(CompanyScopedModelViewSet):
    queryset = Employee.objects.filter(is_deleted=False)
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    filterset_fields = ['company', 'branch', 'department', 'employment_status', 'employment_type']


class EmployeeContractViewSet(CompanyScopedModelViewSet):
    queryset = EmployeeContract.objects.all()
    serializer_class = EmployeeContractSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    company_lookup = 'employee__company_id'
    filterset_fields = ['employee', 'is_active']


class EmployeeDocumentViewSet(CompanyScopedModelViewSet):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    company_lookup = 'employee__company_id'
    filterset_fields = ['employee', 'document_type']


class EmployeeHistoryViewSet(CompanyScopedReadOnlyModelViewSet):
    queryset = EmployeeHistory.objects.all()
    serializer_class = EmployeeHistorySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    company_lookup = 'employee__company_id'
    filterset_fields = ['employee', 'event_type']
