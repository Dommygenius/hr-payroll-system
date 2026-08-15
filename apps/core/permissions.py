from rest_framework import permissions


class IsCompanyMember(permissions.BasePermission):
    """User must belong to the same company as the object."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return bool(getattr(user, 'company_id', None))

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser and not getattr(request.user, 'company_id', None):
            return True
        user_company = getattr(request.user, 'company_id', None)
        obj_company = getattr(obj, 'company_id', None)
        if obj_company is None and hasattr(obj, 'employee'):
            obj_company = getattr(obj.employee, 'company_id', None)
        if obj_company is None and hasattr(obj, 'company'):
            obj_company = getattr(obj.company, 'id', None)
        if obj.__class__.__name__ == 'Company':
            obj_company = obj.pk
        if obj_company is None and obj.__class__.__name__ == 'User':
            obj_company = getattr(obj, 'company_id', None)
        return user_company is not None and user_company == obj_company
