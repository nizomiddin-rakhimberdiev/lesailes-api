from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return True
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsCustomerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['CUSTOMER', 'ADMIN']


class IsAdminForOrder(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'ADMIN'
