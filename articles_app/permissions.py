from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.author.user or request.user.is_superuser


class IsAuthorInRedactionOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        is_authenticated = not isinstance(request.user, AnonymousUser)
        return is_authenticated and (request.user.is_redaction or request.user.is_superuser)
