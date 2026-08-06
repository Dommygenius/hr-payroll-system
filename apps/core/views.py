from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.models import Branch, Company, Department, Designation, Holiday
from apps.core.serializers import (
    BranchSerializer,
    CompanySerializer,
    DepartmentSerializer,
    DesignationSerializer,
    HolidaySerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'slug', 'email']
    filterset_fields = ['country', 'is_active']


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'country', 'is_active']


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'branch', 'is_active']


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.filter(is_active=True)
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'code']
    filterset_fields = ['company', 'level', 'is_active']


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['company', 'branch', 'country', 'date']
