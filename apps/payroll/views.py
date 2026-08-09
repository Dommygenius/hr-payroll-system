from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.payroll.models import (
    Allowance,
    Deduction,
    EmployeeSalary,
    Loan,
    PayrollRun,
    Payslip,
    SalaryStructure,
)


class SalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = '__all__'


class AllowanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allowance
        fields = '__all__'


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = '__all__'


class EmployeeSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSalary
        fields = '__all__'


class PayrollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = '__all__'


class PayslipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payslip
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'


class SalaryStructureViewSet(CompanyScopedModelViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'is_active']


class AllowanceViewSet(CompanyScopedModelViewSet):
    queryset = Allowance.objects.all()
    serializer_class = AllowanceSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'is_active', 'is_taxable']


class DeductionViewSet(CompanyScopedModelViewSet):
    queryset = Deduction.objects.all()
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'is_active', 'is_statutory']


class EmployeeSalaryViewSet(CompanyScopedModelViewSet):
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'salary_structure']


class PayrollRunViewSet(CompanyScopedModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name']
    filterset_fields = ['company', 'status']


class PayslipViewSet(CompanyScopedModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'payroll_run', 'employee', 'is_anomaly']


class LoanViewSet(CompanyScopedModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'status']
