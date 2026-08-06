import uuid

from django.conf import settings
from django.db import models

from apps.core.models.base import CompanyScopedModel


class Incident(CompanyScopedModel):
    class Status(models.TextChoices):
        REPORTED = 'reported', 'Reported'
        INVESTIGATING = 'investigating', 'Investigating'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    class Severity(models.TextChoices):
        MINOR = 'minor', 'Minor'
        MODERATE = 'moderate', 'Moderate'
        MAJOR = 'major', 'Major'
        CRITICAL = 'critical', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='incidents')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    incident_date = models.DateField()
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MINOR)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    location = models.CharField(max_length=255, blank=True)
    witnesses = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)

    class Meta:
        ordering = ['-incident_date']

    def __str__(self):
        return f'Incident: {self.employee} - {self.incident_date}'


class Warning(CompanyScopedModel):
    class WarningType(models.TextChoices):
        VERBAL = 'verbal', 'Verbal Warning'
        WRITTEN = 'written', 'Written Warning'
        FINAL = 'final', 'Final Warning'

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='warnings')
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True)
    warning_type = models.CharField(max_length=20, choices=WarningType.choices)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    issue_date = models.DateField()
    description = models.TextField()
    document = models.FileField(upload_to='disciplinary/warnings/', blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f'{self.warning_type} - {self.employee}'


class Suspension(CompanyScopedModel):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='suspensions')
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    is_paid = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'Suspension: {self.employee} ({self.start_date} - {self.end_date})'


class DisciplinaryHearing(CompanyScopedModel):
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        ADJOURNED = 'adjourned', 'Adjourned'

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='hearings')
    scheduled_date = models.DateTimeField()
    chairperson = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='chaired_hearings')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    outcome = models.TextField(blank=True)
    decision = models.TextField(blank=True)
    minutes = models.FileField(upload_to='disciplinary/hearings/', blank=True, null=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f'Hearing: {self.incident} - {self.scheduled_date}'
