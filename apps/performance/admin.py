from django.contrib import admin

from apps.performance.models import Feedback360, Goal, KPI, PerformanceCycle, PerformanceReview


@admin.register(PerformanceCycle)
class PerformanceCycleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'review_deadline', 'status']
    list_filter = ['company', 'status']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'cycle', 'status', 'progress', 'due_date']
    list_filter = ['company', 'status', 'cycle']
    search_fields = ['title', 'description']


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'target', 'measurement_unit', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name']


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'cycle', 'reviewer', 'status', 'overall_rating']
    list_filter = ['company', 'status', 'cycle']


@admin.register(Feedback360)
class Feedback360Admin(admin.ModelAdmin):
    list_display = ['review', 'reviewer', 'relationship', 'rating', 'is_anonymous']
    list_filter = ['company', 'relationship']
