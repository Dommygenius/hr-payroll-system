from django.contrib import admin

from apps.casuals.models import CasualAttendance, CasualPayment, CasualWorker


@admin.register(CasualWorker)
class CasualWorkerAdmin(admin.ModelAdmin):
    list_display = ['worker_id', 'first_name', 'last_name', 'daily_rate', 'branch', 'status']
    list_filter = ['company', 'branch', 'status']
    search_fields = ['first_name', 'last_name', 'worker_id', 'phone']


@admin.register(CasualAttendance)
class CasualAttendanceAdmin(admin.ModelAdmin):
    list_display = ['worker', 'date', 'hours_worked', 'amount_earned', 'is_paid']
    list_filter = ['company', 'date', 'is_paid']


@admin.register(CasualPayment)
class CasualPaymentAdmin(admin.ModelAdmin):
    list_display = ['worker', 'period_start', 'period_end', 'net_amount', 'is_paid']
    list_filter = ['company', 'is_paid']
