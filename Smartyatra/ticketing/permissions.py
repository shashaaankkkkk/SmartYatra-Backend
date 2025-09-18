from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    role_required = None

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == self.role_required)
        )

class IsAdmin(RolePermission):
    role_required = 'admin'

class IsPassenger(RolePermission):
    role_required = 'customer'

class IsConductor(RolePermission):
    role_required = 'operator'

class IsAuthority(RolePermission):
    role_required = 'authority'
