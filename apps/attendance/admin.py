from django.contrib import admin

from apps.attendance.models import AttendanceRecord, BiometricDevice, Roster, Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'start_time', 'end_time', 'is_night_shift', 'is_active']
    list_filter = ['company', 'is_active', 'is_night_shift']
    search_fields = ['name', 'code']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'check_in', 'check_out', 'hours_worked']
    list_filter = ['company', 'status', 'date', 'is_anomaly']


@admin.register(Roster)
class RosterAdmin(admin.ModelAdmin):
    list_display = ['employee', 'shift', 'date', 'is_off']
    list_filter = ['company', 'date', 'is_off']


@admin.register(BiometricDevice)
class BiometricDeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_id', 'device_type', 'branch', 'is_active', 'last_sync']
    list_filter = ['company', 'device_type', 'is_active']
    search_fields = ['name', 'device_id']
