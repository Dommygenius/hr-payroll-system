import uuid



from django.conf import settings

from django.db import models



from apps.core.models.base import CompanyScopedModel





class LeaveType(CompanyScopedModel):

    class PayPolicy(models.TextChoices):

        FULL_PAY = 'full_pay', 'Full Pay'

        NO_PAY = 'no_pay', 'No Pay (Unpaid Leave)'

        PARTIAL_PAY = 'partial_pay', 'Partial Pay'



    name = models.CharField(max_length=100)

    code = models.CharField(max_length=20)

    days_per_year = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    is_paid = models.BooleanField(default=True)

    pay_policy = models.CharField(

        max_length=20, choices=PayPolicy.choices, default=PayPolicy.FULL_PAY,

        help_text='Full pay, no pay, or partial pay for this leave type',

    )

    pay_percentage = models.DecimalField(

        max_digits=5, decimal_places=2, default=100,

        help_text='100 = full pay, 0 = no pay, 50 = half pay',

    )

    available_for_interns = models.BooleanField(

        default=False,

        help_text='If enabled, interns may use this leave type (optional)',

    )

    is_carry_forward = models.BooleanField(default=False)

    max_carry_forward = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    requires_approval = models.BooleanField(default=True)

    min_days_notice = models.PositiveSmallIntegerField(default=0)

    max_consecutive_days = models.PositiveSmallIntegerField(null=True, blank=True)

    color = models.CharField(max_length=7, default='#3788d8')

    is_active = models.BooleanField(default=True)



    class Meta:

        unique_together = ['company', 'code']



    def __str__(self):

        return self.name



    def save(self, *args, **kwargs):

        if self.pay_policy == self.PayPolicy.FULL_PAY:

            self.is_paid = True

            self.pay_percentage = 100

        elif self.pay_policy == self.PayPolicy.NO_PAY:

            self.is_paid = False

            self.pay_percentage = 0

        else:

            self.is_paid = self.pay_percentage > 0

        super().save(*args, **kwargs)



    @property

    def effective_pay_label(self):

        if self.pay_policy == self.PayPolicy.NO_PAY:

            return 'No pay'

        if self.pay_policy == self.PayPolicy.PARTIAL_PAY:

            return f'{self.pay_percentage}% pay'

        return 'Full pay'





class LeaveBalance(CompanyScopedModel):

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='leave_balances')

    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)

    year = models.PositiveSmallIntegerField()

    entitled = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    used = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    pending = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    carried_forward = models.DecimalField(max_digits=5, decimal_places=1, default=0)



    class Meta:

        unique_together = ['employee', 'leave_type', 'year']



    @property

    def available(self):

        return self.entitled + self.carried_forward - self.used - self.pending



    def __str__(self):

        return f'{self.employee} - {self.leave_type} ({self.year})'





class LeaveRequest(CompanyScopedModel):

    class Status(models.TextChoices):

        PENDING = 'pending', 'Pending'

        APPROVED = 'approved', 'Approved'

        REJECTED = 'rejected', 'Rejected'

        CANCELLED = 'cancelled', 'Cancelled'

        COMPLETED = 'completed', 'Completed'



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='leave_requests')

    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)

    start_date = models.DateField()

    end_date = models.DateField()

    days_requested = models.DecimalField(max_digits=5, decimal_places=1)

    reason = models.TextField()

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves'

    )

    approved_at = models.DateTimeField(null=True, blank=True)

    rejection_reason = models.TextField(blank=True)

    attachment = models.FileField(upload_to='leave/attachments/', blank=True, null=True)

    completion_comment = models.TextField(

        blank=True, help_text='Comment when marking leave as completed / returned to work',

    )

    completed_at = models.DateTimeField(null=True, blank=True)

    actual_return_date = models.DateField(

        null=True, blank=True, help_text='Actual day employee returned from leave',

    )



    class Meta:

        ordering = ['-created_at']



    def __str__(self):

        return f'{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})'





class LeaveDayException(CompanyScopedModel):

    """Per-day pay override within a leave request (e.g. one unpaid day in a paid leave)."""



    class PayPolicy(models.TextChoices):

        FULL_PAY = 'full_pay', 'Full Pay'

        NO_PAY = 'no_pay', 'No Pay'

        PARTIAL_PAY = 'partial_pay', 'Partial Pay'



    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='day_exceptions')

    date = models.DateField()

    pay_policy = models.CharField(max_length=20, choices=PayPolicy.choices, default=PayPolicy.FULL_PAY)

    pay_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100)

    notes = models.CharField(max_length=255, blank=True)



    class Meta:

        unique_together = ['leave_request', 'date']

        ordering = ['date']



    def __str__(self):

        return f'{self.leave_request} — {self.date} ({self.pay_policy})'





class LeaveApproval(CompanyScopedModel):

    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='approvals')

    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    level = models.PositiveSmallIntegerField(default=1)

    status = models.CharField(max_length=20, choices=LeaveRequest.Status.choices, default=LeaveRequest.Status.PENDING)

    comments = models.TextField(blank=True)

    acted_at = models.DateTimeField(null=True, blank=True)



    class Meta:

        ordering = ['level']

        unique_together = ['leave_request', 'level']



    def __str__(self):

        return f'Approval L{self.level}: {self.leave_request}'

