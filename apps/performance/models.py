import uuid

from decimal import Decimal



from django.conf import settings

from django.db import models

from django.utils import timezone



from apps.core.models.base import CompanyScopedModel





class PerformanceCycle(CompanyScopedModel):

    class Status(models.TextChoices):

        DRAFT = 'draft', 'Draft'

        ACTIVE = 'active', 'Active'

        REVIEW = 'review', 'Under Review'

        COMPLETED = 'completed', 'Completed'



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)

    start_date = models.DateField()

    end_date = models.DateField()

    review_deadline = models.DateField()

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    description = models.TextField(blank=True)



    class Meta:

        ordering = ['-start_date']



    def __str__(self):

        return self.name





class WorkTask(CompanyScopedModel):

    """Manager-assigned task with sub-tasks; completion timeline drives performance points."""



    class Status(models.TextChoices):

        PENDING = 'pending', 'Pending'

        IN_PROGRESS = 'in_progress', 'In Progress'

        COMPLETED = 'completed', 'Completed'

        CANCELLED = 'cancelled', 'Cancelled'



    class Priority(models.TextChoices):

        LOW = 'low', 'Low'

        NORMAL = 'normal', 'Normal'

        HIGH = 'high', 'High'

        URGENT = 'urgent', 'Urgent'



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    assigned_to = models.ForeignKey(

        'employees.Employee', on_delete=models.CASCADE, related_name='assigned_tasks',

    )

    assigned_by = models.ForeignKey(

        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,

        related_name='tasks_assigned',

    )

    start_date = models.DateField(null=True, blank=True)

    due_date = models.DateField()

    completed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)

    max_points = models.PositiveSmallIntegerField(default=100, help_text='Max performance points for this task')

    earned_points = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    weight = models.PositiveSmallIntegerField(default=100, help_text='Weight in monthly performance score')



    class Meta:

        ordering = ['due_date', '-created_at']



    def __str__(self):

        return f'{self.title} → {self.assigned_to}'



    @property

    def completion_rate(self):

        subs = self.subtasks.all()

        if not subs.exists():

            return 100 if self.status == self.Status.COMPLETED else 0

        total_weight = sum(s.weight for s in subs) or 100

        done_weight = sum(s.weight for s in subs if s.status == WorkSubTask.Status.COMPLETED)

        return int((done_weight / total_weight) * 100)



    @property

    def is_on_time(self):

        if not self.completed_at or not self.due_date:

            return False

        return self.completed_at.date() <= self.due_date



    @property

    def subtask_count(self):

        return self.subtasks.count()



    @property

    def subtasks_done(self):

        return self.subtasks.filter(status=WorkSubTask.Status.COMPLETED).count()





class WorkSubTask(CompanyScopedModel):

    class Status(models.TextChoices):

        PENDING = 'pending', 'Pending'

        IN_PROGRESS = 'in_progress', 'In Progress'

        COMPLETED = 'completed', 'Completed'

        CANCELLED = 'cancelled', 'Cancelled'



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    task = models.ForeignKey(WorkTask, on_delete=models.CASCADE, related_name='subtasks')

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    due_date = models.DateField(null=True, blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    weight = models.PositiveSmallIntegerField(

        default=25, help_text='Share of parent task completion (all subtasks should sum to ~100)',

    )



    class Meta:

        ordering = ['due_date', 'created_at']



    def __str__(self):

        return f'{self.task.title} / {self.title}'





class MonthlyTaskPerformance(CompanyScopedModel):

    """Monthly rollup for bonus / performance calculation from task completion."""



    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='monthly_task_scores')

    year = models.PositiveSmallIntegerField()

    month = models.PositiveSmallIntegerField()

    tasks_assigned = models.PositiveSmallIntegerField(default=0)

    tasks_completed = models.PositiveSmallIntegerField(default=0)

    tasks_on_time = models.PositiveSmallIntegerField(default=0)

    total_points = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    performance_score = models.DecimalField(

        max_digits=5, decimal_places=2, default=0,

        help_text='0–100 score based on completion rate and timeliness',

    )

    bonus_eligible = models.BooleanField(default=False)



    class Meta:

        unique_together = ['employee', 'year', 'month']

        ordering = ['-year', '-month']



    def __str__(self):

        return f'{self.employee} — {self.year}-{self.month:02d} ({self.performance_score}%)'





class Goal(CompanyScopedModel):

    class Status(models.TextChoices):

        NOT_STARTED = 'not_started', 'Not Started'

        IN_PROGRESS = 'in_progress', 'In Progress'

        COMPLETED = 'completed', 'Completed'

        CANCELLED = 'cancelled', 'Cancelled'



    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='goals')

    cycle = models.ForeignKey(PerformanceCycle, on_delete=models.CASCADE, related_name='goals')

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    target_value = models.CharField(max_length=100, blank=True)

    current_value = models.CharField(max_length=100, blank=True)

    weight = models.PositiveSmallIntegerField(default=100)

    due_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)

    progress = models.PositiveSmallIntegerField(default=0)



    class Meta:

        ordering = ['-created_at']



    def __str__(self):

        return f'{self.title} - {self.employee}'





class KPI(CompanyScopedModel):

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    measurement_unit = models.CharField(max_length=50, blank=True)

    target = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    department = models.ForeignKey('core.Department', on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)



    def __str__(self):

        return self.name





class PerformanceReview(CompanyScopedModel):

    class Status(models.TextChoices):

        PENDING = 'pending', 'Pending'

        SELF_REVIEW = 'self_review', 'Self Review'

        MANAGER_REVIEW = 'manager_review', 'Manager Review'

        COMPLETED = 'completed', 'Completed'



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='reviews')

    cycle = models.ForeignKey(PerformanceCycle, on_delete=models.CASCADE, related_name='reviews')

    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='conducted_reviews')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    overall_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    self_assessment = models.TextField(blank=True)

    manager_comments = models.TextField(blank=True)

    strengths = models.TextField(blank=True)

    areas_for_improvement = models.TextField(blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)



    class Meta:

        unique_together = ['employee', 'cycle']

        ordering = ['-created_at']



    def __str__(self):

        return f'Review: {self.employee} - {self.cycle}'





class Feedback360(CompanyScopedModel):

    review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, related_name='feedback_360')

    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    relationship = models.CharField(max_length=50)

    rating = models.PositiveSmallIntegerField()

    comments = models.TextField(blank=True)

    is_anonymous = models.BooleanField(default=True)



    def __str__(self):

        return f'360 Feedback: {self.review}'

