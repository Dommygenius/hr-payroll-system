from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.attendance.views import (
    AttendanceRecordViewSet,
    BiometricDeviceViewSet,
    RosterViewSet,
    ShiftViewSet,
)

router = DefaultRouter()
router.register('shifts', ShiftViewSet, basename='shift')
router.register('records', AttendanceRecordViewSet, basename='attendance-record')
router.register('rosters', RosterViewSet, basename='roster')
router.register('devices', BiometricDeviceViewSet, basename='biometric-device')

urlpatterns = [path('', include(router.urls))]
