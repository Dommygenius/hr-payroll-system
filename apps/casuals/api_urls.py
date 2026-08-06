from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.casuals.views import CasualAttendanceViewSet, CasualPaymentViewSet, CasualWorkerViewSet

router = DefaultRouter()
router.register('workers', CasualWorkerViewSet, basename='casual-worker')
router.register('attendance', CasualAttendanceViewSet, basename='casual-attendance')
router.register('payments', CasualPaymentViewSet, basename='casual-payment')

urlpatterns = [path('', include(router.urls))]
