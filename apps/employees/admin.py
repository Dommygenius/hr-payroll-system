from django.contrib import admin

from apps.employees.models import Employee, EmployeeContract, EmployeeDocument, EmployeeHistory


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'employment_status', 'date_joined']
    list_filter = ['company', 'employment_status', 'employment_type', 'department']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']


@admin.register(EmployeeContract)
class EmployeeContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'employee', 'start_date', 'end_date', 'is_active']


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'document_type', 'is_verified']


@admin.register(EmployeeHistory)
class EmployeeHistoryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'event_type', 'effective_date']
