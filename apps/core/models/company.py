from django.conf import settings
from django.db import models

from apps.core.models.base import AuditableModel, TimeStampedModel


class Company(AuditableModel):
    """Multi-company tenant model."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    legal_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to='companies/logos/', blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, default='US')
    postal_code = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    default_currency = models.CharField(max_length=3, default='USD')
    default_language = models.CharField(max_length=10, default='en')
    fiscal_year_start_month = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_portal_path(self, path: str = '/dashboard/') -> str:
        from apps.core.tenant import get_portal_path
        return get_portal_path(self.slug, path)

    def get_portal_url(self, path: str = '/dashboard/', request=None) -> str:
        from apps.core.tenant import get_portal_url
        return get_portal_url(self.slug, path, request)


class Branch(AuditableModel):
    """Company branch/location."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, default='US')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_headquarters = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geofence_radius_meters = models.PositiveIntegerField(default=200, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'branches'
        unique_together = ['company', 'code']
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.company.name})'


class Department(AuditableModel):
    """Organizational department."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='departments'
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['company', 'code']
        ordering = ['name']

    def __str__(self):
        return self.name


class Designation(AuditableModel):
    """Job title/designation."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='designations')
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    level = models.PositiveSmallIntegerField(default=1)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['company', 'code']
        ordering = ['level', 'title']

    def __str__(self):
        return self.title


class Holiday(AuditableModel):
    """Public/company holidays."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='holidays')
    name = models.CharField(max_length=255)
    date = models.DateField()
    is_recurring = models.BooleanField(default=False)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, null=True, blank=True, related_name='holidays'
    )
    country = models.CharField(max_length=2, blank=True)

    class Meta:
        ordering = ['date']
        unique_together = ['company', 'name', 'date']

    def __str__(self):
        return f'{self.name} - {self.date}'


class SystemSetting(TimeStampedModel):
    """Key-value system settings per company."""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='settings', null=True, blank=True
    )
    key = models.CharField(max_length=100, db_index=True)
    value = models.JSONField(default=dict)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['company', 'key']

    def __str__(self):
        return f'{self.key} ({self.company or "global"})'
