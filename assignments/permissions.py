from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import MemberShip

#================================================================================================

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.role != 'TEACHER':
            raise PermissionDenied('❌ فقط استادها می‌توانند این کار را انجام دهند')
        
        return True

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

#================================================================================================


class IsClassroomMember(permissions.BasePermission):
    def has_permission(self, request, view):
        classroom_id = view.kwargs.get('pk')

        return MemberShip.objects.filter( user=request.user,classroom_id=classroom_id).exists()