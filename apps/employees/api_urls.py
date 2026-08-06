from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.employees.views import (
    EmployeeContractViewSet,
    EmployeeDocumentViewSet,
    EmployeeHistoryViewSet,
    EmployeeViewSet,
)

router = DefaultRouter()
router.register('', EmployeeViewSet, basename='employee')
router.register('contracts', EmployeeContractViewSet, basename='contract')
router.register('documents', EmployeeDocumentViewSet, basename='document')
router.register('history', EmployeeHistoryViewSet, basename='history')

urlpatterns = [path('', include(router.urls))]
