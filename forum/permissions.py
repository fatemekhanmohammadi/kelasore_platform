from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from classes.models import MemberShip




#=================================================================================================================


class IsClassroomMember(permissions.BasePermission):
    def has_permission(self, request, view):
        classroom_id = view.kwargs.get('pk')
        return MemberShip.objects.filter(user=request.user,classroom_id=classroom_id).exists()



#=================================================================================================================





class IsQuestionClassroomMember(permissions.BasePermission):
    def has_permission(self, request, view):
        question_id = view.kwargs.get('pk')

        return MemberShip.objects.filter( user=request.user,classroom__questions__id=question_id).exists()