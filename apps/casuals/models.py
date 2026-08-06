import uuid

from django.db import models

from apps.core.models.base import CompanyScopedModel


class CasualWorker(CompanyScopedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker_id = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    id_number = models.CharField(max_length=50, blank=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True)
    supervisor = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    date_registered = models.DateField()

    class Meta:
        unique_together = ['company', 'worker_id']
        ordering = ['last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.worker_id})'


class CasualAttendance(CompanyScopedModel):
    worker = models.ForeignKey(CasualWorker, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount_earned = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ['worker', 'date']
        ordering = ['-date']

    def __str__(self):
        return f'{self.worker} - {self.date}'


class CasualPayment(CompanyScopedModel):
    worker = models.ForeignKey(CasualWorker, on_delete=models.CASCADE, related_name='payments')
    period_start = models.DateField()
    period_end = models.DateField()
    total_days = models.PositiveSmallIntegerField()
    total_hours = models.DecimalField(max_digits=8, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-period_start']

    def __str__(self):
        return f'Payment: {self.worker} ({self.period_start} - {self.period_end})'
