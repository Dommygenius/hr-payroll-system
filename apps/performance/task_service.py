"""Task performance scoring for bonus calculation."""
from decimal import Decimal

from django.db.models import F, Q
from django.utils import timezone

from apps.performance.models import MonthlyTaskPerformance, WorkSubTask, WorkTask


def calculate_task_points(task):
    """
    Earlier completion within timeline = higher points.
    Base points scaled by completion rate (sub-tasks) and timeliness bonus.
    """
    if task.status != WorkTask.Status.COMPLETED:
        return Decimal('0')

    base = Decimal(task.max_points)
    rate = Decimal(task.completion_rate) / Decimal('100')
    points = base * rate

    if task.is_on_time:
        days_early = (task.due_date - task.completed_at.date()).days
        bonus_pct = min(Decimal('20'), Decimal(max(days_early, 0)) * Decimal('2'))
        points += base * bonus_pct / Decimal('100')
    else:
        days_late = (task.completed_at.date() - task.due_date).days
        penalty = min(Decimal('30'), Decimal(days_late) * Decimal('5'))
        points -= base * penalty / Decimal('100')

    return max(Decimal('0'), points.quantize(Decimal('0.01')))


def complete_subtask(subtask):
    subtask.status = WorkSubTask.Status.COMPLETED
    subtask.completed_at = timezone.now()
    subtask.save()

    task = subtask.task
    if task.completion_rate >= 100:
        task.status = WorkTask.Status.COMPLETED
        task.completed_at = timezone.now()
        task.earned_points = calculate_task_points(task)
        task.save()
    else:
        task.status = WorkTask.Status.IN_PROGRESS
        task.save()
    return subtask


def complete_task(task):
    task.status = WorkTask.Status.COMPLETED
    task.completed_at = timezone.now()
    task.earned_points = calculate_task_points(task)
    task.save()

    task.subtasks.filter(status__in=[WorkSubTask.Status.PENDING, WorkSubTask.Status.IN_PROGRESS]).update(
        status=WorkSubTask.Status.COMPLETED,
        completed_at=timezone.now(),
    )
    return task


def refresh_monthly_performance(employee, year=None, month=None):
    """Plot monthly performance from task completion vs timeline."""
    now = timezone.localdate()
    year = year or now.year
    month = month or now.month

    qs = WorkTask.objects.filter(
        company=employee.company,
        assigned_to=employee,
        due_date__year=year,
        due_date__month=month,
    )
    assigned = qs.count()
    completed_qs = qs.filter(status=WorkTask.Status.COMPLETED)
    completed = completed_qs.count()
    on_time = completed_qs.filter(completed_at__date__lte=F('due_date')).count()

    total_points = sum(
        (t.earned_points for t in completed_qs),
        Decimal('0'),
    )

    timeliness_rate = (on_time / completed * 100) if completed else 0
    completion_rate = (completed / assigned * 100) if assigned else 0
    performance_score = Decimal(completion_rate * 0.6 + timeliness_rate * 0.4).quantize(Decimal('0.01'))

    snapshot, _ = MonthlyTaskPerformance.objects.update_or_create(
        company=employee.company,
        employee=employee,
        year=year,
        month=month,
        defaults={
            'tasks_assigned': assigned,
            'tasks_completed': completed,
            'tasks_on_time': on_time,
            'total_points': total_points,
            'performance_score': performance_score,
            'bonus_eligible': performance_score >= 75 and completed >= 1,
        },
    )
    return snapshot
