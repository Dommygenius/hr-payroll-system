from django.contrib import admin

from apps.payroll.models import (
    Allowance,
    Deduction,
    EmployeeSalary,
    Loan,
    PayrollRun,
    Payslip,
    SalaryStructure,
)


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'basic_salary', 'currency', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'amount', 'is_percentage', 'is_taxable', 'is_active']
    list_filter = ['company', 'is_active', 'is_taxable']


@admin.register(Deduction)
class DeductionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'amount', 'is_percentage', 'is_statutory', 'is_active']
    list_filter = ['company', 'is_active', 'is_statutory']


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'basic_salary', 'salary_structure', 'effective_date']
    list_filter = ['company', 'salary_structure']


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ['name', 'period_start', 'period_end', 'status', 'total_net']
    list_filter = ['company', 'status']


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_run', 'gross_pay', 'net_pay', 'is_anomaly']
    list_filter = ['company', 'payroll_run', 'is_anomaly']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['employee', 'amount', 'monthly_installment', 'status', 'start_date']
    list_filter = ['company', 'status']
