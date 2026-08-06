from django.contrib import admin

from apps.surveys.models import Survey, SurveyQuestion, SurveyResponse


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'start_date', 'end_date', 'is_anonymous']
    list_filter = ['company', 'status', 'is_anonymous']
    search_fields = ['title']


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'question_type', 'order', 'is_required']
    list_filter = ['company', 'question_type', 'is_required']


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'respondent', 'submitted_at']
    list_filter = ['company', 'survey']
