
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Assignment,Submission,SubCriteria,Score,ActivityBudget
from .serializers import BankSerializer,ScoreSerializer,SubCriteriaSerializer,SubmissionSerializer,ActivityBudgetSerializer,AssignmentSerializer
from django.shortcuts import get_object_or_404
#from .permissions import Isteacher
from classes.models import ClassRoom,MemberShip
from django.contrib.auth import get_user_model
from django.utils import timezone
from .permissions import IsTeacher
from django.db import models
User=get_user_model()

from .permissions import IsClassroomMember
#================================================================================================

class CreateAssignmentView(generics.CreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def post(self, request, pk):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        is_teacher = MemberShip.objects.filter(user=request.user, classroom=classroom, role__in=['TEACHER', 'MENTOR']).exists()
        if not is_teacher:
             return Response({'error': ' فقط استاد اجازه دارد'}, status=403)
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(classroom=classroom, created_by=request.user)
            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status=400)

#==================================================================================================


class BankListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Assignment.objects.filter(save_to_bank=True)

#===============================================================================================

class ReuseAssignmentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk, save_to_bank=True)
        classroom_id = request.data.get('classroom_id')
        classroom = get_object_or_404(ClassRoom, pk=classroom_id)
        is_teacher = MemberShip.objects.filter(user=request.user,classroom=classroom,role='TEACHER').exists()
        if not is_teacher:
            return Response({'error': 'فقط استاد می‌تواند تمرین اضافه کند'}, status=403)
        # کپی بساز
        Assignment.objects.create(
            title=assignment.title,description=assignment.description,score=assignment.score,
            deadline=request.data.get('deadline'),submission_limit=assignment.submission_limit,answer_type=assignment.answer_type,
            assignment_type=assignment.assignment_type,late_penalty=assignment.late_penalty,classroom=classroom,created_by=request.user,save_to_bank=False)
        
        return Response({'message': 'تمرین با موفقیت اضافه شد'}, status=201)

#================================================================================================

