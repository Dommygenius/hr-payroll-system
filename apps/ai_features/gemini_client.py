"""Google Gemini API client for HRMS AI features."""
import logging
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

GEMINI_API_BASE = 'https://generativelanguage.googleapis.com/v1beta'
GEMINI_GENERATE_URL = f'{GEMINI_API_BASE}/models/{{model}}:generateContent'

# Models verified to work with generateContent (fallback order).
DEFAULT_MODEL_PRIORITY = (
    'gemini-3.5-flash',
    'gemini-3.6-flash',
    'gemini-flash-latest',
    'gemini-flash-lite-latest',
    'gemini-3.1-flash-lite',
    'gemini-3.5-flash-lite',
    'gemini-3-flash-preview',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
)

WORKING_MODEL_CACHE_KEY = 'gemini:working_model'
WORKING_MODEL_CACHE_TTL = 3600


class GeminiClient:
    """Native Gemini REST client (supports AQ. auth keys via x-goog-api-key)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '')

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def generate(
        self,
        message: str,
        *,
        history: list | None = None,
        system_prompt: str = '',
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """
        Generate a response. Returns:
        {'ok': True, 'text': '...', 'model': '...'} or
        {'ok': False, 'error': '...', 'code': 429}
        """
        if not self.configured:
            return {'ok': False, 'error': 'GEMINI_API_KEY not configured', 'code': 0}

        contents = self._build_contents(message, history or [])
        payload = {
            'contents': contents,
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens,
            },
        }
        if system_prompt:
            payload['systemInstruction'] = {'parts': [{'text': system_prompt}]}

        models = self._model_candidates()
        cached = cache.get(WORKING_MODEL_CACHE_KEY)
        if cached and cached in models:
            models = (cached,) + tuple(m for m in models if m != cached)

        last_error = 'No models available'
        last_code = 0

        for model in models:
            result = self._call_model(model, payload)
            if result.get('ok'):
                cache.set(WORKING_MODEL_CACHE_KEY, model, WORKING_MODEL_CACHE_TTL)
                result['model'] = model
                return result
            last_error = result.get('error', last_error)
            last_code = result.get('code', last_code)
            if last_code in (400, 404, 503):
                continue
            if last_code == 429:
                continue

        return {'ok': False, 'error': last_error, 'code': last_code}

    def probe(self) -> bool:
        result = self.generate('Reply with exactly: OK', max_tokens=16)
        return result.get('ok', False)

    def list_models(self) -> list[str]:
        if not self.configured:
            return []
        try:
            response = requests.get(
                f'{GEMINI_API_BASE}/models',
                headers=self._headers(),
                timeout=15,
            )
            response.raise_for_status()
            names = []
            for item in response.json().get('models', []):
                methods = item.get('supportedGenerationMethods') or []
                if 'generateContent' in methods:
                    names.append(item['name'].replace('models/', ''))
            return names
        except requests.RequestException as exc:
            logger.warning('Gemini list models failed: %s', exc)
            return []

    def _call_model(self, model: str, payload: dict) -> dict[str, Any]:
        url = GEMINI_GENERATE_URL.format(model=model)
        try:
            response = requests.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=45,
            )
            if response.status_code == 200:
                text = self._extract_text(response.json())
                if text:
                    return {'ok': True, 'text': text}
                return {'ok': False, 'error': 'Empty response from Gemini', 'code': 200}

            error_msg = response.text[:300]
            try:
                error_msg = response.json().get('error', {}).get('message', error_msg)
            except ValueError:
                pass
            logger.warning('Gemini %s failed (%s): %s', model, response.status_code, error_msg)
            return {'ok': False, 'error': error_msg, 'code': response.status_code}
        except requests.RequestException as exc:
            logger.warning('Gemini request error (%s): %s', model, exc)
            return {'ok': False, 'error': str(exc), 'code': 0}

    def _headers(self) -> dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.api_key,
        }

    def _model_candidates(self) -> tuple[str, ...]:
        preferred = getattr(settings, 'GEMINI_MODEL', '')
        models: list[str] = []
        if preferred:
            models.append(preferred)
        for model in DEFAULT_MODEL_PRIORITY:
            if model not in models:
                models.append(model)
        return tuple(models)

    @staticmethod
    def _build_contents(message: str, history: list) -> list:
        contents = []
        for item in history[-12:]:
            role = item.get('role', 'user')
            if role == 'assistant':
                role = 'model'
            if role not in ('user', 'model'):
                continue
            text = (item.get('content') or '').strip()
            if not text:
                continue
            contents.append({'role': role, 'parts': [{'text': text}]})
        contents.append({'role': 'user', 'parts': [{'text': message}]})
        return contents

    @staticmethod
    def _extract_text(data: dict) -> str | None:
        candidates = data.get('candidates') or []
        if not candidates:
            return None
        parts = candidates[0].get('content', {}).get('parts') or []
        text = ''.join(part.get('text', '') for part in parts).strip()
        return text or None
