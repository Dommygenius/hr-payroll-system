import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.dashboard.helpers import (
    apply_search,
    cell_value,
    detail_fields_payload,
    get_request_company,
    get_user_company,
    scoped_queryset,
)
from apps.dashboard.module_config import MODULES, SPECIAL_MODULES, get_module, get_tab
from apps.core.http import tenant_redirect

MODULE_PAGE_SIZE = 50


@login_required
def index(request):
    """Main HR dashboard."""
    from django.core.cache import cache
    from django.db.models import Count, Q

    from apps.attendance.models import AttendanceRecord
    from apps.employees.models import Employee
    from apps.leave.models import LeaveRequest
    from apps.notifications.models import Announcement
    from apps.recruitment.models import Applicant, JobPosting
    from apps.payroll.models import PayrollRun

    today = timezone.now().date()
    company = get_request_company(request)
    if company is None and not request.user.is_superuser:
        messages.warning(request, 'No organization is linked to your account.')
        return render(request, 'dashboard/index.html', {
            'stats': {
                'total_employees': 0, 'active_employees': 0, 'on_leave_today': 0,
                'present_today': 0, 'open_positions': 0, 'pending_applicants': 0,
                'pending_leaves': 0, 'payroll_runs': 0,
            },
            'dept_breakdown_json': '[]',
            'dept_breakdown': [],
            'announcements': [],
            'recent_employees': [],
        })

    cache_key = f'dash_stats:{company.pk if company else "x"}:{today}'

    stats = cache.get(cache_key)
    if stats is None:
        employee_qs = Employee.objects.filter(is_deleted=False)
        if company:
            employee_qs = employee_qs.filter(company=company)
        else:
            employee_qs = employee_qs.none()

        emp_agg = employee_qs.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(employment_status='active')),
        )

        def _cnt(model, **filters):
            qs = model.objects.all()
            if company:
                qs = qs.filter(company=company)
            else:
                qs = qs.none()
            return qs.filter(**filters).count()

        stats = {
            'total_employees': emp_agg['total'],
            'active_employees': emp_agg['active'],
            'on_leave_today': _cnt(
                LeaveRequest, status='approved',
                start_date__lte=today, end_date__gte=today,
            ),
            'present_today': _cnt(
                AttendanceRecord, date=today, status='present',
                excluded_from_attendance=False,
            ),
            'open_positions': _cnt(JobPosting, status='open'),
            'pending_applicants': _cnt(Applicant, status='new'),
            'pending_leaves': _cnt(LeaveRequest, status='pending'),
            'payroll_runs': _cnt(PayrollRun, status__in=['draft', 'review']),
        }
        cache.set(cache_key, stats, 45)

    employee_qs = Employee.objects.filter(is_deleted=False)
    if company:
        employee_qs = employee_qs.filter(company=company)
    else:
        employee_qs = employee_qs.none()

    dept_breakdown = list(
        employee_qs.values('department__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    announcements = Announcement.objects.filter(is_active=True, publish_date__lte=timezone.now())
    if company:
        announcements = announcements.filter(company=company)
    else:
        announcements = announcements.none()
    announcements = announcements[:5]

    context = {
        'stats': stats,
        'dept_breakdown_json': json.dumps(dept_breakdown),
        'dept_breakdown': dept_breakdown,
        'announcements': announcements,
        'recent_employees': employee_qs.select_related('department', 'designation').order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def module_view(request, module, tab=None):
    """Module list view with tabs."""
    if module in SPECIAL_MODULES:
        if module == 'reports':
            return reports_view(request)
        if module == 'ai':
            return ai_view(request)

    mod = get_module(module)
    if not mod:
        raise Http404('Module not found')

    tab_key = tab or request.GET.get('tab')
    tab_cfg = get_tab(module, tab_key) if tab_key else get_tab(module, None)
    if not tab_cfg:
        raise Http404('Tab not found')

    # Special settings: role catalog (super admin enables/disables roles for tenant)
    if module == 'settings' and tab_cfg.get('key') == 'roles':
        return roles_catalog_view(request)

    from apps.accounts.permissions import can_manage_users
    from django.core.exceptions import PermissionDenied

    if module == 'settings' and tab_cfg.get('key') == 'users' and not can_manage_users(request.user):
        raise PermissionDenied('Only Super Admin / HR Admin can manage users and roles.')

    if tab_cfg.get('special'):
        raise Http404('Tab not found')

    search = request.GET.get('q', '').strip()
    qs = scoped_queryset(
        request.user,
        tab_cfg['model'],
        extra_filter=tab_cfg.get('filter'),
        select_related=tab_cfg.get('select_related'),
        company=get_request_company(request),
    )
    qs = apply_search(qs, search, tab_cfg.get('search_fields', []))

    detail_fields = tab_cfg.get('detail_fields') or []
    rows = []
    page_size = MODULE_PAGE_SIZE
    for obj in qs[:page_size]:
        row = {
            'id': str(obj.pk),
            'cells': [cell_value(obj, col[0]) for col in tab_cfg['columns']],
        }
        if detail_fields:
            row['title'] = cell_value(obj, 'full_name') or cell_value(obj, 'employee_id') or str(obj)
            row['subtitle'] = cell_value(obj, 'designation') if hasattr(obj, 'designation') else ''
            row['status'] = cell_value(obj, 'employment_status') if hasattr(obj, 'employment_status') else ''
            row['detail'] = detail_fields_payload(obj, detail_fields)
        rows.append(row)

    total_count = qs.count()

    stats = _module_stats(request.user, module, company=get_request_company(request))

    context = {
        'module': module,
        'mod': mod,
        'tab_cfg': tab_cfg,
        'active_tab': tab_cfg['key'],
        'tabs': mod['tabs'],
        'title': mod['title'],
        'rows': rows,
        'rows_json': json.dumps(rows, default=str),
        'columns': tab_cfg.get('columns', []),
        'detail_fields': detail_fields,
        'search': search,
        'stats': stats,
        'total_count': total_count,
        'page_size': page_size,
    }
    return render(request, 'modules/crud.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def roles_catalog_view(request):
    """Super Admin: enable or remove roles for this tenant's requirements."""
    from django.contrib import messages
    from django.core.exceptions import PermissionDenied

    from apps.accounts.models import UserRole
    from apps.accounts.permissions import can_configure_roles
    from apps.accounts.roles import REQUIRED_ROLES, get_enabled_roles, set_enabled_roles
    from apps.core.http import tenant_redirect

    if not can_configure_roles(request.user):
        raise PermissionDenied('Only a Super Admin can configure the tenant role catalog.')

    company = get_request_company(request)
    if company is None:
        raise Http404('No organization linked to this account.')

    mod = get_module('settings')
    enabled = set(get_enabled_roles(company))

    if request.method == 'POST':
        selected = request.POST.getlist('enabled_roles')
        set_enabled_roles(company, selected)
        messages.success(request, 'Tenant role catalog updated. Assign roles under Users & Roles.')
        return tenant_redirect(request, 'module-tab', module='settings', tab='roles')

    role_options = []
    for value, label in UserRole.choices:
        role_options.append({
            'value': value,
            'label': label,
            'enabled': value in enabled,
            'required': value in REQUIRED_ROLES,
        })

    return render(request, 'modules/roles.html', {
        'module': 'settings',
        'mod': mod,
        'tabs': mod['tabs'],
        'active_tab': 'roles',
        'title': mod['title'],
        'role_options': role_options,
        'company': company,
    })


def _module_stats(user, module, company=None):
    company = company or get_user_company(user)
    stats = []
    try:
        if module == 'employees':
            from apps.employees.models import Employee
            qs = Employee.objects.filter(is_deleted=False)
            if company:
                qs = qs.filter(company=company)
            stats = [
                {'label': 'Total', 'value': qs.count(), 'color': 'primary'},
                {'label': 'Active', 'value': qs.filter(employment_status='active').count(), 'color': 'success'},
                {'label': 'On Probation', 'value': qs.filter(employment_status='probation').count(), 'color': 'warning'},
            ]
        elif module == 'leave':
            from apps.leave.models import LeaveRequest
            qs = LeaveRequest.objects.all()
            if company:
                qs = qs.filter(company=company)
            stats = [
                {'label': 'Pending', 'value': qs.filter(status='pending').count(), 'color': 'warning'},
                {'label': 'Approved', 'value': qs.filter(status='approved').count(), 'color': 'success'},
                {'label': 'Rejected', 'value': qs.filter(status='rejected').count(), 'color': 'danger'},
            ]
        elif module == 'payroll':
            from apps.payroll.models import PayrollRun, Payslip
            run_qs = PayrollRun.objects.all()
            slip_qs = Payslip.objects.all()
            if company:
                run_qs = run_qs.filter(company=company)
                slip_qs = slip_qs.filter(company=company)
            stats = [
                {'label': 'Payroll Runs', 'value': run_qs.count(), 'color': 'primary'},
                {'label': 'Draft/Review', 'value': run_qs.filter(status__in=['draft', 'review']).count(), 'color': 'warning'},
                {'label': 'Payslips', 'value': slip_qs.count(), 'color': 'success'},
            ]
        elif module == 'recruitment':
            from apps.recruitment.models import JobPosting, Applicant
            jobs = JobPosting.objects.all()
            apps_qs = Applicant.objects.all()
            if company:
                jobs = jobs.filter(company=company)
                apps_qs = apps_qs.filter(company=company)
            stats = [
                {'label': 'Open Jobs', 'value': jobs.filter(status='open').count(), 'color': 'primary'},
                {'label': 'New Applicants', 'value': apps_qs.filter(status='new').count(), 'color': 'info'},
                {'label': 'In Interview', 'value': apps_qs.filter(status='interview').count(), 'color': 'warning'},
            ]
    except Exception:
        pass
    return stats


def _after_module_save(request, module, tab, instance):
    """Post-save hooks for leave sync, tasks, and user permissions."""
    from apps.accounts.permissions import can_manage_users, can_assign_tasks
    from apps.leave.models import LeaveRequest
    from apps.leave.services import complete_leave_request, sync_leave_to_attendance
    from apps.performance.models import WorkTask
    from apps.performance.task_service import refresh_monthly_performance

    if module == 'leave' and tab == 'requests':
        if instance.status == LeaveRequest.Status.APPROVED:
            sync_leave_to_attendance(instance)
        elif instance.status == LeaveRequest.Status.COMPLETED:
            if not instance.completed_at:
                complete_leave_request(
                    instance,
                    comment=instance.completion_comment,
                    actual_return_date=instance.actual_return_date,
                )
            else:
                sync_leave_to_attendance(instance)
    elif module == 'performance' and tab == 'tasks':
        if not instance.assigned_by_id:
            instance.assigned_by = request.user
            instance.save(update_fields=['assigned_by'])
        if instance.status == WorkTask.Status.COMPLETED and instance.assigned_to_id:
            refresh_monthly_performance(instance.assigned_to)
    elif module == 'settings' and tab == 'users':
        if not can_manage_users(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied('Only HR administrators can manage users.')


@login_required
@require_http_methods(['GET', 'POST'])
def clock_in_view(request):
    """Mobile-friendly check-in with optional GPS + photo."""
    from apps.accounts.permissions import can_manage_attendance
    from apps.attendance.services import clock_in, clock_out, get_branch_settings
    from apps.employees.models import Employee

    company = get_request_company(request)
    employees = Employee.objects.filter(company=company, is_deleted=False) if company else Employee.objects.none()
    employee = employees.filter(email=request.user.email).first()
    settings = get_branch_settings(employee) if employee else None
    can_select_employee = can_manage_attendance(request.user)

    if request.method == 'POST':
        emp_id = request.POST.get('employee')
        if can_select_employee and emp_id:
            employee = employees.filter(pk=emp_id).first()
        if not employee:
            messages.error(request, 'No employee profile linked to your account.')
            return tenant_redirect(request, 'clock-in')

        action = request.POST.get('action', 'check_in')
        method = request.POST.get('method', 'manual')
        lat = request.POST.get('latitude') or None
        lng = request.POST.get('longitude') or None
        photo = request.FILES.get('photo')

        if action == 'check_out':
            record, msg = clock_out(employee, method, lat, lng, photo)
        else:
            record, msg = clock_in(employee, method, lat, lng, photo, user=request.user)

        if record:
            messages.success(request, msg)
        else:
            messages.warning(request, msg)
        return tenant_redirect(request, 'clock-in')

    return render(request, 'modules/clock_in.html', {
        'employee': employee,
        'employees': employees if can_select_employee else [],
        'can_select_employee': can_select_employee,
        'branch_settings': settings,
        'methods': [
            ('manual', 'Manual'),
            ('geolocation', 'GPS'),
            ('face_recognition', 'Face + Photo'),
            ('biometric', 'Biometric'),
        ],
    })


@login_required
@require_http_methods(['GET', 'POST'])
def module_create(request, module, tab):
    from django.core.exceptions import PermissionDenied

    from apps.accounts.permissions import can_manage_users
    from apps.dashboard.forms import UserAccountForm

    mod = get_module(module)
    tab_cfg = get_tab(module, tab)
    if not mod or not tab_cfg or tab_cfg.get('special'):
        raise Http404()

    if module == 'settings' and tab == 'users' and not can_manage_users(request.user):
        raise PermissionDenied('Only Super Admin / HR Admin can manage users.')

    company = get_request_company(request)
    form_class = tab_cfg['form']
    form_kwargs = {'company': company}
    if form_class is UserAccountForm:
        form_kwargs['request_user'] = request.user

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, **form_kwargs)
        if form.is_valid():
            instance = form.save()
            _after_module_save(request, module, tab, instance)
            messages.success(request, f'{tab_cfg["label"]} record created successfully.')
            return tenant_redirect(request, 'module-tab', module=module, tab=tab)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = form_class(**form_kwargs)

    return render(request, 'modules/form.html', {
        'module': module,
        'mod': mod,
        'tab_cfg': tab_cfg,
        'active_tab': tab,
        'tabs': mod['tabs'],
        'title': mod['title'],
        'form': form,
        'action': 'Create',
    })


def _leave_approval_context(module, tab, obj):
    """Build approval preview payload for leave request edit/approve."""
    if module != 'leave' or tab != 'requests':
        return None
    from apps.leave.models import LeaveRequest

    if not isinstance(obj, LeaveRequest):
        return None
    return {
        'employee': str(obj.employee),
        'leave_type': str(obj.leave_type),
        'days': obj.days_requested,
        'period': f'{obj.start_date} → {obj.end_date}',
        'status': obj.status,
        'reason': obj.reason or '',
    }


@login_required
@require_http_methods(['GET', 'POST'])
def module_edit(request, module, tab, pk):
    from django.core.exceptions import PermissionDenied

    from apps.accounts.permissions import can_manage_users
    from apps.dashboard.forms import UserAccountForm

    mod = get_module(module)
    tab_cfg = get_tab(module, tab)
    if not mod or not tab_cfg or tab_cfg.get('special'):
        raise Http404()

    if module == 'settings' and tab == 'users' and not can_manage_users(request.user):
        raise PermissionDenied('Only Super Admin / HR Admin can manage users.')

    company = get_request_company(request)
    qs = scoped_queryset(request.user, tab_cfg['model'], company=company)
    obj = get_object_or_404(qs, pk=pk)
    form_class = tab_cfg['form']
    form_kwargs = {'company': company, 'instance': obj}
    if form_class is UserAccountForm:
        form_kwargs['request_user'] = request.user

    if request.method == 'POST':
        post_data = request.POST.copy()
        approve_action = post_data.get('approve_action')
        if module == 'leave' and tab == 'requests' and approve_action in ('approve', 'reject'):
            from apps.leave.models import LeaveRequest

            post_data['status'] = (
                LeaveRequest.Status.APPROVED if approve_action == 'approve' else LeaveRequest.Status.REJECTED
            )
        form = form_class(post_data, request.FILES, **form_kwargs)
        if form.is_valid():
            instance = form.save()
            _after_module_save(request, module, tab, instance)
            if approve_action == 'approve':
                messages.success(request, 'Leave request approved.')
            elif approve_action == 'reject':
                messages.success(request, 'Leave request rejected.')
            else:
                messages.success(request, 'Record updated successfully.')
            return tenant_redirect(request, 'module-tab', module=module, tab=tab)
    else:
        form = form_class(**form_kwargs)

    return render(request, 'modules/form.html', {
        'module': module,
        'mod': mod,
        'tab_cfg': tab_cfg,
        'active_tab': tab,
        'tabs': mod['tabs'],
        'title': mod['title'],
        'form': form,
        'action': 'Edit',
        'object': obj,
        'leave_approval': _leave_approval_context(module, tab, obj),
    })


@login_required
@require_http_methods(['POST'])
def module_delete(request, module, tab, pk):
    from django.core.exceptions import PermissionDenied

    from apps.accounts.permissions import can_manage_users

    mod = get_module(module)
    tab_cfg = get_tab(module, tab)
    if not mod or not tab_cfg or tab_cfg.get('special'):
        raise Http404()

    if module == 'settings' and tab == 'users' and not can_manage_users(request.user):
        raise PermissionDenied('Only Super Admin / HR Admin can manage users.')

    qs = scoped_queryset(request.user, tab_cfg['model'], company=get_request_company(request))
    obj = get_object_or_404(qs, pk=pk)

    if tab_cfg.get('soft_delete') and hasattr(obj, 'soft_delete'):
        obj.soft_delete()
    else:
        obj.delete()

    messages.success(request, 'Record deleted successfully.')
    return tenant_redirect(request, 'module-tab', module=module, tab=tab)


@login_required
def reports_view(request):
    from apps.attendance.models import AttendanceRecord
    from apps.employees.models import Employee
    from apps.leave.models import LeaveRequest
    from apps.payroll.models import PayrollRun, Payslip
    from apps.recruitment.models import Applicant, JobPosting

    company = get_request_company(request)
    today = timezone.now().date()

    def _filter(qs):
        return qs.filter(company=company) if company else qs

    emp = _filter(Employee.objects.filter(is_deleted=False))
    context = {
        'module': 'reports',
        'title': 'Reports & Analytics',
        'stats': [
            {'label': 'Employees', 'value': emp.count()},
            {'label': 'Active', 'value': emp.filter(employment_status='active').count()},
            {'label': 'Leave Requests', 'value': _filter(LeaveRequest.objects.all()).count()},
            {'label': 'Payroll Runs', 'value': _filter(PayrollRun.objects.all()).count()},
            {'label': 'Payslips', 'value': _filter(Payslip.objects.all()).count()},
            {'label': 'Open Jobs', 'value': _filter(JobPosting.objects.filter(status='open')).count()},
            {'label': 'Applicants', 'value': _filter(Applicant.objects.all()).count()},
            {'label': 'Present Today', 'value': _filter(AttendanceRecord.objects.filter(date=today, status='present', excluded_from_attendance=False)).count()},
        ],
        'dept_data': list(emp.values('department__name').annotate(count=Count('id')).order_by('-count')[:8]),
        'leave_by_status': list(_filter(LeaveRequest.objects.all()).values('status').annotate(count=Count('id'))),
    }
    context['dept_data_json'] = json.dumps(context['dept_data'])
    context['leave_data_json'] = json.dumps(context['leave_by_status'])
    return render(request, 'modules/reports.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def ai_view(request):
    from apps.ai_features.models import AIAnalysisJob, ChatbotConversation, ChatbotMessage
    from apps.ai_features.services import HRChatbotService

    company = get_request_company(request)
    chat_response = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'chat':
            message = request.POST.get('message', '').strip()
            if message:
                conv, _ = ChatbotConversation.objects.get_or_create(user=request.user, is_active=True)
                prior = [
                    {'role': m.role, 'content': m.content}
                    for m in conv.messages.order_by('created_at')
                ]
                ChatbotMessage.objects.create(conversation=conv, role='user', content=message)
                result = HRChatbotService.respond(message, history=prior, user=request.user)
                reply = result['text']
                ChatbotMessage.objects.create(conversation=conv, role='assistant', content=reply)
                chat_response = reply

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'reply': reply,
                        'source': result.get('source', 'assistant'),
                        'model': result.get('model', ''),
                    })

        if action == 'clear_chat':
            ChatbotConversation.objects.filter(user=request.user).update(is_active=False)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True})
            return tenant_redirect(request, 'module-ai')

    jobs_qs = AIAnalysisJob.objects.all()
    if company:
        jobs_qs = jobs_qs.filter(company=company)

    conv = ChatbotConversation.objects.filter(user=request.user, is_active=True).first()
    chat_history = []
    if conv:
        chat_history = list(conv.messages.order_by('-created_at')[:20])[::-1]

    return render(request, 'modules/ai.html', {
        'module': 'ai',
        'title': 'AI Assistant',
        'chat_history': chat_history,
        'chat_response': chat_response,
        'ai_jobs': jobs_qs.order_by('-created_at')[:10],
    })
