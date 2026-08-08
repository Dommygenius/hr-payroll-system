"""Seed HRMS with rich sample data for development/demo."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial HRMS data for development'

    def handle(self, *args, **options):
        from apps.accounts.models import PermissionGroup
        from apps.attendance.models import (
            AttendanceException,
            AttendanceRecord,
            BranchAttendanceSettings,
            Shift,
        )
        from apps.core.models import Branch, Company, Department, Designation, Holiday
        from apps.employees.models import Employee
        from apps.leave.models import LeaveBalance, LeaveDayException, LeaveRequest, LeaveType
        from apps.leave.services import sync_leave_to_attendance
        from apps.notifications.models import Announcement, Notification
        from apps.payroll.models import PayrollRun
        from apps.performance.models import MonthlyTaskPerformance, PerformanceCycle, WorkSubTask, WorkTask
        from apps.performance.task_service import complete_subtask, refresh_monthly_performance
        from apps.recruitment.models import Applicant, JobPosting

        self.stdout.write('Seeding HRMS data...')

        company, _ = Company.objects.get_or_create(
            slug='acme-corp',
            defaults={
                'name': 'Acme Corporation',
                'legal_name': 'Acme Corporation Ltd.',
                'email': 'hr@acme.com',
                'country': 'US',
                'default_currency': 'USD',
                'city': 'New York',
            },
        )

        branch, _ = Branch.objects.get_or_create(
            company=company, code='HQ',
            defaults={
                'name': 'Headquarters',
                'is_headquarters': True,
                'city': 'New York',
                'latitude': Decimal('40.712800'),
                'longitude': Decimal('-74.006000'),
                'geofence_radius_meters': 300,
            },
        )
        Branch.objects.update_or_create(
            company=company, code='WEST',
            defaults={
                'name': 'West Coast Office',
                'city': 'San Francisco',
                'latitude': Decimal('37.774900'),
                'longitude': Decimal('-122.419400'),
                'geofence_radius_meters': 250,
            },
        )

        dept_map = {}
        for code, name in [
            ('HR', 'Human Resources'),
            ('IT', 'Information Technology'),
            ('FIN', 'Finance'),
            ('OPS', 'Operations'),
            ('MKT', 'Marketing'),
        ]:
            d, _ = Department.objects.get_or_create(
                company=company, code=code,
                defaults={'name': name, 'branch': branch},
            )
            dept_map[code] = d

        desig_map = {}
        for code, title, level in [
            ('CEO', 'Chief Executive Officer', 10),
            ('MGR', 'Manager', 5),
            ('SR', 'Senior Specialist', 3),
            ('SPEC', 'Specialist', 2),
            ('JR', 'Junior Associate', 1),
            ('INT', 'Intern', 0),
        ]:
            d, _ = Designation.objects.get_or_create(
                company=company, code=code,
                defaults={'title': title, 'level': level},
            )
            desig_map[code] = d

        admin_user, created = User.objects.get_or_create(
            email='admin@acme.com',
            defaults={
                'username': 'admin',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'super_admin',
                'company': company,
                'branch': branch,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin_user.set_password('Admin@123456')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('  Admin: admin@acme.com / Admin@123456'))

        hr_user, created = User.objects.get_or_create(
            email='hr@acme.com',
            defaults={
                'username': 'hr_admin',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'hr_admin',
                'company': company,
                'branch': branch,
                'is_staff': True,
            },
        )
        if created:
            hr_user.set_password('Hr@12345678')
            hr_user.save()
            self.stdout.write(self.style.SUCCESS('  HR Admin: hr@acme.com / Hr@12345678'))

        manager_user, manager_created = User.objects.get_or_create(
            email='manager@acme.com',
            defaults={
                'username': 'manager',
                'first_name': 'Robert',
                'last_name': 'Chen',
                'role': 'manager',
                'company': company,
                'branch': branch,
                'is_staff': False,
            },
        )
        if manager_created or not manager_user.has_usable_password():
            manager_user.set_password('Manager@123456')
            manager_user.role = 'manager'
            manager_user.company = company
            manager_user.save()
            self.stdout.write(self.style.SUCCESS('  Manager: manager@acme.com / Manager@123456'))

        leave_type_defs = [
            ('ANNUAL', 'Annual Leave', 21, 'full_pay', 100, True),
            ('SICK', 'Sick Leave', 10, 'full_pay', 100, True),
            ('UNPAID', 'Unpaid Leave', 5, 'no_pay', 0, False),
            ('HALF', 'Half Pay Leave', 3, 'partial_pay', 50, False),
            ('INT', 'Intern Leave', 5, 'full_pay', 100, True),
        ]
        lt_map = {}
        for code, name, days, policy, pct, interns in leave_type_defs:
            lt, _ = LeaveType.objects.update_or_create(
                company=company, code=code,
                defaults={
                    'name': name,
                    'days_per_year': days,
                    'pay_policy': policy,
                    'pay_percentage': pct,
                    'available_for_interns': interns,
                    'is_paid': policy != 'no_pay',
                    'color': '#0d9488' if policy == 'full_pay' else '#f59e0b',
                },
            )
            lt_map[code] = lt

        PermissionGroup.objects.get_or_create(
            codename='hr-administrators',
            defaults={
                'name': 'HR Administrators',
                'description': 'Full HR module access',
                'company': company,
                'permissions': ['employees.*', 'leave.*', 'recruitment.*'],
            },
        )

        BranchAttendanceSettings.objects.get_or_create(
            company=company, branch=branch,
            defaults={
                'allow_manual': True,
                'allow_gps': True,
                'allow_face': True,
                'allow_biometric': True,
                'require_gps': False,
            },
        )

        shift, _ = Shift.objects.get_or_create(
            company=company, code='STD',
            defaults={
                'name': 'Standard 9-5',
                'start_time': '09:00',
                'end_time': '17:00',
                'grace_period_minutes': 15,
            },
        )

        employee_defs = [
            ('EMP001', 'John', 'Doe', 'john.doe@acme.com', 'IT', 'MGR', 'full_time'),
            ('EMP002', 'Sarah', 'Johnson', 'sarah.johnson@acme.com', 'HR', 'SR', 'full_time'),
            ('EMP003', 'Michael', 'Brown', 'michael.brown@acme.com', 'FIN', 'SPEC', 'full_time'),
            ('EMP004', 'Emily', 'Davis', 'emily.davis@acme.com', 'MKT', 'SPEC', 'full_time'),
            ('EMP005', 'David', 'Wilson', 'david.wilson@acme.com', 'OPS', 'JR', 'full_time'),
            ('EMP006', 'Lisa', 'Anderson', 'lisa.anderson@acme.com', 'IT', 'SR', 'full_time'),
            ('EMP007', 'James', 'Taylor', 'james.taylor@acme.com', 'FIN', 'MGR', 'full_time'),
            ('EMP008', 'Maria', 'Garcia', 'maria.garcia@acme.com', 'HR', 'SPEC', 'full_time'),
            ('EMP009', 'Alex', 'Kim', 'alex.kim@acme.com', 'IT', 'INT', 'intern'),
            ('EMP010', 'Priya', 'Patel', 'priya.patel@acme.com', 'MKT', 'INT', 'intern'),
            ('EMP011', 'Tom', 'Lee', 'tom.lee@acme.com', 'OPS', 'JR', 'full_time'),
            ('EMP012', 'Anna', 'White', 'anna.white@acme.com', 'IT', 'SPEC', 'full_time'),
        ]
        employees = []
        for eid, fname, lname, email, dept, desig, etype in employee_defs:
            emp, _ = Employee.objects.update_or_create(
                company=company, employee_id=eid,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'email': email,
                    'branch': branch,
                    'department': dept_map[dept],
                    'designation': desig_map[desig],
                    'date_joined': date(2024, 1, 15) + timedelta(days=len(employees) * 30),
                    'employment_status': 'active',
                    'employment_type': etype,
                },
            )
            employees.append(emp)

        year = timezone.now().year
        for emp in employees:
            for code in ['ANNUAL', 'SICK']:
                lt = lt_map[code]
                LeaveBalance.objects.update_or_create(
                    company=company, employee=emp, leave_type=lt, year=year,
                    defaults={'entitled': lt.days_per_year, 'used': Decimal('2'), 'pending': Decimal('1')},
                )

        today = timezone.localdate()

        # Leave requests
        lr1, _ = LeaveRequest.objects.update_or_create(
            company=company, employee=employees[0],
            start_date=today - timedelta(days=14), end_date=today - timedelta(days=10),
            defaults={
                'leave_type': lt_map['ANNUAL'],
                'days_requested': Decimal('5'),
                'reason': 'Family vacation',
                'status': 'completed',
                'completion_comment': 'Returned on schedule, handover complete.',
                'completed_at': timezone.now() - timedelta(days=9),
                'actual_return_date': today - timedelta(days=9),
                'approved_by': hr_user,
                'approved_at': timezone.now() - timedelta(days=20),
            },
        )
        sync_leave_to_attendance(lr1)

        lr2, _ = LeaveRequest.objects.update_or_create(
            company=company, employee=employees[2],
            start_date=today + timedelta(days=3), end_date=today + timedelta(days=5),
            defaults={
                'leave_type': lt_map['SICK'],
                'days_requested': Decimal('3'),
                'reason': 'Medical appointment',
                'status': 'pending',
            },
        )

        lr3, _ = LeaveRequest.objects.update_or_create(
            company=company, employee=employees[4],
            start_date=today - timedelta(days=2), end_date=today + timedelta(days=2),
            defaults={
                'leave_type': lt_map['ANNUAL'],
                'days_requested': Decimal('5'),
                'reason': 'Personal travel',
                'status': 'approved',
                'approved_by': hr_user,
                'approved_at': timezone.now() - timedelta(days=5),
            },
        )
        sync_leave_to_attendance(lr3)

        LeaveDayException.objects.get_or_create(
            company=company, leave_request=lr3, date=today,
            defaults={'pay_policy': 'no_pay', 'pay_percentage': 0, 'notes': 'Unpaid day exception'},
        )

        # Attendance — last 5 working days + today
        for emp in employees[:8]:
            for day_offset in range(5, -1, -1):
                d = today - timedelta(days=day_offset)
                if d.weekday() >= 5:
                    continue
                on_leave = LeaveRequest.objects.filter(
                    employee=emp, status__in=['approved', 'completed'],
                    start_date__lte=d, end_date__gte=d,
                ).exists()
                if on_leave:
                    AttendanceRecord.objects.update_or_create(
                        company=company, employee=emp, date=d,
                        defaults={
                            'shift': shift,
                            'status': 'on_leave',
                            'is_on_approved_leave': True,
                            'excluded_from_attendance': True,
                            'notes': 'On approved leave',
                        },
                    )
                    continue

                is_late = emp == employees[1] and day_offset == 1
                check_in = timezone.make_aware(
                    datetime.combine(d, datetime.min.time().replace(hour=9, minute=22 if is_late else 5))
                )
                rec, _ = AttendanceRecord.objects.update_or_create(
                    company=company, employee=emp, date=d,
                    defaults={
                        'shift': shift,
                        'status': 'late' if is_late else 'present',
                        'check_in': check_in,
                        'check_in_method': 'geolocation' if day_offset % 2 == 0 else 'manual',
                        'check_in_latitude': Decimal('40.712800'),
                        'check_in_longitude': Decimal('-74.006000'),
                        'hours_worked': Decimal('7.5'),
                        'late_minutes': 22 if is_late else 0,
                    },
                )
                if is_late:
                    AttendanceException.objects.get_or_create(
                        company=company, attendance_record=rec,
                        exception_type='late',
                        defaults={
                            'minutes_affected': 22,
                            'reason': 'Traffic delay',
                            'status': 'pending',
                        },
                    )

        # Recruitment
        job, _ = JobPosting.objects.get_or_create(
            company=company, title='Senior Python Developer',
            defaults={
                'department': dept_map['IT'],
                'designation': desig_map['SR'],
                'description': 'Build HRMS and payroll systems.',
                'status': 'open',
                'openings': 2,
                'closing_date': today + timedelta(days=30),
            },
        )
        for fname, lname, status in [
            ('Chris', 'Evans', 'new'),
            ('Nina', 'Ross', 'interview'),
            ('Omar', 'Hassan', 'screening'),
        ]:
            Applicant.objects.get_or_create(
                company=company, email=f'{fname.lower()}.{lname.lower()}@email.com',
                defaults={
                    'job': job,
                    'first_name': fname,
                    'last_name': lname,
                    'status': status,
                    'source': 'linkedin',
                },
            )

        PayrollRun.objects.get_or_create(
            company=company, name=f'Payroll {today.strftime("%B %Y")}',
            defaults={
                'period_start': today.replace(day=1),
                'period_end': today,
                'payment_date': today + timedelta(days=5),
                'status': 'draft',
            },
        )

        Announcement.objects.get_or_create(
            company=company, title='Q3 All-Hands Meeting',
            defaults={
                'content': 'Join us Friday at 3 PM for quarterly updates and team recognition.',
                'publish_date': timezone.now() - timedelta(days=2),
                'is_active': True,
            },
        )

        for i, emp in enumerate(employees[:3]):
            Notification.objects.get_or_create(
                recipient=admin_user,
                title=f'Leave request from {emp.full_name}',
                defaults={
                    'message': f'Review pending leave request #{i + 1}.',
                    'channel': 'in_app',
                    'is_read': i > 0,
                },
            )

        # Performance cycle & tasks
        cycle, _ = PerformanceCycle.objects.get_or_create(
            company=company, name=f'Q{(today.month - 1) // 3 + 1} {year}',
            defaults={
                'start_date': today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1),
                'end_date': today + timedelta(days=60),
                'review_deadline': today + timedelta(days=75),
                'status': 'active',
            },
        )

        task1, _ = WorkTask.objects.update_or_create(
            company=company, title='Launch employee self-service portal',
            assigned_to=employees[0],
            defaults={
                'description': 'Deliver ESS module with leave and payslip access.',
                'assigned_by': hr_user,
                'due_date': today + timedelta(days=14),
                'start_date': today - timedelta(days=7),
                'status': 'in_progress',
                'priority': 'high',
                'max_points': 100,
                'weight': 100,
            },
        )
        for title, weight, done in [
            ('Design UI mockups', 30, True),
            ('Implement leave API', 40, False),
            ('Write user documentation', 30, False),
        ]:
            st, created = WorkSubTask.objects.get_or_create(
                company=company, task=task1, title=title,
                defaults={'weight': weight, 'due_date': today + timedelta(days=10)},
            )
            if done and created:
                complete_subtask(st)

        task2, _ = WorkTask.objects.update_or_create(
            company=company, title='Complete payroll audit',
            assigned_to=employees[2],
            defaults={
                'assigned_by': hr_user,
                'due_date': today - timedelta(days=3),
                'start_date': today - timedelta(days=20),
                'status': 'completed',
                'completed_at': timezone.now() - timedelta(days=5),
                'max_points': 80,
                'earned_points': Decimal('88.00'),
            },
        )
        WorkSubTask.objects.get_or_create(
            company=company, task=task2, title='Reconcile tax deductions',
            defaults={'weight': 100, 'status': 'completed', 'completed_at': timezone.now() - timedelta(days=5)},
        )

        task3, _ = WorkTask.objects.update_or_create(
            company=company, title='Onboard intern cohort',
            assigned_to=employees[1],
            defaults={
                'assigned_by': hr_user,
                'due_date': today + timedelta(days=7),
                'status': 'pending',
                'max_points': 60,
            },
        )

        for emp in employees[:5]:
            refresh_monthly_performance(emp, year, today.month)

        Holiday.objects.get_or_create(
            company=company, name='Independence Day', date=date(year, 7, 4),
            defaults={'is_recurring': True, 'country': 'US'},
        )

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed complete! {len(employees)} employees, leave, attendance, tasks, and more.\n'
            f'  Login: admin@acme.com / Admin@123456'
        ))
