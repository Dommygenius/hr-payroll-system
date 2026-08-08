"""SaaS tenant URL helpers and bootstrap."""
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


def get_portal_path(slug: str, path: str = '/') -> str:
    """Build tenant-scoped path, e.g. /t/acme-corp/dashboard/."""
    path = path if path.startswith('/') else f'/{path}'
    return f'/t/{slug}{path}'


def get_portal_url(slug: str, path: str = '/dashboard/', request=None) -> str:
    """Full absolute URL for a tenant portal."""
    relative = get_portal_path(slug, path)
    if request is not None:
        return request.build_absolute_uri(relative)
    base = getattr(settings, 'HRMS_PUBLIC_BASE_URL', '').rstrip('/')
    if base:
        return f'{base}{relative}'
    return relative


def reverse_tenant(viewname: str, tenant_slug: str, *args, **kwargs) -> str:
    """Reverse a named URL and prefix with tenant path."""
    url = reverse(viewname, args=args, kwargs=kwargs)
    return get_portal_path(tenant_slug, url)


def bootstrap_tenant(company_name: str, slug: str, admin_email: str, password: str,
                     first_name: str = '', last_name: str = ''):
    """
    Create a fully isolated tenant:
    Company + HQ branch + General department + Designation +
    admin User + Employee profile + default leave types + leave balances.
    """
    from django.contrib.auth import get_user_model
    from django.db import transaction

    from apps.accounts.models import UserRole
    from apps.core.models import Branch, Company, Department, Designation
    from apps.employees.models import Employee
    from apps.leave.models import LeaveBalance, LeaveType

    User = get_user_model()
    username = admin_email.split('@')[0]
    base_username = username
    n = 1
    while User.objects.filter(username=username).exists():
        username = f'{base_username}{n}'
        n += 1

    with transaction.atomic():
        company = Company.objects.create(
            name=company_name,
            slug=slug,
            email=admin_email,
            is_active=True,
        )
        branch = Branch.objects.create(
            company=company,
            name='Head Office',
            code='HQ',
            is_headquarters=True,
            is_active=True,
        )
        department = Department.objects.create(
            company=company,
            branch=branch,
            name='General',
            code='GEN',
            is_active=True,
        )
        designation = Designation.objects.create(
            company=company,
            title='HR Administrator',
            code='HR-ADMIN',
            is_active=True,
        )
        user = User.objects.create_user(
            username=username,
            email=admin_email,
            password=password,
            first_name=first_name or 'Admin',
            last_name=last_name or company_name.split()[0],
            company=company,
            branch=branch,
            role=UserRole.HR_ADMIN,
            is_staff=True,
        )
        employee = Employee.objects.create(
            company=company,
            user=user,
            employee_id='EMP001',
            first_name=user.first_name,
            last_name=user.last_name,
            email=admin_email,
            branch=branch,
            department=department,
            designation=designation,
            employment_type=Employee.EmploymentType.FULL_TIME,
            employment_status=Employee.EmploymentStatus.ACTIVE,
            date_joined=timezone.now().date(),
        )

        leave_defaults = [
            ('Annual Leave', 'ANNUAL', 21, True, LeaveType.PayPolicy.FULL_PAY, 100),
            ('Sick Leave', 'SICK', 10, True, LeaveType.PayPolicy.FULL_PAY, 100),
            ('Unpaid Leave', 'UNPAID', 0, False, LeaveType.PayPolicy.NO_PAY, 0),
        ]
        year = timezone.now().year
        for name, code, days, is_paid, policy, pct in leave_defaults:
            leave_type = LeaveType.objects.create(
                company=company,
                name=name,
                code=code,
                days_per_year=days,
                is_paid=is_paid,
                pay_policy=policy,
                pay_percentage=pct,
                is_active=True,
            )
            if days > 0:
                LeaveBalance.objects.create(
                    company=company,
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    entitled=days,
                    used=0,
                    pending=0,
                    carried_forward=0,
                )

    return company, user
