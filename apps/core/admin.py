from django.contrib import admin

from apps.core.models import Branch, Company, Department, Designation, Holiday, SystemSetting


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'country', 'default_currency', 'is_active']
    search_fields = ['name', 'slug', 'email']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'city', 'is_headquarters', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'branch', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'company', 'level', 'is_active']
    list_filter = ['company', 'level']
    search_fields = ['title', 'code']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'company', 'is_recurring']
    list_filter = ['company', 'date']


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'company', 'description']
    list_filter = ['company']
