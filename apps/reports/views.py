from django.http import HttpResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reports.services import ReportExportService


class DashboardStatsView(APIView):
    """Aggregate dashboard counts from employees, leave, payroll, and recruitment."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.employees.models import Employee
        from apps.leave.models import LeaveRequest
        from apps.payroll.models import PayrollRun
        from apps.recruitment.models import Applicant, JobPosting

        today = timezone.now().date()
        company = getattr(request.user, 'company', None)

        employee_qs = Employee.objects.filter(is_deleted=False)
        if company:
            employee_qs = employee_qs.filter(company=company)

        leave_qs = LeaveRequest.objects.all()
        payroll_qs = PayrollRun.objects.all()
        job_qs = JobPosting.objects.all()
        applicant_qs = Applicant.objects.all()

        if company:
            leave_qs = leave_qs.filter(company=company)
            payroll_qs = payroll_qs.filter(company=company)
            job_qs = job_qs.filter(company=company)
            applicant_qs = applicant_qs.filter(company=company)

        stats = {
            'employees': {
                'total': employee_qs.count(),
                'active': employee_qs.filter(employment_status='active').count(),
            },
            'leave': {
                'pending_requests': leave_qs.filter(status='pending').count(),
                'approved_today': leave_qs.filter(
                    status='approved', start_date__lte=today, end_date__gte=today
                ).count(),
            },
            'payroll': {
                'pending_runs': payroll_qs.filter(status__in=['draft', 'review']).count(),
                'approved_runs': payroll_qs.filter(status='approved').count(),
                'paid_runs': payroll_qs.filter(status='paid').count(),
            },
            'recruitment': {
                'open_positions': job_qs.filter(status='open').count(),
                'new_applicants': applicant_qs.filter(status='new').count(),
                'total_applicants': applicant_qs.count(),
            },
        }

        return Response(stats)


class ReportExportView(APIView):
    """Export report data to Excel or PDF."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        export_format = request.data.get('format', 'excel')
        title = request.data.get('title', 'HR Report')
        headers = request.data.get('headers', [])
        data = request.data.get('data', [])

        if not headers or not data:
            return Response(
                {'error': 'headers and data are required'},
                status=400,
            )

        if export_format == 'pdf':
            buffer = ReportExportService.export_to_pdf(title, data, headers)
            content_type = 'application/pdf'
            filename = f'{title.replace(" ", "_").lower()}.pdf'
        else:
            buffer = ReportExportService.export_to_excel(data, headers)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'{title.replace(" ", "_").lower()}.xlsx'

        response = HttpResponse(buffer.read(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
