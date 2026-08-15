from rest_framework import serializers

from apps.core.models import Branch, Company, Department, Designation, Holiday


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'slug', 'is_active', 'enabled_roles',
        ]


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'company']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'company']


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'company']


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'company']
