def dashboard_context(request):
    """Global template context — notification queries cached 30s per user."""
    from django.core.cache import cache

    context = {
        'app_name': 'HRMS Pro',
        'app_version': '1.0.0',
        'tenant': getattr(request, 'tenant', None),
        'tenant_slug': getattr(request, 'tenant_slug', None),
    }
    if request.user.is_authenticated:
        context['user_theme'] = getattr(request.user, 'theme', 'light')
        cache_key = f'notif_ctx:{request.user.pk}'
        cached = cache.get(cache_key)
        if cached is not None:
            context.update(cached)
        else:
            from apps.notifications.models import Notification
            notifications_qs = Notification.objects.filter(
                recipient=request.user, is_read=False
            ).order_by('-created_at')
            data = {
                'unread_notifications': notifications_qs.count(),
                'recent_notifications': list(notifications_qs[:5]),
            }
            cache.set(cache_key, data, 30)
            context.update(data)
    return context
