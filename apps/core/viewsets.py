"""Shared DRF mixins for tenant-safe querysets."""
from rest_framework import viewsets


class CompanyScopedMixin:
    """
    Force queryset filtering to the authenticated user's company.
    Fail closed: no company on the user → empty queryset (except platform
    superusers with no company assignment, who may see all for ops).
    """

    company_lookup = None  # override e.g. 'employee__company_id'

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return qs.none()

        company_id = getattr(user, 'company_id', None)
        if company_id is None:
            if user.is_superuser:
                return qs
            return qs.none()

        if self.company_lookup:
            return qs.filter(**{self.company_lookup: company_id})

        model = qs.model
        if hasattr(model, 'company_id'):
            return qs.filter(company_id=company_id)

        for path in (
            'employee__company_id',
            'leave_request__company_id',
            'survey__company_id',
            'job__company_id',
            'payroll_run__company_id',
            'attendance_record__company_id',
            'applicant__company_id',
            'cycle__company_id',
            'recipient__company_id',
            'worker__company_id',
        ):
            try:
                return qs.filter(**{path: company_id})
            except Exception:
                continue

        # User accounts table
        if model._meta.model_name == 'user' and hasattr(model, 'company_id'):
            return qs.filter(company_id=company_id)

        return qs.none()

    def perform_create(self, serializer):
        """Always stamp company from the authenticated user when the model is scoped."""
        extra = {}
        user = self.request.user
        company_id = getattr(user, 'company_id', None)
        model = getattr(getattr(serializer, 'Meta', None), 'model', None)
        if company_id and model is not None and hasattr(model, 'company_id'):
            # Prevent clients from writing into another tenant
            extra['company_id'] = company_id
        serializer.save(**extra)


class CompanyScopedModelViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    """Convenience base for company-scoped CRUD APIs."""

    pass


class CompanyScopedReadOnlyModelViewSet(CompanyScopedMixin, viewsets.ReadOnlyModelViewSet):
    """Convenience base for company-scoped read APIs."""

    pass
