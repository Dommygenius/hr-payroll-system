from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.leave.views import (
    LeaveApprovalViewSet,
    LeaveBalanceViewSet,
    LeaveRequestViewSet,
    LeaveTypeViewSet,
)

router = DefaultRouter()
router.register('types', LeaveTypeViewSet, basename='leave-type')
router.register('balances', LeaveBalanceViewSet, basename='leave-balance')
router.register('requests', LeaveRequestViewSet, basename='leave-request')
router.register('approvals', LeaveApprovalViewSet, basename='leave-approval')

urlpatterns = [path('', include(router.urls))]
