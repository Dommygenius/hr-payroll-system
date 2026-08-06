from django.contrib import admin

from apps.leave.models import LeaveApproval, LeaveBalance, LeaveRequest, LeaveType


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'days_per_year', 'is_paid', 'is_active']
    list_filter = ['company', 'is_active', 'is_paid']
    search_fields = ['name', 'code']


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'entitled', 'used', 'pending']
    list_filter = ['company', 'year', 'leave_type']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'status']
    list_filter = ['company', 'status', 'leave_type']


@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ['leave_request', 'approver', 'level', 'status', 'acted_at']
    list_filter = ['company', 'status']
