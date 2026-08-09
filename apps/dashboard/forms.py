"""ModelForms for dashboard module CRUD."""
from django import forms

from apps.attendance.models import (
    AttendanceCapture,
    AttendanceException,
    AttendanceRecord,
    BiometricDevice,
    BranchAttendanceSettings,
    Roster,
    Shift,
)
from apps.casuals.models import CasualAttendance, CasualPayment, CasualWorker
from apps.core.models import Branch, Department, Designation, Holiday
from apps.disciplinary.models import DisciplinaryHearing, Incident, Suspension, Warning
from apps.employees.models import Employee
from apps.leave.models import LeaveBalance, LeaveDayException, LeaveRequest, LeaveType
from apps.notifications.models import Announcement
from apps.payroll.models import Allowance, Deduction, Loan, PayrollRun, Payslip, SalaryStructure
from apps.performance.models import Goal, KPI, MonthlyTaskPerformance, PerformanceCycle, PerformanceReview, WorkSubTask, WorkTask
from apps.recruitment.models import Applicant, Interview, JobPosting, OfferLetter, OnboardingChecklist
from apps.relations.models import ExitInterview, Grievance, Recognition
from apps.surveys.models import Survey, SurveyQuestion, SurveyResponse


class CompanyModelForm(forms.ModelForm):
    """Base form that excludes company (set in view)."""

    def __init__(self, *args, company=None, **kwargs):
        self.company = company
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control')
            else:
                field.widget.attrs.setdefault('class', 'form-check-input')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company and hasattr(instance, 'company_id') and not instance.company_id:
            instance.company = self.company
        if commit:
            instance.save()
            self.save_m2m()
        return instance


def _fk_queryset(form, company, field, model):
    if company and field in form.fields:
        form.fields[field].queryset = model.objects.filter(company=company, is_active=True) if hasattr(model, 'is_active') else model.objects.filter(company=company)


