"""Module registry for dashboard CRUD UI."""

from apps.accounts.models import User
from apps.attendance.models import (
    AttendanceCapture,
    AttendanceException,
    AttendanceRecord,
    BiometricDevice,
    BranchAttendanceSettings,
    Roster,
    Shift,
)
from apps.casuals.models import CasualAttendance, CasualWorker
from apps.core.models import Branch, Department, Designation, Holiday
from apps.disciplinary.models import Incident, Warning
from apps.employees.models import Employee
from apps.leave.models import LeaveBalance, LeaveDayException, LeaveRequest, LeaveType
from apps.payroll.models import Loan, PayrollRun, Payslip
from apps.performance.models import Goal, KPI, MonthlyTaskPerformance, PerformanceCycle, PerformanceReview, WorkSubTask, WorkTask
from apps.recruitment.models import Applicant, Interview, JobPosting
from apps.relations.models import Grievance, Recognition
from apps.surveys.models import Survey

from apps.dashboard import forms as F

MODULES = {
    'employees': {
        'title': 'Employee Management',
        'icon': 'bi-people',
        'tabs': [
            {
                'key': 'list',
                'label': 'Employees',
                'model': Employee,
                'form': F.EmployeeForm,
                'filter': {'is_deleted': False},
                'select_related': ['department', 'designation', 'branch', 'manager'],
                'search_fields': ['first_name', 'last_name', 'employee_id', 'email'],
                'columns': [
                    ('employee_id', 'ID'),
                    ('full_name', 'Name'),
                    ('email', 'Email'),
                    ('department', 'Department'),
                    ('designation', 'Designation'),
                    ('employment_status', 'Status'),
                ],
                'detail_fields': [
                    ('employee_id', 'Employee ID'),
                    ('full_name', 'Full name'),
                    ('email', 'Email'),
                    ('phone', 'Phone'),
                    ('department', 'Department'),
                    ('designation', 'Designation'),
                    ('branch', 'Branch'),
                    ('manager', 'Manager'),
                    ('employment_type', 'Employment type'),
                    ('employment_status', 'Status'),
                    ('date_joined', 'Date joined'),
                    ('date_confirmed', 'Date confirmed'),
                    ('address', 'Address'),
                    ('city', 'City'),
                    ('country', 'Country'),
                ],
                'soft_delete': True,
            },
        ],
    },
    'recruitment': {
        'title': 'Recruitment & Onboarding',
        'icon': 'bi-person-plus',
        'tabs': [
            {
                'key': 'jobs',
                'label': 'Job Postings',
                'model': JobPosting,
                'form': F.JobPostingForm,
                'select_related': ['department', 'designation'],
                'search_fields': ['title'],
                'columns': [('title', 'Title'), ('department', 'Dept'), ('status', 'Status'), ('openings', 'Openings'), ('closing_date', 'Closes')],
            },
            {
                'key': 'applicants',
                'label': 'Applicants',
                'model': Applicant,
                'form': F.ApplicantForm,
                'select_related': ['job'],
                'search_fields': ['first_name', 'last_name', 'email'],
                'columns': [('full_name', 'Name'), ('job', 'Job'), ('status', 'Status'), ('ai_score', 'AI Score'), ('email', 'Email')],
            },
            {
                'key': 'interviews',
                'label': 'Interviews',
                'model': Interview,
                'form': F.InterviewForm,
                'select_related': ['applicant'],
                'columns': [('applicant', 'Applicant'), ('scheduled_at', 'Scheduled'), ('rating', 'Rating'), ('is_completed', 'Done')],
            },
        ],
    },
    'payroll': {
        'title': 'Payroll & Compliance',
        'icon': 'bi-cash-stack',
        'tabs': [
            {
                'key': 'runs',
                'label': 'Payroll Runs',
                'model': PayrollRun,
                'form': F.PayrollRunForm,
                'columns': [('name', 'Name'), ('period_start', 'Start'), ('period_end', 'End'), ('status', 'Status'), ('total_net', 'Net Total')],
            },
            {
                'key': 'payslips',
                'label': 'Payslips',
                'model': Payslip,
                'form': F.PayslipForm,
                'select_related': ['employee', 'payroll_run'],
                'columns': [('employee', 'Employee'), ('payroll_run', 'Run'), ('gross_pay', 'Gross'), ('net_pay', 'Net'), ('is_anomaly', 'Anomaly')],
            },
            {
                'key': 'loans',
                'label': 'Loans',
                'model': Loan,
                'form': F.LoanForm,
                'select_related': ['employee'],
                'columns': [('employee', 'Employee'), ('amount', 'Amount'), ('status', 'Status'), ('monthly_installment', 'Monthly')],
            },
        ],
    },
    'leave': {
        'title': 'Leave Management',
        'icon': 'bi-calendar-check',
        'tabs': [
            {
                'key': 'requests',
                'label': 'Leave Requests',
                'model': LeaveRequest,
                'form': F.LeaveRequestForm,
                'select_related': ['employee', 'leave_type'],
                'columns': [
                    ('employee', 'Employee'),
                    ('leave_type', 'Type'),
                    ('start_date', 'From'),
                    ('end_date', 'To'),
                    ('days_requested', 'Days'),
                    ('reason', 'Description'),
                    ('status', 'Status'),
                ],
            },
            {
                'key': 'exceptions',
                'label': 'Day Exceptions',
                'model': LeaveDayException,
                'form': F.LeaveDayExceptionForm,
                'select_related': ['leave_request'],
                'columns': [('leave_request', 'Request'), ('date', 'Date'), ('pay_policy', 'Pay Policy'), ('pay_percentage', 'Pay %'), ('notes', 'Notes')],
            },
            {
                'key': 'types',
                'label': 'Leave Types',
                'model': LeaveType,
                'form': F.LeaveTypeForm,
                'columns': [('name', 'Name'), ('code', 'Code'), ('days_per_year', 'Days/Year'), ('pay_policy', 'Pay Policy'), ('pay_percentage', 'Pay %'), ('available_for_interns', 'Interns'), ('is_active', 'Active')],
            },
            {
                'key': 'balances',
                'label': 'Balances',
                'model': LeaveBalance,
                'form': F.LeaveBalanceForm,
                'select_related': ['employee', 'leave_type'],
                'columns': [('employee', 'Employee'), ('leave_type', 'Type'), ('year', 'Year'), ('entitled', 'Entitled'), ('used', 'Used')],
            },
        ],
    },
    'attendance': {
        'title': 'Time & Attendance',
        'icon': 'bi-clock-history',
        'tabs': [
            {
                'key': 'records',
                'label': 'Attendance',
                'model': AttendanceRecord,
                'form': F.AttendanceRecordForm,
                'select_related': ['employee', 'shift'],
                'columns': [('employee', 'Employee'), ('date', 'Date'), ('status', 'Status'), ('check_in_method', 'Method'), ('late_minutes', 'Late Min'), ('hours_worked', 'Hours')],
            },
            {
                'key': 'exceptions',
                'label': 'Exceptions',
                'model': AttendanceException,
                'form': F.AttendanceExceptionForm,
                'select_related': ['attendance_record'],
                'columns': [('attendance_record', 'Record'), ('exception_type', 'Type'), ('minutes_affected', 'Minutes'), ('status', 'Status')],
            },
            {
                'key': 'captures',
                'label': 'Photo / GPS',
                'model': AttendanceCapture,
                'form': F.AttendanceCaptureForm,
                'select_related': ['employee'],
                'columns': [('employee', 'Employee'), ('capture_type', 'Type'), ('latitude', 'Lat'), ('longitude', 'Lng'), ('method', 'Method'), ('captured_at', 'Time')],
            },
            {
                'key': 'devices',
                'label': 'Biometric Devices',
                'model': BiometricDevice,
                'form': F.BiometricDeviceForm,
                'columns': [('name', 'Name'), ('device_type', 'Type'), ('branch', 'Branch'), ('is_active', 'Active')],
            },
            {
                'key': 'settings',
                'label': 'Check-in Methods',
                'model': BranchAttendanceSettings,
                'form': F.BranchAttendanceSettingsForm,
                'columns': [('branch', 'Branch'), ('allow_manual', 'Manual'), ('allow_gps', 'GPS'), ('allow_face', 'Face'), ('allow_biometric', 'Biometric')],
            },
            {
                'key': 'shifts',
                'label': 'Shifts',
                'model': Shift,
                'form': F.ShiftForm,
                'columns': [('name', 'Name'), ('code', 'Code'), ('start_time', 'Start'), ('end_time', 'End'), ('is_active', 'Active')],
            },
            {
                'key': 'rosters',
                'label': 'Rosters',
                'model': Roster,
                'form': F.RosterForm,
                'select_related': ['employee', 'shift'],
                'columns': [('employee', 'Employee'), ('shift', 'Shift'), ('date', 'Date'), ('is_off', 'Off Day')],
            },
        ],
    },
    'performance': {
        'title': 'Performance Management',
        'icon': 'bi-graph-up-arrow',
        'tabs': [
            {
                'key': 'tasks',
                'label': 'Tasks',
                'model': WorkTask,
                'form': F.WorkTaskForm,
                'select_related': ['assigned_to'],
                'columns': [('title', 'Title'), ('assigned_to', 'Assignee'), ('due_date', 'Due'), ('status', 'Status'), ('max_points', 'Points'), ('earned_points', 'Earned')],
            },
            {
                'key': 'subtasks',
                'label': 'Sub-tasks',
                'model': WorkSubTask,
                'form': F.WorkSubTaskForm,
                'select_related': ['task'],
                'columns': [('task', 'Task'), ('title', 'Title'), ('due_date', 'Due'), ('status', 'Status'), ('weight', 'Weight %')],
            },
            {
                'key': 'monthly-scores',
                'label': 'Monthly Performance',
                'model': MonthlyTaskPerformance,
                'form': F.MonthlyTaskPerformanceForm,
                'select_related': ['employee'],
                'columns': [('employee', 'Employee'), ('year', 'Year'), ('month', 'Month'), ('tasks_completed', 'Done'), ('tasks_on_time', 'On Time'), ('performance_score', 'Score'), ('bonus_eligible', 'Bonus')],
            },
            {
                'key': 'cycles',
                'label': 'Review Cycles',
                'model': PerformanceCycle,
                'form': F.PerformanceCycleForm,
                'columns': [('name', 'Name'), ('start_date', 'Start'), ('end_date', 'End'), ('status', 'Status')],
            },
            {
                'key': 'goals',
                'label': 'Goals',
                'model': Goal,
                'form': F.GoalForm,
                'select_related': ['employee', 'cycle'],
                'columns': [('title', 'Title'), ('employee', 'Employee'), ('status', 'Status'), ('progress', 'Progress %')],
            },
            {
                'key': 'reviews',
                'label': 'Reviews',
                'model': PerformanceReview,
                'form': F.PerformanceReviewForm,
                'select_related': ['employee', 'cycle'],
                'columns': [('employee', 'Employee'), ('cycle', 'Cycle'), ('status', 'Status'), ('overall_rating', 'Rating')],
            },
            {
                'key': 'kpis',
                'label': 'KPIs',
                'model': KPI,
                'form': F.KPIForm,
                'columns': [('name', 'Name'), ('measurement_unit', 'Unit'), ('target', 'Target'), ('is_active', 'Active')],
            },
        ],
    },
    'relations': {
        'title': 'Employee Relations',
        'icon': 'bi-heart',
        'tabs': [
            {
                'key': 'grievances',
                'label': 'Grievances',
                'model': Grievance,
                'form': F.GrievanceForm,
                'select_related': ['employee'],
                'columns': [('subject', 'Subject'), ('employee', 'Employee'), ('priority', 'Priority'), ('status', 'Status')],
            },
            {
                'key': 'recognitions',
                'label': 'Recognition',
                'model': Recognition,
                'form': F.RecognitionForm,
                'select_related': ['employee'],
                'columns': [('title', 'Title'), ('employee', 'Employee'), ('category', 'Category'), ('award_date', 'Date')],
            },
        ],
    },
    'disciplinary': {
        'title': 'Disciplinary Management',
        'icon': 'bi-shield-exclamation',
        'tabs': [
            {
                'key': 'incidents',
                'label': 'Incidents',
                'model': Incident,
                'form': F.IncidentForm,
                'select_related': ['employee'],
                'columns': [('employee', 'Employee'), ('incident_date', 'Date'), ('severity', 'Severity'), ('status', 'Status')],
            },
            {
                'key': 'warnings',
                'label': 'Warnings',
                'model': Warning,
                'form': F.WarningForm,
                'select_related': ['employee'],
                'columns': [('employee', 'Employee'), ('warning_type', 'Type'), ('issue_date', 'Issued'), ('is_active', 'Active')],
            },
        ],
    },
    'casuals': {
        'title': 'Casuals Management',
        'icon': 'bi-person-workspace',
        'tabs': [
            {
                'key': 'workers',
                'label': 'Casual Workers',
                'model': CasualWorker,
                'form': F.CasualWorkerForm,
                'columns': [('worker_id', 'ID'), ('first_name', 'First'), ('last_name', 'Last'), ('daily_rate', 'Daily Rate'), ('status', 'Status')],
            },
            {
                'key': 'attendance',
                'label': 'Attendance',
                'model': CasualAttendance,
                'form': F.CasualAttendanceForm,
                'select_related': ['worker'],
                'columns': [('worker', 'Worker'), ('date', 'Date'), ('hours_worked', 'Hours'), ('amount_earned', 'Earned'), ('is_paid', 'Paid')],
            },
        ],
    },
    'surveys': {
        'title': 'Feedback & Surveys',
        'icon': 'bi-chat-square-text',
        'tabs': [
            {
                'key': 'surveys',
                'label': 'Surveys',
                'model': Survey,
                'form': F.SurveyForm,
                'columns': [('title', 'Title'), ('status', 'Status'), ('start_date', 'Start'), ('end_date', 'End'), ('is_anonymous', 'Anonymous')],
            },
        ],
    },
    'settings': {
        'title': 'System Settings',
        'icon': 'bi-gear',
        'tabs': [
            {
                'key': 'users',
                'label': 'Users & Roles',
                'model': User,
                'form': F.UserAccountForm,
                'columns': [('email', 'Email'), ('first_name', 'First Name'), ('last_name', 'Last Name'), ('role', 'Role'), ('is_active', 'Active')],
            },
            {
                'key': 'branches',
                'label': 'Branches',
                'model': Branch,
                'form': F.BranchForm,
                'columns': [('name', 'Name'), ('code', 'Code'), ('city', 'City'), ('is_headquarters', 'HQ'), ('is_active', 'Active')],
            },
            {
                'key': 'departments',
                'label': 'Departments',
                'model': Department,
                'form': F.DepartmentForm,
                'select_related': ['branch'],
                'columns': [('name', 'Name'), ('code', 'Code'), ('branch', 'Branch'), ('is_active', 'Active')],
            },
            {
                'key': 'designations',
                'label': 'Designations',
                'model': Designation,
                'form': F.DesignationForm,
                'columns': [('title', 'Title'), ('code', 'Code'), ('level', 'Level'), ('is_active', 'Active')],
            },
            {
                'key': 'holidays',
                'label': 'Holidays',
                'model': Holiday,
                'form': F.HolidayForm,
                'columns': [('name', 'Name'), ('date', 'Date'), ('is_recurring', 'Recurring'), ('country', 'Country')],
            },
        ],
    },
}

SPECIAL_MODULES = {'reports', 'ai'}


def get_module(module_name):
    return MODULES.get(module_name)


def get_tab(module_name, tab_key):
    mod = get_module(module_name)
    if not mod:
        return None
    for tab in mod['tabs']:
        if tab['key'] == tab_key:
            return tab
    return mod['tabs'][0] if mod['tabs'] else None
