import uuid

from django.conf import settings
from django.db import models

from apps.core.models.base import CompanyScopedModel, TimeStampedModel


class AIAnalysisJob(CompanyScopedModel):
    class JobType(models.TextChoices):
        RESUME_SCREENING = 'resume_screening', 'Resume Screening'
        CANDIDATE_RANKING = 'candidate_ranking', 'Candidate Ranking'
        PAYROLL_ANOMALY = 'payroll_anomaly', 'Payroll Anomaly Detection'
        ATTRITION_PREDICTION = 'attrition_prediction', 'Attrition Prediction'
        ATTENDANCE_ANOMALY = 'attendance_anomaly', 'Attendance Anomaly'
        REPORT_GENERATION = 'report_generation', 'Smart Report Generation'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_type = models.CharField(max_length=30, choices=JobType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    input_data = models.JSONField(default=dict)
    result = models.JSONField(default=dict, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.job_type} - {self.status}'


class ChatbotConversation(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chatbot_conversations')
    session_id = models.UUIDField(default=uuid.uuid4)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']


class ChatbotMessage(TimeStampedModel):
    conversation = models.ForeignKey(ChatbotConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}'
