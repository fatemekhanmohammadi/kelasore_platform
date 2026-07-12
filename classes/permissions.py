from rest_framework import permissions

class Isteacher(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user