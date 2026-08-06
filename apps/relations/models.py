import uuid

from django.conf import settings
from django.db import models

from apps.core.models.base import CompanyScopedModel


class Grievance(CompanyScopedModel):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        INVESTIGATING = 'investigating', 'Investigating'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='grievances')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} - {self.employee}'


class Recognition(CompanyScopedModel):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='recognitions')
    awarded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    award_date = models.DateField()

    class Meta:
        ordering = ['-award_date']

    def __str__(self):
        return f'{self.title} - {self.employee}'


class ExitInterview(CompanyScopedModel):
    employee = models.OneToOneField('employees.Employee', on_delete=models.CASCADE, related_name='exit_interview')
    interview_date = models.DateField()
    interviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reason_for_leaving = models.TextField()
    feedback = models.TextField(blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    suggestions = models.TextField(blank=True)

    def __str__(self):
        return f'Exit Interview: {self.employee}'
