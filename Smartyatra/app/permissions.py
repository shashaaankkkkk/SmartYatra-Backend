from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'customer'

class IsOperator(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'operator'

class IsAuthority(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'authority'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'
