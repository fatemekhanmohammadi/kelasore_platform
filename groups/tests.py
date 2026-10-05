from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from classes.models import MemberShip
from assignments.models import Submission, Score
from .models import Group
User = get_user_model()

#==============================================================================================================

class GroupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # ساخت Teacher
        self.teacher = User.objects.create_user(username='teacher',password='testpass123')
        self.client.force_authenticate(user=self.teacher)
        # ساخت کلاس
        response = self.client.post(reverse('classes:create-class'),{'title': 'کلاس تستی','classtype': 'PUBLIC'},format='json')
        self.classroom_id = response.data['id']
        # ساخت Assignment
        response = self.client.post(reverse('assignments:createassignment',kwargs={'pk': self.classroom_id}),{'title': 'تمرین تستی','score': 20,'deadline': (timezone.now() + timedelta(days=7)).isoformat(),'answer_type': 'TEXT','assignment_type': 'GROUP','submission_limit': 3},format='json')
        self.assignment_id = response.data['id']



    def _make_student(self, name, score=None):
        user = User.objects.create_user(username=name, password='testpass123')
        MemberShip.objects.create(user=user, classroom_id=self.classroom_id, role='STUDENT')
        if score is not None:
            sub = Submission.objects.create(user=user, assignment_id=self.assignment_id, text='x')
            Score.objects.create(submission=sub, scored=self.teacher, score=score)
        return user

    def _auto_group(self, group_count):
        url = reverse('groups:group-auto', kwargs={'pk': self.classroom_id})
        return self.client.post(url, {'group_count': group_count}, format='json')

    def test_auto_group_sizes_are_balanced(self):
        for i in range(7):
            self._make_student(f's{i}', score=50 + i)
        response = self._auto_group(3)
        self.assertEqual(response.status_code, 201)
        sizes = sorted(g.members.count() for g in Group.objects.filter(classroom_id=self.classroom_id))
        self.assertEqual(sizes, [2, 2, 3])

    def test_auto_group_scores_are_balanced(self):
        for name, score in [('a', 100), ('b', 90), ('c', 80), ('d', 70)]:
            self._make_student(name, score)
        self._auto_group(2)
        totals = []
        for g in Group.objects.filter(classroom_id=self.classroom_id):
            users = [getattr(m, 'user', m) for m in g.members.all()]
            totals.append(Score.objects.filter(submission__user__in=users).aggregate(t=Sum('score'))['t'])
        self.assertEqual(totals[0], totals[1])

    def test_auto_group_student_without_score(self):
        self._make_student('a', 100)
        self._make_student('b')  # بدون نمره
        response = self._auto_group(2)
        self.assertEqual(response.status_code, 201)


#==============================================================================================================