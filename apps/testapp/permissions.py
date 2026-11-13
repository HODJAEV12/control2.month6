from rest_framework.permissions import BasePermission
from .models import CustomUser

class IsTeacherOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        elif request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return request.user.is_authenticated and request.user.role == CustomUser.Role.TEACHER