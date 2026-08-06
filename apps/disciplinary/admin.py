from django.contrib import admin

from apps.disciplinary.models import DisciplinaryHearing, Incident, Suspension, Warning


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'incident_date', 'severity', 'status', 'reported_by']
    list_filter = ['company', 'status', 'severity']


@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ['employee', 'warning_type', 'issue_date', 'issued_by', 'is_active']
    list_filter = ['company', 'warning_type', 'is_active']


@admin.register(Suspension)
class SuspensionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_date', 'end_date', 'is_paid', 'approved_by']
    list_filter = ['company', 'is_paid']


@admin.register(DisciplinaryHearing)
class DisciplinaryHearingAdmin(admin.ModelAdmin):
    list_display = ['incident', 'scheduled_date', 'chairperson', 'status']
    list_filter = ['company', 'status']
