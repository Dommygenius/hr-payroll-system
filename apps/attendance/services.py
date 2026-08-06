"""Attendance check-in logic — GPS, face, manual, late exceptions, leave exclusion."""
from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.accounts.permissions import can_manage_attendance
from apps.attendance.models import (
    AttendanceCapture,
    AttendanceException,
    AttendanceRecord,
    BranchAttendanceSettings,
    Shift,
)
from apps.leave.models import LeaveRequest


def _employee_on_leave(employee, date):
    return LeaveRequest.objects.filter(
        employee=employee,
        status__in=[LeaveRequest.Status.APPROVED, LeaveRequest.Status.COMPLETED],
        start_date__lte=date,
        end_date__gte=date,
    ).exists()


def get_branch_settings(employee):
    branch = employee.branch
    if not branch:
        return None
    settings, _ = BranchAttendanceSettings.objects.get_or_create(
        company=employee.company,
        branch=branch,
        defaults={
            'allow_manual': True,
            'allow_gps': True,
            'allow_face': True,
            'allow_biometric': True,
        },
    )
    return settings


def _calc_late_minutes(check_in_dt, shift):
    if not shift or not check_in_dt:
        return 0
    shift_start = datetime.combine(check_in_dt.date(), shift.start_time)
    if timezone.is_aware(check_in_dt):
        shift_start = timezone.make_aware(shift_start, timezone.get_current_timezone())
    grace = timedelta(minutes=shift.grace_period_minutes or 0)
    if check_in_dt > shift_start + grace:
        return int((check_in_dt - shift_start).total_seconds() / 60)
    return 0


def _validate_geofence(employee, latitude, longitude):
    branch = employee.branch
    if not branch or branch.latitude is None or branch.longitude is None:
        return True, ''
    from math import radians, sin, cos, sqrt, atan2

    r = 6371000
    lat1, lon1 = radians(float(branch.latitude)), radians(float(branch.longitude))
    lat2, lon2 = radians(float(latitude)), radians(float(longitude))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dist = 2 * r * atan2(sqrt(a), sqrt(1 - a))
    radius = branch.geofence_radius_meters or 200
    settings = get_branch_settings(employee)
    if settings:
        radius = settings.geofence_radius_meters or radius
    if dist > radius:
        return False, f'Outside geofence ({int(dist)}m from branch, max {radius}m)'
    return True, ''


def clock_in(employee, method, latitude=None, longitude=None, photo=None, device=None, user=None):
    """
    Check in with optional GPS + photo. Creates late exception if applicable.
    Skips if employee is on approved leave.
    """
    today = timezone.localdate()
    if _employee_on_leave(employee, today):
        return None, 'Employee is on approved leave today — attendance excluded.'

    settings = get_branch_settings(employee)
    method_map = {
        'manual': settings.allow_manual if settings else True,
        'geolocation': settings.allow_gps if settings else True,
        'face_recognition': settings.allow_face if settings else True,
        'biometric': settings.allow_biometric if settings else True,
    }
    if method in method_map and not method_map.get(method, True):
        return None, f'{method} check-in is not enabled for this branch.'

    if settings and settings.require_gps and (latitude is None or longitude is None):
        return None, 'GPS coordinates are required for check-in.'

    geofence_ok, geofence_msg = True, ''
    if latitude is not None and longitude is not None:
        geofence_ok, geofence_msg = _validate_geofence(employee, latitude, longitude)

    shift = Shift.objects.filter(company=employee.company, is_active=True).first()
    roster = employee.rosters.filter(date=today).select_related('shift').first()
    if roster and roster.shift:
        shift = roster.shift

    now = timezone.now()
    record, created = AttendanceRecord.objects.get_or_create(
        company=employee.company,
        employee=employee,
        date=today,
        defaults={'shift': shift},
    )

    record.check_in = now
    record.check_in_method = method
    if latitude is not None:
        record.check_in_latitude = Decimal(str(latitude))
    if longitude is not None:
        record.check_in_longitude = Decimal(str(longitude))

    late_mins = _calc_late_minutes(now, shift or record.shift)
    record.late_minutes = late_mins
    if late_mins > 0:
        record.status = AttendanceRecord.Status.LATE
        AttendanceException.objects.get_or_create(
            company=employee.company,
            attendance_record=record,
            exception_type=AttendanceException.ExceptionType.LATE,
            defaults={
                'minutes_affected': late_mins,
                'reason': f'Late by {late_mins} minutes',
                'status': AttendanceException.Status.PENDING,
            },
        )
    else:
        record.status = AttendanceRecord.Status.PRESENT

    if not geofence_ok:
        record.is_anomaly = True
        AttendanceException.objects.get_or_create(
            company=employee.company,
            attendance_record=record,
            exception_type=AttendanceException.ExceptionType.GPS_MISMATCH,
            defaults={
                'reason': geofence_msg,
                'status': AttendanceException.Status.PENDING,
            },
        )

    record.excluded_from_attendance = False
    record.is_on_approved_leave = False
    record.save()

    if photo and latitude is not None and longitude is not None:
        AttendanceCapture.objects.create(
            company=employee.company,
            employee=employee,
            attendance_record=record,
            capture_type=AttendanceCapture.CaptureType.CHECK_IN,
            photo=photo,
            latitude=Decimal(str(latitude)),
            longitude=Decimal(str(longitude)),
            method=method,
            device=device,
        )

    return record, 'Check-in recorded.' if created else 'Check-in updated.'


def clock_out(employee, method, latitude=None, longitude=None, photo=None, device=None):
    today = timezone.localdate()
    try:
        record = AttendanceRecord.objects.get(employee=employee, date=today)
    except AttendanceRecord.DoesNotExist:
        return None, 'No check-in found for today.'

    now = timezone.now()
    record.check_out = now
    record.check_out_method = method
    if latitude is not None:
        record.check_out_latitude = Decimal(str(latitude))
    if longitude is not None:
        record.check_out_longitude = Decimal(str(longitude))

    if record.check_in and record.check_out:
        delta = record.check_out - record.check_in
        record.hours_worked = round(delta.total_seconds() / 3600, 2)

    record.save()

    if photo and latitude is not None and longitude is not None:
        AttendanceCapture.objects.create(
            company=employee.company,
            employee=employee,
            attendance_record=record,
            capture_type=AttendanceCapture.CaptureType.CHECK_OUT,
            photo=photo,
            latitude=Decimal(str(latitude)),
            longitude=Decimal(str(longitude)),
            method=method,
            device=device,
        )

    return record, 'Check-out recorded.'


def approve_exception(exception, user, comment=''):
    if not can_manage_attendance(user):
        return False, 'Only HR can approve attendance exceptions.'
    exception.status = AttendanceException.Status.APPROVED
    exception.approved_by = user
    exception.approved_at = timezone.now()
    exception.hr_comment = comment
    exception.save()
    return True, 'Exception approved.'
