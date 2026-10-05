
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ClassRoom, MemberShip, Invitation
from .serializers import ClassroomCreateSerializer, MembershipSerializer,ClassroomSerializer
from django.shortcuts import get_object_or_404
import secrets
from django.utils import timezone
from datetime import timedelta
from .permissions import IsTeacher,IsClassroomTeacher
from django.contrib.auth import get_user_model
from .permissions import IsClassroomTeacher
from django.db import transaction
User=get_user_model()


#------------------------------------------------------------------------------------------------------
#لیست کاس های کاربر
class ListClassroomView(generics.ListAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
                user_memberships = MemberShip.objects.filter(user=self.request.user)
                classroom_ids = user_memberships.values_list('classroom_id', flat=True)
                return ClassRoom.objects.filter(id__in=classroom_ids)

#-------------------------------------------------------------------------------------------------------
class ClassroomDetailView(generics.RetrieveAPIView):
   serializer_class = ClassroomSerializer
   permission_classes = [permissions.IsAuthenticated]
   queryset = ClassRoom.objects.all()

#-------------------------------------------------------------------------------------------------------

class CreateClassroomView(generics.CreateAPIView):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassroomCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        classroom = serializer.save(owner=self.request.user)
        MemberShip.objects.create(user=self.request.user, classroom=classroom, role='TEACHER')


#--------------------------------------------------------------------------------------------------------
class JoinClassroomView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        classroom = get_object_or_404(ClassRoom, pk=pk)

        if MemberShip.objects.filter(user=request.user, classroom=classroom).exists():
            return Response({'error': 'شما قبلاً در این کلاس عضو هستید'},
                            status=status.HTTP_400_BAD_REQUEST)

        current_members = MemberShip.objects.filter(classroom=classroom).count()
        if classroom.max_members is not None and current_members >= classroom.max_members:
            return Response({'error': 'ظرفیت کلاس پر است'},
                            status=status.HTTP_400_BAD_REQUEST)

        if classroom.classtype == 'PRIVATE':
            if classroom.securitytype == 'INVITE':
                return Response({'error': 'این کلاس فقط با دعوتنامه قابل عضویت است'},
                                status=status.HTTP_403_FORBIDDEN)
            if classroom.securitytype == 'PASSWORD':
                if request.data.get('password') != classroom.password:
                    return Response({'error': 'گذرواژه اشتباه است'},
                                    status=status.HTTP_400_BAD_REQUEST)

        MemberShip.objects.create(user=request.user, classroom=classroom, role='STUDENT')
        return Response({'message': 'عضویت با موفقیت انجام شد'}, status=status.HTTP_200_OK)
#-------------------------------------------------------------------------------------------------
class LeaveClassroomView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,pk):
      classroom=get_object_or_404(ClassRoom, pk=pk)
      membership = MemberShip.objects.filter(user=request.user,classroom=classroom).first()
      if not membership:
         return Response({"detail": "شما عضو این کلاس نیستید"},status=status.HTTP_404_NOT_FOUND)
    # صاحب کلاس نمی‌تواند خارج شود
      if request.user == classroom.owner:
         return Response({"detail": "صاحب کلاس نمی‌تواند خارج شود"},status=status.HTTP_400_BAD_REQUEST)
      membership.delete()
      return Response({"detail": "با موفقیت از کلاس خارج شدید"},status=status.HTTP_200_OK)

#------------------------------------------------------------------------------------------------

class RetrieveUpdateclassroomView(generics.RetrieveUpdateAPIView):
    queryset=ClassRoom.objects.all()
    serializer_class=ClassroomSerializer
    permission_classes=[permissions.IsAuthenticated,IsClassroomTeacher]

#-------------------------------------------------------------------------------------------------

class SendInvitationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,IsClassroomTeacher]
    def post(self, request, pk):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        invited_user = get_object_or_404(User, username=request.data.get('username'))

        if MemberShip.objects.filter(user=invited_user, classroom=classroom).exists():
            return Response({'error': 'کاربر عضو کلاس است'},status=status.HTTP_400_BAD_REQUEST)
        if Invitation.objects.filter(classroom=classroom, invited_user=invited_user,status=Invitation.Status.PENDING, expires_at__gt=timezone.now(),).exists():
            return Response({'error': 'دعوتنامه فعال وجود دارد'},status=status.HTTP_400_BAD_REQUEST)
        token = secrets.token_urlsafe(32)
        Invitation.objects.create(classroom=classroom,invited_by=request.user,invited_user=invited_user,token=token,expires_at=timezone.now() + timedelta(days=7),)
        return Response({'message': 'دعوتنامه ارسال شد', 'token': token},
                        status=status.HTTP_201_CREATED)

#------------------------------------------------------------------------------------------------
class AcceptInvitationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        invitation = Invitation.objects.filter(token=token).select_related('classroom').first()
        if not invitation:
            return Response({'error': 'توکن وجود ندارد'}, status=status.HTTP_404_NOT_FOUND)

        if invitation.invited_user != request.user:
            return Response({'error': 'این دعوتنامه برای شما نیست'},status=status.HTTP_403_FORBIDDEN)

        if invitation.status != Invitation.Status.PENDING:
            return Response({'error': 'دعوتنامه قبلاً استفاده شده'},status=status.HTTP_400_BAD_REQUEST)

        if invitation.expires_at < timezone.now():
            return Response({'error': 'دعوتنامه منقضی شده'},status=status.HTTP_400_BAD_REQUEST)
        classroom = invitation.classroom
        current_members = MemberShip.objects.filter(classroom=classroom).count()
        if classroom.max_members is not None and current_members >= classroom.max_members:
            return Response({'error': 'ظرفیت کلاس پر است'},status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            MemberShip.objects.get_or_create(user=request.user, classroom=classroom, defaults={'role': 'STUDENT'},)
            invitation.status = Invitation.Status.ACCEPT
            invitation.save()

        return Response({'message': 'عضویت با موفقیت انجام شد'}, status=status.HTTP_200_OK)
#--------------------------------------------------------------------------------------------


class AddMemberView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,IsClassroomTeacher]
    def post(self, request, pk):
        username = request.data.get('username')
        role = request.data.get('role')  # 'TEACHER' یا 'MENTOR'
        if not username:
            return Response({'error': 'نام کاربری را وارد کنید'}, status=400)
        if role not in ['TEACHER', 'MENTOR']:
            return Response({'error': 'نقش باید TEACHER یا MENTOR باشد'}, status=400)
        user = get_object_or_404(User, username=username)
        classroom = get_object_or_404(ClassRoom, pk=pk)
        if user == request.user:
            return Response({'error': 'شما خودتان استاد کلاس هستید'}, status=400)
        if MemberShip.objects.filter(user=user, classroom=classroom).exists():
            return Response({'error': 'کاربر قبلاً در این کلاس عضو است'}, status=400)
        membership = MemberShip.objects.create(user=user,classroom=classroom,role=role)
        return Response({'message': f'کاربر {username} با نقش {role} به کلاس اضافه شد'},status=201)

#-------------------------------------------------------------------------------------------------
#لیست اعضای آن کلاس

class ClassroomMembersView(generics.ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        classroom_id = self.kwargs.get('pk')
        return MemberShip.objects.filter(classroom_id=classroom_id)

#-------------------------------------------------------------------------------------------------

class RemoveMemberView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsClassroomTeacher]

    def post(self, request, pk):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'آیدی کاربر را وارد کنید'},status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, pk=user_id)
        if user == classroom.owner:
            return Response({"detail": "صاحب کلاس را نمی‌توان حذف کرد"},status=status.HTTP_400_BAD_REQUEST)
        membership = MemberShip.objects.filter(user=user,classroom=classroom).first()
        if not membership:
            return Response({"detail": "کاربر عضو این کلاس نیست"},status=status.HTTP_404_NOT_FOUND)
        membership.delete()
        return Response({"detail": "کاربر با موفقیت حذف شد"},status=status.HTTP_200_OK)

#----------------------------------------------------------------------------------------------

#لیست کلاس هایی ک هست
class ClassroomListView(generics.ListAPIView):
    queryset=ClassRoom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    