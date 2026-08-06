from django.contrib import admin

from apps.recruitment.models import Applicant, Interview, JobPosting, OfferLetter, OnboardingChecklist


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'status', 'openings', 'posted_date', 'closing_date']
    list_filter = ['company', 'status', 'employment_type', 'is_published']
    search_fields = ['title', 'description']


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'job', 'email', 'status', 'ai_score']
    list_filter = ['company', 'status', 'source']
    search_fields = ['first_name', 'last_name', 'email', 'phone']


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'interviewer', 'scheduled_at', 'is_completed', 'rating']
    list_filter = ['company', 'is_completed']


@admin.register(OfferLetter)
class OfferLetterAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'salary', 'start_date', 'expiry_date', 'is_accepted']
    list_filter = ['company', 'is_accepted']


@admin.register(OnboardingChecklist)
class OnboardingChecklistAdmin(admin.ModelAdmin):
    list_display = ['task', 'employee', 'assigned_to', 'due_date', 'is_completed']
    list_filter = ['company', 'is_completed']
    search_fields = ['task', 'description']
