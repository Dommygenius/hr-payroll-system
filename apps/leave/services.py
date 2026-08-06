"""Leave business logic — pay rules, day exceptions, attendance sync."""
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.attendance.models import AttendanceRecord
from apps.leave.models import LeaveDayException, LeaveRequest, LeaveType


def get_day_pay_percentage(leave_request, day_date):
    """Resolve pay % for a specific leave day (exception overrides type default)."""
    exc = leave_request.day_exceptions.filter(date=day_date).first()
    if exc:
        if exc.pay_policy == LeaveDayException.PayPolicy.NO_PAY:
            return Decimal('0')
        if exc.pay_policy == LeaveDayException.PayPolicy.PARTIAL_PAY:
            return exc.pay_percentage
        return Decimal('100')
    lt = leave_request.leave_type
    if lt.pay_policy == LeaveType.PayPolicy.NO_PAY:
        return Decimal('0')
    if lt.pay_policy == LeaveType.PayPolicy.PARTIAL_PAY:
        return lt.pay_percentage
    return Decimal('100')


def employee_can_use_leave_type(employee, leave_type):
    """Interns only see leave types marked available_for_interns."""
    if employee.employment_type == 'intern' and not leave_type.available_for_interns:
        return False
    return True


def sync_leave_to_attendance(leave_request):
    """
    Mark attendance records as on_leave for each day in an approved leave.
    Excludes those days from present/absent counts.
    """
    if leave_request.status not in (
        LeaveRequest.Status.APPROVED,
        LeaveRequest.Status.COMPLETED,
    ):
        return 0

    updated = 0
    current = leave_request.start_date
    end = leave_request.actual_return_date or leave_request.end_date
    if leave_request.status == LeaveRequest.Status.COMPLETED and leave_request.actual_return_date:
        end = min(end, leave_request.actual_return_date - timedelta(days=1))

    while current <= leave_request.end_date and current <= end:
        record, _ = AttendanceRecord.objects.get_or_create(
            company=leave_request.company,
            employee=leave_request.employee,
            date=current,
            defaults={
                'status': AttendanceRecord.Status.ON_LEAVE,
                'is_on_approved_leave': True,
                'excluded_from_attendance': True,
                'notes': f'Approved leave: {leave_request.leave_type.name}',
            },
        )
        if record.status != AttendanceRecord.Status.ON_LEAVE or not record.excluded_from_attendance:
            record.status = AttendanceRecord.Status.ON_LEAVE
            record.is_on_approved_leave = True
            record.excluded_from_attendance = True
            record.notes = f'Approved leave: {leave_request.leave_type.name}'
            record.save(update_fields=['status', 'is_on_approved_leave', 'excluded_from_attendance', 'notes'])
            updated += 1
        current += timedelta(days=1)
    return updated


def complete_leave_request(leave_request, comment='', actual_return_date=None):
    """Mark leave completed with comment and sync attendance."""
    leave_request.status = LeaveRequest.Status.COMPLETED
    leave_request.completion_comment = comment
    leave_request.completed_at = timezone.now()
    if actual_return_date:
        leave_request.actual_return_date = actual_return_date
    leave_request.save()
    sync_leave_to_attendance(leave_request)
    return leave_request
