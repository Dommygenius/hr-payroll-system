from rest_framework import permissions


class IsCompanyMember(permissions.BasePermission):
    """User must belong to the same company as the object."""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        user_company = getattr(request.user, 'company_id', None)
        obj_company = getattr(obj, 'company_id', None)
        if obj_company is None and hasattr(obj, 'employee'):
            obj_company = getattr(obj.employee, 'company_id', None)
        return user_company == obj_company
