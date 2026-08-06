from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_payroll_run(payroll_run_id):
    """Process payroll run asynchronously."""
    from apps.payroll.models import PayrollRun
    from apps.ai_features.services import PayrollAnomalyService

    try:
        payroll_run = PayrollRun.objects.get(pk=payroll_run_id)
        payroll_run.status = PayrollRun.Status.PROCESSING
        payroll_run.save(update_fields=['status'])

        anomalies = PayrollAnomalyService.detect_anomalies(str(payroll_run_id))
        logger.info('Payroll run %s processed. Anomalies: %d', payroll_run_id, len(anomalies))

        payroll_run.status = PayrollRun.Status.REVIEW
        payroll_run.save(update_fields=['status'])
        return {'status': 'completed', 'anomalies': len(anomalies)}
    except Exception as e:
        logger.exception('Payroll processing failed: %s', e)
        return {'status': 'failed', 'error': str(e)}


@shared_task
def screen_applicant_resume(applicant_id):
    """AI resume screening task."""
    from apps.ai_features.services import ResumeScreeningService
    return ResumeScreeningService.screen_resume(applicant_id)


@shared_task
def send_notification_email(notification_id):
    """Send email notification."""
    from django.core.mail import send_mail
    from django.conf import settings
    from apps.notifications.models import Notification

    try:
        notification = Notification.objects.get(pk=notification_id)
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            fail_silently=False,
        )
        return {'status': 'sent'}
    except Exception as e:
        logger.exception('Email send failed: %s', e)
        return {'status': 'failed', 'error': str(e)}


@shared_task
def accrue_leave_balances():
    """Monthly leave accrual task."""
    from datetime import date
    from apps.leave.models import LeaveBalance, LeaveType
    from apps.employees.models import Employee

    year = date.today().year
    count = 0
    for employee in Employee.objects.filter(employment_status='active', is_deleted=False):
        for leave_type in LeaveType.objects.filter(company=employee.company, is_active=True):
            balance, created = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                year=year,
                company=employee.company,
                defaults={'entitled': leave_type.days_per_year},
            )
            if created:
                count += 1
    return {'balances_created': count}
