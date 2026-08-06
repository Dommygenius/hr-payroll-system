import uuid

from django.conf import settings
from django.db import models

from apps.core.models.base import CompanyScopedModel


class Survey(CompanyScopedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    start_date = models.DateField()
    end_date = models.DateField()
    is_anonymous = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class SurveyQuestion(CompanyScopedModel):
    class QuestionType(models.TextChoices):
        TEXT = 'text', 'Text'
        RATING = 'rating', 'Rating (1-5)'
        MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
        YES_NO = 'yes_no', 'Yes/No'

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    options = models.JSONField(default=list, blank=True)
    is_required = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.survey.title} - Q{self.order}'


class SurveyResponse(CompanyScopedModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    answers = models.JSONField(default=dict)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'Response: {self.survey}'
