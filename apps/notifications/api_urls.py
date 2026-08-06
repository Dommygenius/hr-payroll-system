from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.notifications.views import AnnouncementViewSet, NotificationViewSet

router = DefaultRouter()
router.register('', NotificationViewSet, basename='notification')
router.register('announcements', AnnouncementViewSet, basename='announcement')

urlpatterns = [path('', include(router.urls))]
