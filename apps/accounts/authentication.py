from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.models import APIToken


class APITokenAuthentication(BaseAuthentication):
    """Authenticate requests using API tokens."""

    keyword = 'Token'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith(f'{self.keyword} '):
            return None

        key = auth_header[len(self.keyword) + 1:]
        try:
            token = APIToken.objects.select_related('user').get(key=key, is_active=True)
        except APIToken.DoesNotExist:
            raise AuthenticationFailed('Invalid API token.')

        if token.is_expired:
            raise AuthenticationFailed('API token has expired.')

        from django.utils import timezone
        token.last_used_at = timezone.now()
        token.save(update_fields=['last_used_at'])

        return (token.user, token)
