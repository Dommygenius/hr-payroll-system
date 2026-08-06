import uuid

from django.conf import settings
from django.db import models

from apps.core.models.base import CompanyScopedModel


class SalaryStructure(CompanyScopedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['company', 'code']

    def __str__(self):
        return self.name


class Allowance(CompanyScopedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_percentage = models.BooleanField(default=False)
    percentage_of = models.CharField(max_length=50, default='basic')
    is_taxable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Deduction(CompanyScopedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_percentage = models.BooleanField(default=False)
    percentage_of = models.CharField(max_length=50, default='basic')
    is_statutory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class EmployeeSalary(CompanyScopedModel):
    employee = models.OneToOneField('employees.Employee', on_delete=models.CASCADE, related_name='salary')
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.SET_NULL, null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    allowances = models.ManyToManyField(Allowance, blank=True)
    deductions = models.ManyToManyField(Deduction, blank=True)
    effective_date = models.DateField()
    bank_account = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.employee} - {self.basic_salary}'


class PayrollRun(CompanyScopedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PROCESSING = 'processing', 'Processing'
        REVIEW = 'review', 'Under Review'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    period_start = models.DateField()
    period_end = models.DateField()
    payment_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payrolls'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-period_start']

    def __str__(self):
        return f'{self.name} ({self.period_start} - {self.period_end})'


class Payslip(CompanyScopedModel):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='payslips')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pension_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    breakdown = models.JSONField(default=dict)
    pdf_file = models.FileField(upload_to='payroll/payslips/', blank=True, null=True)
    is_anomaly = models.BooleanField(default=False)
    anomaly_reason = models.TextField(blank=True)

    class Meta:
        unique_together = ['payroll_run', 'employee']
        ordering = ['employee__last_name']

    def __str__(self):
        return f'Payslip: {self.employee} - {self.payroll_run}'


class Loan(CompanyScopedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        ACTIVE = 'active', 'Active'
        PAID = 'paid', 'Paid'
        DEFAULTED = 'defaulted', 'Defaulted'

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    monthly_installment = models.DecimalField(max_digits=12, decimal_places=2)
    total_installments = models.PositiveSmallIntegerField()
    paid_installments = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    start_date = models.DateField()
    purpose = models.TextField(blank=True)

    def __str__(self):
        return f'Loan: {self.employee} - {self.amount}'
