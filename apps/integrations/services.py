"""Thin integration connectors (SMS / WhatsApp) using env or provider credentials."""
from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings
from django.utils import timezone

from apps.integrations.models import IntegrationLog, IntegrationProvider

logger = logging.getLogger(__name__)


def _log(provider: IntegrationProvider | None, action: str, status: str, detail: dict[str, Any]):
    if provider is None:
        return
    IntegrationLog.objects.create(
        provider=provider,
        action=action,
        status=status,
        request_data=detail.get('request') or {},
        response_data=detail.get('response') or {},
        error_message=(detail.get('message') or detail.get('error') or '')[:500],
    )


class SmsGateway:
    @staticmethod
    def send(to: str, body: str, company=None) -> dict:
        provider = None
        if company is not None:
            provider = IntegrationProvider.objects.filter(
                company=company, provider_type='sms', is_active=True
            ).first()

        url = settings.SMS_GATEWAY_URL
        api_key = settings.SMS_GATEWAY_API_KEY
        if provider and isinstance(provider.credentials, dict):
            url = provider.credentials.get('url') or url
            api_key = provider.credentials.get('api_key') or api_key

        if not url or not api_key:
            result = {'ok': False, 'error': 'SMS gateway not configured'}
            _log(provider, 'sms.send', 'failed', {'request': {'to': to}, 'response': result})
            return result

        try:
            resp = requests.post(
                url,
                json={'to': to, 'message': body},
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=15,
            )
            ok = 200 <= resp.status_code < 300
            result = {'ok': ok, 'status_code': resp.status_code, 'body': resp.text[:500]}
            _log(
                provider,
                'sms.send',
                'success' if ok else 'failed',
                {'request': {'to': to}, 'response': result},
            )
            if provider:
                provider.last_sync = timezone.now()
                provider.save(update_fields=['last_sync'])
            return result
        except Exception as exc:
            result = {'ok': False, 'error': str(exc)}
            _log(provider, 'sms.send', 'failed', {'request': {'to': to}, 'response': result})
            return result


class WhatsAppGateway:
    @staticmethod
    def send(to: str, body: str, company=None) -> dict:
        provider = None
        if company is not None:
            provider = IntegrationProvider.objects.filter(
                company=company, provider_type='whatsapp', is_active=True
            ).first()

        url = settings.WHATSAPP_API_URL
        token = settings.WHATSAPP_API_TOKEN
        if provider and isinstance(provider.credentials, dict):
            url = provider.credentials.get('url') or url
            token = provider.credentials.get('token') or token

        if not url or not token:
            result = {'ok': False, 'error': 'WhatsApp API not configured'}
            _log(provider, 'whatsapp.send', 'failed', {'request': {'to': to}, 'response': result})
            return result

        try:
            resp = requests.post(
                url,
                json={'to': to, 'text': body},
                headers={'Authorization': f'Bearer {token}'},
                timeout=15,
            )
            ok = 200 <= resp.status_code < 300
            result = {'ok': ok, 'status_code': resp.status_code, 'body': resp.text[:500]}
            _log(
                provider,
                'whatsapp.send',
                'success' if ok else 'failed',
                {'request': {'to': to}, 'response': result},
            )
            if provider:
                provider.last_sync = timezone.now()
                provider.save(update_fields=['last_sync'])
            return result
        except Exception as exc:
            result = {'ok': False, 'error': str(exc)}
            _log(provider, 'whatsapp.send', 'failed', {'request': {'to': to}, 'response': result})
            return result
