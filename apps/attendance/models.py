import uuid



from django.conf import settings

from django.db import models



from apps.core.models.base import CompanyScopedModel





class Shift(CompanyScopedModel):

    name = models.CharField(max_length=100)

    code = models.CharField(max_length=20)

    start_time = models.TimeField()

    end_time = models.TimeField()

    break_duration_minutes = models.PositiveSmallIntegerField(default=60)

    grace_period_minutes = models.PositiveSmallIntegerField(default=15)

    is_night_shift = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)



    class Meta:

        unique_together = ['company', 'code']



    def __str__(self):

        return f'{self.name} ({self.start_time} - {self.end_time})'





class AttendanceRecord(CompanyScopedModel):

    class Status(models.TextChoices):

        PRESENT = 'present', 'Present'

        ABSENT = 'absent', 'Absent'

        LATE = 'late', 'Late'

        HALF_DAY = 'half_day', 'Half Day'

        ON_LEAVE = 'on_leave', 'On Leave'

        HOLIDAY = 'holiday', 'Holiday'

        REMOTE = 'remote', 'Remote'



    class CheckMethod(models.TextChoices):

        MANUAL = 'manual', 'Manual'

        BIOMETRIC = 'biometric', 'Biometric'

        QR = 'qr', 'QR Code'

        GEO = 'geolocation', 'GPS / Geolocation'

        FACE = 'face_recognition', 'Face Recognition'



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='attendance_records')

    date = models.DateField(db_index=True)

    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)

    check_in = models.DateTimeField(null=True, blank=True)

    check_out = models.DateTimeField(null=True, blank=True)

    check_in_method = models.CharField(max_length=20, choices=CheckMethod.choices, default=CheckMethod.MANUAL)

    check_out_method = models.CharField(max_length=20, choices=CheckMethod.choices, blank=True)

    check_in_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    check_in_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    check_out_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    check_out_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    late_minutes = models.PositiveSmallIntegerField(default=0)

    is_anomaly = models.BooleanField(default=False)

    is_on_approved_leave = models.BooleanField(

        default=False, help_text='Auto-set when employee is on approved leave this day',

    )

    excluded_from_attendance = models.BooleanField(

        default=False, help_text='Exclude from attendance stats (leave/holiday)',

    )

    notes = models.TextField(blank=True)



    class Meta:

        unique_together = ['employee', 'date']

        ordering = ['-date']



    def __str__(self):

        return f'{self.employee} - {self.date} ({self.status})'





class AttendanceException(CompanyScopedModel):

    """Late arrival or other attendance exceptions requiring HR review."""



    class ExceptionType(models.TextChoices):

        LATE = 'late', 'Late Arrival'

        EARLY_DEPARTURE = 'early_departure', 'Early Departure'

        MISSING_CHECKOUT = 'missing_checkout', 'Missing Check-out'

        GPS_MISMATCH = 'gps_mismatch', 'GPS Location Mismatch'

        OTHER = 'other', 'Other'



    class Status(models.TextChoices):

        PENDING = 'pending', 'Pending'

        APPROVED = 'approved', 'Approved'

        REJECTED = 'rejected', 'Rejected'



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    attendance_record = models.ForeignKey(

        AttendanceRecord, on_delete=models.CASCADE, related_name='exceptions',

    )

    exception_type = models.CharField(max_length=20, choices=ExceptionType.choices, default=ExceptionType.LATE)

    reason = models.TextField(blank=True)

    minutes_affected = models.PositiveSmallIntegerField(default=0)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,

        related_name='approved_attendance_exceptions',

    )

    approved_at = models.DateTimeField(null=True, blank=True)

    hr_comment = models.TextField(blank=True)



    class Meta:

        ordering = ['-created_at']



    def __str__(self):

        return f'{self.exception_type} — {self.attendance_record}'





class AttendanceCapture(CompanyScopedModel):

    """Photo capture with GPS coordinates at check-in/out."""



    class CaptureType(models.TextChoices):

        CHECK_IN = 'check_in', 'Check In'

        CHECK_OUT = 'check_out', 'Check Out'

        FACE_VERIFY = 'face_verify', 'Face Verification'



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='attendance_captures')

    attendance_record = models.ForeignKey(

        AttendanceRecord, on_delete=models.CASCADE, null=True, blank=True, related_name='captures',

    )

    capture_type = models.CharField(max_length=20, choices=CaptureType.choices)

    photo = models.ImageField(upload_to='attendance/captures/%Y/%m/')

    latitude = models.DecimalField(max_digits=9, decimal_places=6)

    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    captured_at = models.DateTimeField(auto_now_add=True)

    method = models.CharField(

        max_length=20, choices=AttendanceRecord.CheckMethod.choices,

        default=AttendanceRecord.CheckMethod.MANUAL,

    )

    device = models.ForeignKey(

        'attendance.BiometricDevice', on_delete=models.SET_NULL, null=True, blank=True,

    )



    class Meta:

        ordering = ['-captured_at']



    def __str__(self):

        return f'{self.employee} — {self.capture_type} @ {self.latitude},{self.longitude}'





class Roster(CompanyScopedModel):

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='rosters')

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    date = models.DateField()

    is_off = models.BooleanField(default=False)

    notes = models.TextField(blank=True)



    class Meta:

        unique_together = ['employee', 'date']

        ordering = ['date']



    def __str__(self):

        return f'{self.employee} - {self.date} - {self.shift}'





class BiometricDevice(CompanyScopedModel):

    class DeviceType(models.TextChoices):

        FINGERPRINT = 'fingerprint', 'Fingerprint'

        FACE = 'face', 'Face Recognition'

        CARD = 'card', 'Card Reader'



    name = models.CharField(max_length=100)

    device_id = models.CharField(max_length=100, unique=True)

    device_type = models.CharField(max_length=20, choices=DeviceType.choices)

    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    last_sync = models.DateTimeField(null=True, blank=True)

    allow_manual_fallback = models.BooleanField(

        default=True, help_text='Allow manual check-in if biometric unavailable',

    )



    def __str__(self):

        return f'{self.name} ({self.device_type})'





class BranchAttendanceSettings(CompanyScopedModel):

    """Optional check-in methods enabled per branch (GPS, face, manual, biometric)."""



    branch = models.OneToOneField('core.Branch', on_delete=models.CASCADE, related_name='attendance_settings')

    allow_manual = models.BooleanField(default=True)

    allow_gps = models.BooleanField(default=True)

    allow_face = models.BooleanField(default=True)

    allow_biometric = models.BooleanField(default=True)

    require_photo = models.BooleanField(default=False)

    require_gps = models.BooleanField(default=False)

    geofence_radius_meters = models.PositiveIntegerField(default=200)



    def __str__(self):

        return f'Attendance settings — {self.branch}'

