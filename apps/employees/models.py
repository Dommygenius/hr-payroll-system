import uuid

from django.conf import settings
from django.db import models

from apps.core.models.base import AuditableModel, CompanyScopedModel, SoftDeleteModel


class Employee(CompanyScopedModel, SoftDeleteModel):
    """Core employee profile."""

    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PROBATION = 'probation', 'Probation'
        ON_LEAVE = 'on_leave', 'On Leave'
        SUSPENDED = 'suspended', 'Suspended'
        TERMINATED = 'terminated', 'Terminated'
        RESIGNED = 'resigned', 'Resigned'

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        CONTRACT = 'contract', 'Contract'
        INTERN = 'intern', 'Intern'
        CASUAL = 'casual', 'Casual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile'
    )
    employee_id = models.CharField(max_length=50, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='employees/photos/', blank=True, null=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, related_name='employees')
    department = models.ForeignKey('core.Department', on_delete=models.SET_NULL, null=True, related_name='employees')
    designation = models.ForeignKey('core.Designation', on_delete=models.SET_NULL, null=True, related_name='employees')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    employment_status = models.CharField(max_length=20, choices=EmploymentStatus.choices, default=EmploymentStatus.ACTIVE)
    date_joined = models.DateField()
    date_confirmed = models.DateField(null=True, blank=True)
    date_terminated = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, default='US')
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    social_security_number = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ['company', 'employee_id']
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.employee_id})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class EmployeeContract(CompanyScopedModel):
    """Employment contracts."""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    contract_type = models.CharField(max_length=50)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    document = models.FileField(upload_to='employees/contracts/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.contract_number} - {self.employee}'


class EmployeeDocument(CompanyScopedModel):
    """Employee document management."""

    class DocumentType(models.TextChoices):
        ID = 'id', 'National ID'
        PASSPORT = 'passport', 'Passport'
        CERTIFICATE = 'certificate', 'Certificate'
        CONTRACT = 'contract', 'Contract'
        RESUME = 'resume', 'Resume'
        OTHER = 'other', 'Other'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='employees/documents/')
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.employee}'


class EmployeeHistory(AuditableModel):
    """Track employee changes over time."""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='history')
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    effective_date = models.DateField()
    previous_value = models.JSONField(default=dict, blank=True)
    new_value = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-effective_date']
        verbose_name_plural = 'employee histories'

    def __str__(self):
        return f'{self.event_type} - {self.employee}'
