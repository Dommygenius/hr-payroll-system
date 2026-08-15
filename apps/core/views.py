from rest_framework.permissions import IsAuthenticated

from apps.core.models import Branch, Company, Department, Designation, Holiday
from apps.core.permissions import IsCompanyMember
from apps.core.serializers import (
    BranchSerializer,
    CompanySerializer,
    DepartmentSerializer,
    DesignationSerializer,
    HolidaySerializer,
)
from apps.core.viewsets import CompanyScopedModelViewSet, CompanyScopedReadOnlyModelViewSet


class CompanyViewSet(CompanyScopedReadOnlyModelViewSet):
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'slug', 'email']
    filterset_fields = ['country', 'is_active']

    def get_queryset(self):
        user = self.request.user
        qs = Company.objects.filter(is_active=True)
        company_id = getattr(user, 'company_id', None)
        if company_id is None:
            if user.is_superuser:
                return qs
            return qs.none()
        return qs.filter(pk=company_id)


class BranchViewSet(CompanyScopedModelViewSet):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'country', 'is_active']


class DepartmentViewSet(CompanyScopedModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'code']
    filterset_fields = ['company', 'branch', 'is_active']


class DesignationViewSet(CompanyScopedModelViewSet):
    queryset = Designation.objects.filter(is_active=True)
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['title', 'code']
    filterset_fields = ['company', 'level', 'is_active']


class HolidayViewSet(CompanyScopedModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'branch', 'country', 'date']
