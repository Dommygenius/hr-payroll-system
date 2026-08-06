from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.core.views import (
    BranchViewSet,
    CompanyViewSet,
    DepartmentViewSet,
    DesignationViewSet,
    HolidayViewSet,
)

router = DefaultRouter()
router.register('companies', CompanyViewSet)
router.register('branches', BranchViewSet)
router.register('departments', DepartmentViewSet)
router.register('designations', DesignationViewSet)
router.register('holidays', HolidayViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