class SubmitAnswerView(generics.GenericAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        membership = MemberShip.objects.filter(user=request.user,classroom=assignment.classroom).first()
        if not membership:
            return Response({'error': 'شما عضو این کلاس نیستید'}, status=400)
        # ===== جریمه زمانی =====
        penalty = 0
        if assignment.deadline and assignment.deadline < timezone.now():
            if assignment.late_penalty:
                # هر ۲۴ ساعت دیرتر، ۲۰٪ کسر میشه
                hours_late = (timezone.now() - assignment.deadline).total_seconds() / 3600
                days_late = int(hours_late // 24) + 1
                penalty = days_late * (assignment.late_penalty / 100)
                # حداکثر جریمه ۱۰۰٪
                if penalty > 1:
                    penalty = 1

        count = Submission.objects.filter(user=request.user,assignment=assignment).count()
        if count >= assignment.submission_limit:
            return Response({'error': 'تعداد ارسال مجاز تمام شده'}, status=400)

        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            submission = serializer.save(user=request.user, assignment=assignment, penalty=penalty)
            # ذخیره جریمه (اگه فیلد داشته باشی)
            return Response({'message': 'پاسخ ارسال شد','penalty': penalty,'final_score': assignment.score * (1 - penalty)}, status=201)

        return Response(serializer.errors, status=400)

#===================================================================================================

class ScoreView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        classroom = submission.assignment.classroom
        if not MemberShip.objects.filter(
            user=request.user, classroom=classroom, role__in=['TEACHER', 'MENTOR']
        ).exists():
            return Response({'error': 'فقط استاد یا منتور میتواند نمره دهد'}, status=403)

        raw_score = request.data.get('score')
        if raw_score is None:
            return Response({'error': 'نمره را وارد کنید'}, status=400)
        final_score = float(raw_score) * (1 - float(submission.penalty or 0))

        member = None
        user_id = request.data.get('user_id')
        if user_id:
            member = MemberShip.objects.filter(user_id=user_id, classroom=classroom).first()
            if not submission.group_id or not member:
                return Response({'error': 'نمره‌ی جدا فقط برای عضو گروه است'}, status=400)

        score_obj, _ = Score.objects.update_or_create(
            submission=submission, member=member,
            defaults={'scored': request.user, 'score': final_score,
                      'feedback': request.data.get('feedback', '')},
        )
        return Response({'id': score_obj.id, 'score': score_obj.score}, status=201)
#===================================================================================================

class SubmissionDetailView(generics.RetrieveAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Submission.objects.all()

#=================================================================================================

class SubCriteriaView(generics.CreateAPIView):
    serializer_class = SubCriteriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        
        is_teacher = MemberShip.objects.filter(user=request.user,classroom=assignment.classroom,role='TEACHER').exists()
        if not is_teacher:
            return Response({'error': 'فقط استاد می‌تواند ریزبارم تعریف کند'}, status=403)
        # چک کن مجموع ریزبارم‌ها از نمره کل تمرین بیشتر نشه
        existing_total = SubCriteria.objects.filter(assignment=assignment).aggregate( total=models.Sum('max_score'))['total'] or 0
        
        new_score = request.data.get('max_score', 0)
        if existing_total + new_score > assignment.score:
            return Response({'error': f'مجموع ریزبارم‌ها ({existing_total + new_score}) از نمره کل تمرین ({assignment.score}) بیشتر است'}, status=400)
        
        serializer = SubCriteriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assignment=assignment)
            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status=400)

#=====================================================================================================

class ActivityBudgetView(generics.CreateAPIView):
    serializer_class = ActivityBudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        
        is_teacher = MemberShip.objects.filter(user=request.user,classroom=classroom,role='TEACHER').exists()
        if not is_teacher:
            return Response({'error': 'فقط استاد می‌تواند بودجه تعریف کند'}, status=403)
        
        # ===== چک کن مجموع بودجه‌ها از ۱۰۰ بیشتر نشه =====
        existing_total = ActivityBudget.objects.filter(classroom=classroom).aggregate(total=models.Sum('max_score'))['total'] or 0
        
        new_score = request.data.get('max_score', 0)
        if existing_total + new_score > 100:
            return Response({'error': f'مجموع بودجه‌ها ({existing_total + new_score}) از ۱۰۰ بیشتر است'}, status=400)
        
        data = {'classroom': classroom.id,'activity_type': request.data.get('activity_type'),'max_score': request.data.get('max_score'),}
        
        serializer = ActivityBudgetSerializer(data=data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status=400)

#==================================================================================================

class ClassAssignmentListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        classroom_id = self.kwargs.get('pk')
        return Assignment.objects.filter(classroom_id=classroom_id)

#==============================================================================================

class AssignmentDetailView(generics.RetrieveAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Assignment.objects.all()

#==========================================================================================

class AssignmentSubmissionsListView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        assignment_id = self.kwargs.get('pk')
        assignment = get_object_or_404(Assignment, pk=assignment_id)
    
        is_teacher_or_mentor = MemberShip.objects.filter(user=self.request.user,classroom=assignment.classroom,role__in=['TEACHER', 'MENTOR']).exists()
        if not is_teacher_or_mentor:
            return Submission.objects.none()
        
        return Submission.objects.filter(assignment=assignment)

#=================================================================================================

class UserSubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        classroom_id = self.kwargs.get('pk')
        return Submission.objects.filter(user=self.request.user,assignment__classroom_id=classroom_id)
    
#================================================================================================

class MyGradesView(generics.ListAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Score.objects.filter(submission__user=self.request.user)

#========================================================================================================

class BudgetListView(generics.ListAPIView):
    serializer_class = ActivityBudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        classroom_id = self.kwargs.get('pk')
        return ActivityBudget.objects.filter(classroom_id=classroom_id)

# =======================================================================================================
#  فاز ۷ — جدول نمره و رتبه‌بندی
# =======================================================================================================

class ClassGradeTableView(generics.GenericAPIView):
    """
    جدول نمرات و رتبه‌بندی دانشجوهای یک کلاس
    قابل مشاهده برای استاد و دانشجو
    """
    permission_classes = [permissions.IsAuthenticated,IsClassroomMember]
    def get(self, request, pk):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        students = MemberShip.objects.filter(classroom=classroom,role='STUDENT')
        grade_list = []
        for student in students:
            total_score = Score.objects.filter(submission__user=student.user,submission__assignment__classroom=classroom).aggregate(total=models.Sum('score'))['total'] or 0
            submitted_count = Submission.objects.filter(user=student.user,assignment__classroom=classroom).count()
            grade_list.append({'student_id': student.user.id,'student_name': student.user.get_full_name() or student.user.username,'total_score': float(total_score),'submitted_count': submitted_count,'assignments_count': Assignment.objects.filter(classroom=classroom).count(),})
        grade_list.sort(key=lambda x: x['total_score'], reverse=True)
        
        for index, item in enumerate(grade_list):
            item['rank'] = index + 1
        
        return Response(grade_list, status=200)

#============================================================================================
class StudentActivityView(generics.ListAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_id, student_id):
        student = get_object_or_404(User, pk=student_id)
        if request.user != student:
            is_teacher_or_mentor = MemberShip.objects.filter(user=request.user,classroom_id=class_id,role__in=['TEACHER', 'MENTOR']).exists()
            if not is_teacher_or_mentor:
                return Response({'error': 'شما دسترسی به این صفحه ندارید'},status=403)
        scores = Score.objects.filter(submission__user=student, submission__assignment__classroom_id=class_id).select_related('submission__assignment')
        activities = []

        for score in scores:
            assignment = score.submission.assignment
            subcriteria = SubCriteria.objects.filter(assignment=assignment)
            subcriteria_data = []
            for sub in subcriteria:
                subcriteria_data.append({'title': sub.title,'max_score': float(sub.max_score),})

            activities.append({'assignment_id': assignment.id,'assignment_title': assignment.title,'score': float(score.score),'max_score': float(assignment.score),'feedback': score.feedback,'submitted_at': score.submission.submitted_at,'scored_at': score.scored_at,'penalty': float(score.submission.penalty or 0),'subcriteria': subcriteria_data,})

        return Response({'student_name': student.get_full_name() or student.username,'activities': activities,}, status=200)
#================================================================================================


