from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payroll.views import (
    AllowanceViewSet,
    DeductionViewSet,
    EmployeeSalaryViewSet,
    LoanViewSet,
    PayrollRunViewSet,
    PayslipViewSet,
    SalaryStructureViewSet,
)

router = DefaultRouter()
router.register('salary-structures', SalaryStructureViewSet, basename='salary-structure')
router.register('allowances', AllowanceViewSet, basename='allowance')
router.register('deductions', DeductionViewSet, basename='deduction')
router.register('employee-salaries', EmployeeSalaryViewSet, basename='employee-salary')
router.register('runs', PayrollRunViewSet, basename='payroll-run')
router.register('payslips', PayslipViewSet, basename='payslip')
router.register('loans', LoanViewSet, basename='loan')

urlpatterns = [path('', include(router.urls))]
