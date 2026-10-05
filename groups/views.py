from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Group
from .serializers import GroupSerializer
from classes.models import ClassRoom, MemberShip
from assignments.models import Assignment,Score
from django.contrib.auth import get_user_model
from django.db.models import Sum
import random

User = get_user_model()



#-------------------------------------------------------------------------------------------------------

class GroupCreateAPIView(generics.CreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, class_id):
        classroom = get_object_or_404(ClassRoom, pk=class_id)
        is_teacher = MemberShip.objects.filter(user=request.user,classroom=classroom,role='TEACHER').exists()
        if not is_teacher:
            return Response({'error': 'فقط استاد می‌تواند گروه بسازد'}, status=403)
        name = request.data.get('name')
        if not name:
            return Response({'error': 'نام گروه الزامی است'}, status=400)
        group = Group.objects.create(name=name,classroom=classroom,created_by=request.user)
        
        members_ids = request.data.get('members', [])
        members = MemberShip.objects.filter(id__in=members_ids)
        group.members.set(members)
        return Response({'id': group.id, 'name': group.name}, status=201)

# ===== گروه‌بندی خودکار بر اساس نمره ======================================================================

class CreateAutoGroupView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        is_teacher = MemberShip.objects.filter(user=request.user,classroom=classroom,role='TEACHER').exists()
        if not is_teacher:
            return Response({'error': 'فقط استاد می‌تواند گروه بسازد'}, status=403)
        students = MemberShip.objects.filter(classroom=classroom, role='STUDENT')
        if not students.exists():
            return Response({'error': 'هیچ دانشجویی در کلاس وجود ندارد'}, status=400)

        # محاسبه نمره کل هر دانشجو از تمام تمرین‌ها
        student_scores = []
        for student in students:
            total_score = Score.objects.filter(submission__user=student.user,submission__assignment__classroom=classroom).aggregate(total=Sum('score'))['total'] or 0
            student_scores.append({'member': student,'score': total_score})

        # مرتب‌سازی از بیشترین به کمترین نمره
        student_scores.sort(key=lambda x: x['score'], reverse=True)
        group_count = int(request.data.get('group_count', 3))
        groups = []
        for i in range(group_count):
            group = Group.objects.create(name=f'گروه {i+1}',classroom=classroom,created_by=request.user)
            groups.append(group)
            
        for i, item in enumerate(student_scores):
          round_no, pos = divmod(i, group_count)
          group_index = pos if round_no % 2 == 0 else group_count - 1 - pos
          groups[group_index].members.add(item['member'])
        return Response({'message': f'{group_count} گروه با توزیع متوازن ساخته شد','groups': [{'id': g.id,'name': g.name,'member_count': g.members.count()} for g in groups]}, status=201)

#=================================================================================================

class GroupListView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        classroom_id = self.kwargs.get('pk')
        print('🔵 Classroom ID for groups:', classroom_id)  # برای دیباگ
        return Group.objects.filter(classroom_id=classroom_id)
    
#============================================================================================