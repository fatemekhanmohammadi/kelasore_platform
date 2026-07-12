
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
from .permissions import Isteacher
from django.contrib.auth import get_user_model


User=get_user_model()


# ✅ ویو جدید برای نمایش صفحه HTML

def create_classroom_page(request):
    return render(request, 'classes/create_class.html')

def list_classrooms_page(request):
    return render(request, 'accounts/dashboard.html')

def classroom_detail_page(request, pk):
    return render(request, 'classes/class_detail.html', {'class_id': pk})

def update_classroom_page(request, pk):
    return render(request, 'classes/update-class.html', {'class_id': pk})

# ✅ ویو API که داری (همون)

class ListClassroomView(generics.ListAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
                user_memberships = MemberShip.objects.filter(user=self.request.user)
                classroom_ids = user_memberships.values_list('classroom_id', flat=True)
                return ClassRoom.objects.filter(id__in=classroom_ids)


class ClassroomDetailView(generics.RetrieveAPIView):
   serializer_class = ClassroomSerializer
   permission_classes = [permissions.IsAuthenticated]
   queryset = ClassRoom.objects.all()


class CreateClassroomView(generics.CreateAPIView):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassroomCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        classroom = serializer.save(owner=self.request.user)
        MemberShip.objects.create(user=self.request.user, classroom=classroom, role='TEACHER')

class JoinClassroomView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # ۱. پیدا کردن کلاس
        classroom = get_object_or_404(ClassRoom, pk=pk)
        
        # ۲. چک کردن عضویت قبلی
        existing_membership = MemberShip.objects.filter(
            user=request.user,
            classroom=classroom
        ).first()
        
        if existing_membership:
            return Response(
                {'error': 'شما قبلاً در این کلاس عضو هستید'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ۳. چک کردن ظرفیت
        current_members = MemberShip.objects.filter(classroom=classroom).count()
        if classroom.max_members is not None and current_members >= classroom.max_members:
            return Response(
                {'error': 'ظرفیت کلاس پر است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ۴. چک کردن رمز (برای کلاس خصوصی)
        if classroom.classtype == 'PRIVATE' and classroom.securitytype == 'PASSWORD':
            entered_password = request.data.get('password')
            if entered_password != classroom.password:
                return Response(
                    {'error': 'گذرواژه اشتباه است'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # ۵. ثبت‌نام کاربر
        membership, created = MemberShip.objects.get_or_create(
            user=request.user,
            classroom=classroom,
            defaults={'role': 'STUDENT'}
        )
        
        if created:
            return Response(
                {'message': 'عضویت با موفقیت انجام شد'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'خطا در ثبت‌نام، لطفاً دوباره تلاش کنید'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LeaveClassroomView(generics.GenericAPIView):

    def post(self,request,pk):
      classroom=get_object_or_404(ClassRoom, pk=pk)

      membership = MemberShip.objects.filter(
        user=request.user,
        classroom=classroom
        ).first()

      if not membership:
         return Response({"detail": "شما عضو این کلاس نیستید"},
                        status=status.HTTP_404_NOT_FOUND)

    # صاحب کلاس نمی‌تواند خارج شود
      if request.user == classroom.owner:
         return Response({"detail": "صاحب کلاس نمی‌تواند خارج شود"},
                        status=status.HTTP_400_BAD_REQUEST)

      membership.delete()

      return Response({"detail": "با موفقیت از کلاس خارج شدید"},
                    status=status.HTTP_200_OK)



class RetrieveUpdateclassroomView(generics.RetrieveUpdateAPIView):
    queryset=ClassRoom.objects.all()
    serializer_class=ClassroomSerializer
    permission_classes=[permissions.IsAuthenticated,Isteacher]




class SendInvitationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # ۱. پیدا کردن کلاس
        classroom = get_object_or_404(ClassRoom, pk=pk)

        # ۲. چک کن فرستنده استاد کلاسه
        is_teacher = MemberShip.objects.filter(
            user=request.user,
            classroom=classroom,
            role='TEACHER'
        ).exists()

        if not is_teacher:
            return Response({'error': 'فقط استاد می‌تواند دعوت‌نامه بفرستد'}, status=403)

        # ۳. پیدا کردن کاربر دعوت‌شده
        invited_username = request.data.get('username')
        invited_user = get_object_or_404(User, username=invited_username)

        # ۴. ساختن token و ذخیره دعوت‌نامه
        token = secrets.token_urlsafe(32)
        Invitation.objects.create(
            classroom=classroom,
            invited_by=request.user,
            invited_user=invited_user,
            token=token,
            expires_at=timezone.now() + timedelta(days=7)
        )

        return Response({'message': 'دعوت‌نامه ارسال شد', 'token': token}, status=201)



class AcceptInvitationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        invitation = Invitation.objects.filter(token=token).first()
        
        if not invitation:
            return Response({'error': 'توکن وجود ندارد'}, status=404)
        
        if invitation.expires_at < timezone.now():
            return Response({'error': 'دعوت‌نامه منقضی شده'}, status=400)
        
        if invitation.status != 'PENDING':
            return Response({'error': 'دعوت‌نامه قبلاً استفاده شده'}, status=400)
        
        MemberShip.objects.get_or_create(
            user=request.user,
            classroom=invitation.classroom,
            defaults={'role': 'STUDENT'}
        )
        
        invitation.status = 'ACCEPT'
        invitation.save()
        
        return Response({'message': 'عضویت با موفقیت انجام شد'}, status=200)