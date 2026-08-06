import uuid

from django.conf import settings
from django.db import models

from apps.core.models.base import CompanyScopedModel


class JobPosting(CompanyScopedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'
        ON_HOLD = 'on_hold', 'On Hold'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    department = models.ForeignKey('core.Department', on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey('core.Designation', on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    employment_type = models.CharField(max_length=20, default='full_time')
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    openings = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    posted_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Applicant(CompanyScopedModel):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        SCREENING = 'screening', 'Screening'
        INTERVIEW = 'interview', 'Interview'
        OFFER = 'offer', 'Offer'
        HIRED = 'hired', 'Hired'
        REJECTED = 'rejected', 'Rejected'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applicants')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    resume = models.FileField(upload_to='recruitment/resumes/')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    ai_score = models.FloatField(null=True, blank=True)
    ai_rank = models.PositiveIntegerField(null=True, blank=True)
    source = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['ai_rank', '-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.job.title}'


class Interview(CompanyScopedModel):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    location = models.CharField(max_length=255, blank=True)
    meeting_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f'Interview: {self.applicant} at {self.scheduled_at}'


class OfferLetter(CompanyScopedModel):
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE, related_name='offer')
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    start_date = models.DateField()
    expiry_date = models.DateField()
    document = models.FileField(upload_to='recruitment/offers/', blank=True, null=True)
    is_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    terms = models.TextField(blank=True)

    def __str__(self):
        return f'Offer: {self.applicant}'


class OnboardingChecklist(CompanyScopedModel):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='onboarding_items')
    task = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f'{self.task} - {self.employee}'
