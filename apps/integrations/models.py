import uuid

from django.db import models

from apps.core.models.base import CompanyScopedModel, TimeStampedModel


class IntegrationProvider(CompanyScopedModel):
    class ProviderType(models.TextChoices):
        ERP = 'erp', 'ERP System'
        ACCOUNTING = 'accounting', 'Accounting'
        PAYMENT = 'payment', 'Payment Gateway'
        SMS = 'sms', 'SMS Gateway'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        EMAIL = 'email', 'Email Service'
        LDAP = 'ldap', 'LDAP/AD'
        BANK = 'bank', 'Bank'
        API = 'api', 'Custom API'

    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices)
    provider_code = models.CharField(max_length=50)
    config = models.JSONField(default=dict)
    credentials = models.JSONField(default=dict)
    is_active = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['company', 'provider_code']

    def __str__(self):
        return f'{self.name} ({self.provider_type})'


class IntegrationLog(TimeStampedModel):
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failed', 'Failed')])
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.provider.name} - {self.action} ({self.status})'


class WebhookEndpoint(CompanyScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    url = models.URLField()
    secret = models.CharField(max_length=100)
    events = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
