from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import MemberShip


#===================================================================================================

class IsTeacher(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner != request.user:
            raise PermissionDenied('❌ فقط صاحب کلاس می‌تواند این کار را انجام دهد')
        return True

#===================================================================================================
class IsClassroomTeacher(permissions.BasePermission):

    def has_permission(self, request, view):
        classroom_id = view.kwargs.get('pk')

        if not MemberShip.objects.filter(user=request.user,classroom_id=classroom_id,role='TEACHER').exists():
            raise PermissionDenied('فقط استاد کلاس می‌تواند این کار را انجام دهد')

        return True