class EmployeeForm(CompanyModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'middle_name', 'email', 'phone',
            'department', 'designation', 'branch', 'manager', 'employment_type',
            'employment_status', 'date_joined', 'date_confirmed', 'address', 'city', 'country',
        ]
        widgets = {'date_joined': forms.DateInput(attrs={'type': 'date'}), 'date_confirmed': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'department', Department)
            _fk_queryset(self, company, 'designation', Designation)
            _fk_queryset(self, company, 'branch', Branch)
            self.fields['manager'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class JobPostingForm(CompanyModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'department', 'designation', 'description', 'requirements', 'employment_type',
                  'salary_min', 'salary_max', 'openings', 'status', 'posted_date', 'closing_date', 'is_published']
        widgets = {'posted_date': forms.DateInput(attrs={'type': 'date'}), 'closing_date': forms.DateInput(attrs={'type': 'date'}),
                   'description': forms.Textarea(attrs={'rows': 3}), 'requirements': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'department', Department)
            _fk_queryset(self, company, 'designation', Designation)


class ApplicantForm(CompanyModelForm):
    class Meta:
        model = Applicant
        fields = ['job', 'first_name', 'last_name', 'email', 'phone', 'cover_letter', 'status', 'source']
        widgets = {'cover_letter': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['job'].queryset = JobPosting.objects.filter(company=company)


class InterviewForm(CompanyModelForm):
    class Meta:
        model = Interview
        fields = ['applicant', 'scheduled_at', 'duration_minutes', 'location', 'meeting_link', 'notes', 'rating', 'is_completed']
        widgets = {'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 'notes': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['applicant'].queryset = Applicant.objects.filter(company=company)


class PayrollRunForm(CompanyModelForm):
    class Meta:
        model = PayrollRun
        fields = ['name', 'period_start', 'period_end', 'payment_date', 'status', 'notes']
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class PayslipForm(CompanyModelForm):
    class Meta:
        model = Payslip
        fields = ['payroll_run', 'employee', 'basic_salary', 'gross_pay', 'total_deductions', 'net_pay', 'tax_amount']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['payroll_run'].queryset = PayrollRun.objects.filter(company=company)
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class LoanForm(CompanyModelForm):
    class Meta:
        model = Loan
        fields = ['employee', 'amount', 'interest_rate', 'monthly_installment', 'total_installments', 'status', 'start_date', 'purpose']
        widgets = {'start_date': forms.DateInput(attrs={'type': 'date'}), 'purpose': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class LeaveTypeForm(CompanyModelForm):
    class Meta:
        model = LeaveType
        fields = [
            'name', 'code', 'days_per_year', 'pay_policy', 'pay_percentage', 'is_paid',
            'available_for_interns', 'is_carry_forward', 'requires_approval', 'color', 'is_active',
        ]


class LeaveDayExceptionForm(CompanyModelForm):
    class Meta:
        model = LeaveDayException
        fields = ['leave_request', 'date', 'pay_policy', 'pay_percentage', 'notes']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['leave_request'].queryset = LeaveRequest.objects.filter(company=company)


class LeaveRequestForm(CompanyModelForm):
    class Meta:
        model = LeaveRequest
        fields = [
            'employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'reason',
            'status', 'rejection_reason', 'completion_comment', 'actual_return_date',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_return_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe why this leave is needed (shown during approval).',
                'class': 'form-control',
            }),
            'rejection_reason': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Required when rejecting — explain the decision for the employee.',
                'class': 'form-control',
            }),
            'completion_comment': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
        labels = {
            'reason': 'Description / Reason',
            'rejection_reason': 'Approval notes / Rejection reason',
            'status': 'Approval status',
            'days_requested': 'Days requested',
        }
        help_texts = {
            'reason': 'Employee explanation for this leave request. Approvers will see this.',
            'rejection_reason': 'If rejecting, clearly describe why. Optional note when approving.',
            'status': 'Set to Approved or Rejected to complete the approval phase.',
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)
            self.fields['leave_type'].queryset = LeaveType.objects.filter(company=company, is_active=True)
        # Highlight description during edit/approval
        if 'reason' in self.fields:
            self.fields['reason'].widget.attrs.setdefault('class', 'form-control')
            self.fields['reason'].required = True


class LeaveBalanceForm(CompanyModelForm):
    class Meta:
        model = LeaveBalance
        fields = ['employee', 'leave_type', 'year', 'entitled', 'used', 'pending', 'carried_forward']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)
            self.fields['leave_type'].queryset = LeaveType.objects.filter(company=company)


class ShiftForm(CompanyModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'code', 'start_time', 'end_time', 'break_duration_minutes', 'grace_period_minutes', 'is_night_shift', 'is_active']
        widgets = {'start_time': forms.TimeInput(attrs={'type': 'time'}), 'end_time': forms.TimeInput(attrs={'type': 'time'})}


class AttendanceRecordForm(CompanyModelForm):
    class Meta:
        model = AttendanceRecord
        fields = [
            'employee', 'date', 'shift', 'status', 'check_in', 'check_out',
            'check_in_method', 'check_out_method',
            'check_in_latitude', 'check_in_longitude', 'check_out_latitude', 'check_out_longitude',
            'hours_worked', 'overtime_hours', 'late_minutes', 'is_on_approved_leave',
            'excluded_from_attendance', 'notes',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)
            self.fields['shift'].queryset = Shift.objects.filter(company=company, is_active=True)


class RosterForm(CompanyModelForm):
    class Meta:
        model = Roster
        fields = ['employee', 'shift', 'date', 'is_off', 'notes']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)
            self.fields['shift'].queryset = Shift.objects.filter(company=company, is_active=True)


