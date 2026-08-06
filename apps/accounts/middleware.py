from django.utils import timezone
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

from apps.accounts.models import AuditLog, UserSession

SESSION_ACTIVITY_INTERVAL = 60  # seconds between DB writes


class AuditLogMiddleware(MiddlewareMixin):
    """Log authenticated API requests only."""

    AUDIT_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def process_response(self, request, response):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response

        if request.method in self.AUDIT_METHODS and request.path.startswith('/api/'):
            action_map = {
                'POST': AuditLog.ActionType.CREATE,
                'PUT': AuditLog.ActionType.UPDATE,
                'PATCH': AuditLog.ActionType.UPDATE,
                'DELETE': AuditLog.ActionType.DELETE,
            }
            AuditLog.objects.create(
                user=request.user,
                action=action_map.get(request.method, AuditLog.ActionType.UPDATE),
                model_name=request.path,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                company=getattr(request.user, 'company', None),
            )
        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class SessionActivityMiddleware(MiddlewareMixin):
    """Track session activity — throttled to one DB write per minute."""

    def process_request(self, request):
        if not (hasattr(request, 'user') and request.user.is_authenticated):
            return

        session_key = request.session.session_key
        if not session_key:
            return

        cache_key = f'session_activity:{session_key}'
        if cache.get(cache_key):
            return

        UserSession.objects.filter(
            session_key=session_key, user=request.user
        ).update(last_activity=timezone.now())
        cache.set(cache_key, True, SESSION_ACTIVITY_INTERVAL)
