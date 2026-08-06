"""AI service layer for HRMS intelligent features."""
import logging

logger = logging.getLogger(__name__)


class ResumeScreeningService:
    """Screen and score resumes against job requirements."""

    @staticmethod
    def screen_resume(applicant_id: str) -> dict:
        from apps.recruitment.models import Applicant

        try:
            applicant = Applicant.objects.get(pk=applicant_id)
        except Applicant.DoesNotExist:
            return {'error': 'Applicant not found'}

        score = 0.65
        keywords = ['python', 'django', 'management', 'leadership', 'experience']
        cover_lower = (applicant.cover_letter or '').lower()
        matched = [kw for kw in keywords if kw in cover_lower]
        score += len(matched) * 0.05
        score = min(score, 1.0)

        applicant.ai_score = round(score, 2)
        applicant.save(update_fields=['ai_score'])

        return {
            'applicant_id': str(applicant.id),
            'score': applicant.ai_score,
            'matched_keywords': matched,
            'recommendation': 'interview' if score >= 0.6 else 'reject',
        }


class PayrollAnomalyService:
    """Detect anomalies in payroll data."""

    @staticmethod
    def detect_anomalies(payroll_run_id: str) -> list:
        from apps.payroll.models import Payslip

        anomalies = []
        payslips = Payslip.objects.filter(payroll_run_id=payroll_run_id)

        if not payslips.exists():
            return anomalies

        avg_net = sum(p.net_pay for p in payslips) / payslips.count()

        for payslip in payslips:
            if payslip.net_pay > avg_net * 2:
                payslip.is_anomaly = True
                payslip.anomaly_reason = 'Net pay exceeds 200% of average'
                payslip.save(update_fields=['is_anomaly', 'anomaly_reason'])
                anomalies.append({
                    'payslip_id': str(payslip.id),
                    'employee': str(payslip.employee),
                    'reason': payslip.anomaly_reason,
                })

        return anomalies


class AttritionPredictionService:
    """Predict employee attrition risk."""

    @staticmethod
    def predict(employee_id: str) -> dict:
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return {'error': 'Employee not found'}

        risk_score = 0.3
        factors = []

        if employee.employment_status == 'probation':
            risk_score += 0.15
            factors.append('Currently on probation')

        warning_count = employee.warnings.filter(is_active=True).count()
        if warning_count > 0:
            risk_score += warning_count * 0.1
            factors.append(f'{warning_count} active warning(s)')

        risk_score = min(risk_score, 1.0)
        risk_level = 'high' if risk_score >= 0.7 else 'medium' if risk_score >= 0.4 else 'low'

        return {
            'employee_id': str(employee.id),
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'factors': factors,
        }


class AttendanceAnomalyService:
    """Detect attendance pattern anomalies."""

    @staticmethod
    def detect(employee_id: str, days: int = 30) -> list:
        from datetime import timedelta

        from django.utils import timezone

        from apps.attendance.models import AttendanceRecord

        start_date = timezone.now().date() - timedelta(days=days)
        records = AttendanceRecord.objects.filter(
            employee_id=employee_id, date__gte=start_date
        )

        anomalies = []
        late_count = records.filter(status='late').count()
        if late_count >= 5:
            anomalies.append({
                'type': 'frequent_late',
                'count': late_count,
                'message': f'Employee was late {late_count} times in {days} days',
            })

        return anomalies


class HRChatbotService:
    """Simple HR chatbot with keyword-based responses."""

    RESPONSES = {
        'leave': 'You can apply for leave through the Employee Self-Service portal under Leave Management.',
        'payslip': 'Your payslips are available for download in the Payroll section of your profile.',
        'attendance': 'View your attendance records in the Time & Attendance module.',
        'password': 'To reset your password, go to Account Settings > Change Password.',
    }

    @classmethod
    def respond(cls, message: str) -> str:
        message_lower = message.lower()
        for keyword, response in cls.RESPONSES.items():
            if keyword in message_lower:
                return response
        return (
            'I can help with leave, payslips, attendance, and password questions. '
            'Please ask about one of these topics.'
        )