class PerformanceCycleForm(CompanyModelForm):
    class Meta:
        model = PerformanceCycle
        fields = ['name', 'start_date', 'end_date', 'review_deadline', 'status', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'review_deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class GoalForm(CompanyModelForm):
    class Meta:
        model = Goal
        fields = ['employee', 'cycle', 'title', 'description', 'target_value', 'due_date', 'status', 'progress']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'}), 'description': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)
            self.fields['cycle'].queryset = PerformanceCycle.objects.filter(company=company)


class PerformanceReviewForm(CompanyModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['employee', 'cycle', 'status', 'overall_rating', 'self_assessment', 'manager_comments', 'strengths', 'areas_for_improvement']
        widgets = {
            'self_assessment': forms.Textarea(attrs={'rows': 2}),
            'manager_comments': forms.Textarea(attrs={'rows': 2}),
            'strengths': forms.Textarea(attrs={'rows': 2}),
            'areas_for_improvement': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)
            self.fields['cycle'].queryset = PerformanceCycle.objects.filter(company=company)


class KPIForm(CompanyModelForm):
    class Meta:
        model = KPI
        fields = ['name', 'description', 'measurement_unit', 'target', 'department', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'department', Department)


class GrievanceForm(CompanyModelForm):
    class Meta:
        model = Grievance
        fields = ['employee', 'subject', 'description', 'status', 'priority', 'resolution']
        widgets = {'description': forms.Textarea(attrs={'rows': 3}), 'resolution': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class RecognitionForm(CompanyModelForm):
    class Meta:
        model = Recognition
        fields = ['employee', 'title', 'description', 'category', 'award_date']
        widgets = {'award_date': forms.DateInput(attrs={'type': 'date'}), 'description': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class IncidentForm(CompanyModelForm):
    class Meta:
        model = Incident
        fields = ['employee', 'incident_date', 'description', 'severity', 'status', 'location', 'action_taken']
        widgets = {'incident_date': forms.DateInput(attrs={'type': 'date'}), 'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class WarningForm(CompanyModelForm):
    class Meta:
        model = Warning
        fields = ['employee', 'warning_type', 'issue_date', 'description', 'expiry_date', 'is_active']
        widgets = {'issue_date': forms.DateInput(attrs={'type': 'date'}), 'expiry_date': forms.DateInput(attrs={'type': 'date'}),
                   'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class CasualWorkerForm(CompanyModelForm):
    class Meta:
        model = CasualWorker
        fields = ['worker_id', 'first_name', 'last_name', 'phone', 'id_number', 'daily_rate', 'branch', 'status', 'date_registered']
        widgets = {'date_registered': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'branch', Branch)


class CasualAttendanceForm(CompanyModelForm):
    class Meta:
        model = CasualAttendance
        fields = ['worker', 'date', 'hours_worked', 'daily_rate', 'amount_earned', 'is_paid']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['worker'].queryset = CasualWorker.objects.filter(company=company)


class SurveyForm(CompanyModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'status', 'start_date', 'end_date', 'is_anonymous']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class BranchForm(CompanyModelForm):
    class Meta:
        model = Branch
        fields = [
            'name', 'code', 'address', 'city', 'country', 'phone', 'email',
            'latitude', 'longitude', 'geofence_radius_meters',
            'is_headquarters', 'is_active',
        ]
        widgets = {'address': forms.Textarea(attrs={'rows': 2})}


class DepartmentForm(CompanyModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'branch', 'parent', 'description', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'branch', Branch)
            self.fields['parent'].queryset = Department.objects.filter(company=company, is_active=True)


class DesignationForm(CompanyModelForm):
    class Meta:
        model = Designation
        fields = ['title', 'code', 'level', 'description', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}


class HolidayForm(CompanyModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'date', 'is_recurring', 'branch', 'country']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'branch', Branch)


class AnnouncementForm(CompanyModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_pinned', 'publish_date', 'expiry_date', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            'publish_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AttendanceExceptionForm(CompanyModelForm):
    class Meta:
        model = AttendanceException
        fields = ['attendance_record', 'exception_type', 'reason', 'minutes_affected', 'status', 'hr_comment']
        widgets = {'reason': forms.Textarea(attrs={'rows': 2}), 'hr_comment': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['attendance_record'].queryset = AttendanceRecord.objects.filter(company=company)


class AttendanceCaptureForm(CompanyModelForm):
    class Meta:
        model = AttendanceCapture
        fields = ['employee', 'attendance_record', 'capture_type', 'photo', 'latitude', 'longitude', 'method', 'device']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)
            self.fields['attendance_record'].queryset = AttendanceRecord.objects.filter(company=company)
            self.fields['device'].queryset = BiometricDevice.objects.filter(company=company)


class BiometricDeviceForm(CompanyModelForm):
    class Meta:
        model = BiometricDevice
        fields = ['name', 'device_id', 'device_type', 'branch', 'ip_address', 'is_active', 'allow_manual_fallback']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'branch', Branch)


class BranchAttendanceSettingsForm(CompanyModelForm):
    class Meta:
        model = BranchAttendanceSettings
        fields = [
            'branch', 'allow_manual', 'allow_gps', 'allow_face', 'allow_biometric',
            'require_photo', 'require_gps', 'geofence_radius_meters',
        ]

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'branch', Branch)


class WorkTaskForm(CompanyModelForm):
    class Meta:
        model = WorkTask
        fields = [
            'title', 'description', 'assigned_to', 'start_date', 'due_date',
            'status', 'priority', 'max_points', 'weight',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['assigned_to'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class WorkSubTaskForm(CompanyModelForm):
    class Meta:
        model = WorkSubTask
        fields = ['task', 'title', 'description', 'due_date', 'status', 'weight']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['task'].queryset = WorkTask.objects.filter(company=company)


class MonthlyTaskPerformanceForm(CompanyModelForm):
    class Meta:
        model = MonthlyTaskPerformance
        fields = [
            'employee', 'year', 'month', 'tasks_assigned', 'tasks_completed',
            'tasks_on_time', 'total_points', 'performance_score', 'bonus_eligible',
        ]

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, company=company, **kwargs)
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company, is_deleted=False)


class UserAccountForm(CompanyModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False, label='Confirm password')

    class Meta:
        from apps.accounts.models import User
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'role', 'phone', 'branch', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'role': 'Role',
        }
        help_texts = {
            'role': 'Promote or demote this user within roles enabled for your organization.',
        }

    def __init__(self, *args, company=None, request_user=None, **kwargs):
        self.request_user = request_user
        super().__init__(*args, company=company, **kwargs)
        if company:
            _fk_queryset(self, company, 'branch', Branch)
        if self.instance and self.instance.pk:
            self.fields['password'].help_text = 'Leave blank to keep current password.'

        from apps.accounts.roles import assignable_role_choices
        current = getattr(self.instance, 'role', None) if self.instance and self.instance.pk else None
        actor = self.request_user
        self.fields['role'].choices = assignable_role_choices(actor, company, current_role=current)

    def clean_role(self):
        from apps.accounts.models import User, UserRole
        from apps.accounts.roles import can_configure_tenant_roles, get_enabled_roles

        role = self.cleaned_data.get('role')
        company = self.company or getattr(self.instance, 'company', None)
        enabled = set(get_enabled_roles(company))
        current = getattr(self.instance, 'role', None) if self.instance and self.instance.pk else None
        if role not in enabled and role != current:
            raise forms.ValidationError('That role is not enabled for this organization.')

        actor = self.request_user
        if role == UserRole.SUPER_ADMIN and actor and not can_configure_tenant_roles(actor):
            raise forms.ValidationError('Only a Super Admin can assign the Super Admin role.')

        # Prevent removing the last active super admin in the tenant
        if (
            self.instance and self.instance.pk
            and current == UserRole.SUPER_ADMIN
            and role != UserRole.SUPER_ADMIN
            and company
        ):
            remaining = User.objects.filter(
                company=company,
                role=UserRole.SUPER_ADMIN,
                is_active=True,
            ).exclude(pk=self.instance.pk).count()
            if remaining < 1:
                raise forms.ValidationError(
                    'Cannot demote the last Super Admin for this organization. Promote another user first.'
                )
        return role

    def clean(self):
        cleaned = super().clean()
        pw, pw2 = cleaned.get('password'), cleaned.get('password_confirm')
        if pw or pw2:
            if pw != pw2:
                raise forms.ValidationError('Passwords do not match.')
            if len(pw) < 8:
                raise forms.ValidationError('Password must be at least 8 characters.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        pw = self.cleaned_data.get('password')
        if pw:
            instance.set_password(pw)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

