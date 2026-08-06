from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

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


class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'is_active']


class AllowanceViewSet(viewsets.ModelViewSet):
    queryset = Allowance.objects.all()
    serializer_class = AllowanceSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'is_active', 'is_taxable']


class DeductionViewSet(viewsets.ModelViewSet):
    queryset = Deduction.objects.all()
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'is_active', 'is_statutory']


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'employee', 'salary_structure']


class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    filterset_fields = ['company', 'status']


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'payroll_run', 'employee', 'is_anomaly']


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'employee', 'status']
