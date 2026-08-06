from django.contrib import admin

from apps.relations.models import ExitInterview, Grievance, Recognition


@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ['subject', 'employee', 'status', 'priority', 'assigned_to']
    list_filter = ['company', 'status', 'priority']
    search_fields = ['subject', 'description']


@admin.register(Recognition)
class RecognitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'awarded_by', 'category', 'award_date']
    list_filter = ['company', 'category']
    search_fields = ['title', 'description']


@admin.register(ExitInterview)
class ExitInterviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'interview_date', 'interviewer', 'would_recommend']
    list_filter = ['company']
