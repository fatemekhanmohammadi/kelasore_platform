from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
User = get_user_model()
from decimal import Decimal
from classes.models import MemberShip
from groups.models import Group
from .models import Assignment, Submission, Score, SubCriteria

# ================================================================

class SubmitAnswerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(username='teacher',password='testpass123')
        self.student = User.objects.create_user(username='student',password='testpass123')
        # ساخت کلاس توسط Teacher
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(reverse('classes:create-class'),{'title': 'کلاس تستی','classtype': 'PUBLIC'},format='json')
        self.classroom_id = response.data['id']
        # دانشجو وارد کلاس می‌شود
        self.client.force_authenticate(user=self.student)
        self.client.post(reverse('classes:join-class',kwargs={'pk': self.classroom_id}),format='json')
        # Teacher assignment می‌سازد
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(reverse('assignments:createassignment',kwargs={'pk': self.classroom_id}),{'title': 'تمرین تستی','score': 20,'deadline': (timezone.now() + timedelta(days=7)).isoformat(),'answer_type': 'TEXT','assignment_type': 'INDIVIDUAL','submission_limit': 3},format='json')
        self.assignment_id = response.data['id']

    def test_submit_over_submission_limit_rejected(self):
        Assignment.objects.filter(pk=self.assignment_id).update(submission_limit=1)
        self.client.force_authenticate(user=self.student)
        url = reverse('assignments:submit', kwargs={'pk': self.assignment_id})
        data = {'assignment': self.assignment_id, 'text': 'پاسخ تستی'}
        first = self.client.post(url, data, format='json')
        second = self.client.post(url, data, format='json')
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(
            Submission.objects.filter(user=self.student, assignment_id=self.assignment_id).count(), 1
        )

    def test_submit_before_deadline_no_penalty(self):
        Assignment.objects.filter(pk=self.assignment_id).update(deadline=timezone.now() + timedelta(days=1), late_penalty=20)
        self.client.force_authenticate(user=self.student)
        url = reverse('assignments:submit', kwargs={'pk': self.assignment_id})
        response = self.client.post(url, {'assignment': self.assignment_id, 'text': 'پاسخ تستی'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['penalty'], 0)

    def test_submit_after_deadline_is_accepted(self):
        Assignment.objects.filter(pk=self.assignment_id).update(deadline=timezone.now() - timedelta(days=1))
        self.client.force_authenticate(user=self.student)
        url = reverse('assignments:submit', kwargs={'pk': self.assignment_id})
        response = self.client.post(url, {'assignment': self.assignment_id, 'text': 'پاسخ تستی'}, format='json')
        self.assertEqual(response.status_code, 201)


#================================================================
class SubCriteriaTestCase(TestCase):
    def setUp(self):
       self.client = APIClient()
       self.teacher = User.objects.create_user( username='teacher', password='testpass123')
       self.student = User.objects.create_user( username='student', password='testpass123')
    # ساخت کلاس
       self.client.force_authenticate(user=self.teacher)
       response = self.client.post(reverse('classes:create-class'),{'title': 'کلاس تستی','classtype': 'PUBLIC'},format='json')
       self.classroom_id = response.data['id']
    # ورود دانشجو
       self.client.force_authenticate(user=self.student)
       self.client.post( reverse('classes:join-class',kwargs={'pk': self.classroom_id}),format='json')
    # ساخت تمرین
       self.client.force_authenticate(user=self.teacher)
       response = self.client.post(reverse('assignments:createassignment',kwargs={'pk': self.classroom_id}), {'title': 'تمرین تستی','score': 10,'deadline': '2026-10-10T20:00:00Z','answer_type': 'TEXT','assignment_type': 'INDIVIDUAL',},format='json')
       self.assignment_id = response.data['id']
       Assignment.objects.filter(pk=self.assignment_id).update(score=10)


    def _add(self, title, max_score, user=None):
        self.client.force_authenticate(user=user or self.teacher)
        url = reverse('assignments:sub-criteria', kwargs={'pk': self.assignment_id})
        data = {'assignment': self.assignment_id, 'title': title, 'max_score': max_score}
        return self.client.post(url, data, format='json')

    def test_teacher_adds_subcriteria_success(self):
        response = self._add('اجرا شدن پروژه', 5)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SubCriteria.objects.filter(assignment_id=self.assignment_id).count(), 1)

    def test_total_over_assignment_score_rejected(self):
        self.assertEqual(self._add('الف', 6).status_code, 201)
        self.assertEqual(self._add('ب', 5).status_code, 400)
        self.assertEqual(SubCriteria.objects.filter(assignment_id=self.assignment_id).count(), 1)

    def test_total_equal_to_assignment_score_allowed(self):
        self.assertEqual(self._add('الف', 6).status_code, 201)
        self.assertEqual(self._add('ب', 4).status_code, 201)

    def test_student_cannot_add_subcriteria(self):
        response = self._add('الف', 5, user=self.student)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SubCriteria.objects.filter(assignment_id=self.assignment_id).count(), 0)

#================================================================

class GradingTestCase(TestCase):
    def setUp(self):
        

    
        self.client = APIClient()

        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123'
        )

        self.s1 = User.objects.create_user(
            username='s1',
            password='testpass123'
        )

        self.s2 = User.objects.create_user(
            username='s2',
            password='testpass123'
        )

        # ساخت کلاس
        self.client.force_authenticate(user=self.teacher)

        r = self.client.post(
            reverse('classes:create-class'),
            {
                'title': 'کلاس تستی',
                'classtype': 'PUBLIC'
            },
            format='json'
        )

        self.classroom_id = r.data['id']

        # اضافه کردن دانشجوها
        for u in (self.s1, self.s2):
            self.client.force_authenticate(user=u)

            self.client.post(
                reverse(
                    'classes:join-class',
                    kwargs={'pk': self.classroom_id}
                ),
                format='json'
            )

        # ساخت تمرین توسط استاد
        self.client.force_authenticate(user=self.teacher)

        r = self.client.post(
            reverse(
                'assignments:createassignment',
                kwargs={'pk': self.classroom_id}
            ),
            {
                'title': 'تمرین تستی',
                'score': 10,
                'deadline': '2026-10-10T20:00:00Z',
                'answer_type': 'TEXT',
                'assignment_type': 'INDIVIDUAL',
            },
            format='json'
        )

        self.assignment_id = r.data['id']

        Assignment.objects.filter(
            pk=self.assignment_id
        ).update(
            score=10,
            late_penalty=20
        )

        # Membership دانشجوها
        self.m1 = MemberShip.objects.get(
            user=self.s1,
            classroom_id=self.classroom_id
        )

        self.m2 = MemberShip.objects.get(
            user=self.s2,
            classroom_id=self.classroom_id
        )

        # ساخت گروه
        self.group = Group.objects.create(
            name='گروه ۱',
            classroom_id=self.classroom_id,
            created_by=self.teacher
        )

        self.group.members.add(
            self.m1,
            self.m2
        )



    def _score(self, submission, score, **extra):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('assignments:score', kwargs={'pk': submission.pk})
        return self.client.post(url, {'score': score, **extra}, format='json')

    def test_late_penalty_is_saved(self):
        Assignment.objects.filter(pk=self.assignment_id).update(deadline=timezone.now() - timedelta(hours=2))
        self.client.force_authenticate(user=self.s1)
        r = self.client.post(reverse('assignments:submit', kwargs={'pk': self.assignment_id}), {'assignment': self.assignment_id, 'text': 'x'}, format='json')
        self.assertEqual(r.status_code, 201)
        sub = Submission.objects.get(user=self.s1, assignment_id=self.assignment_id)
        self.assertEqual(sub.penalty, Decimal('0.20'))

    def test_score_applies_penalty(self):
        sub = Submission.objects.create(user=self.s1, assignment_id=self.assignment_id, text='x', penalty=Decimal('0.20'))
        self.assertEqual(self._score(sub, 10).status_code, 201)
        self.assertEqual(Score.objects.get(submission=sub).score, Decimal('8.00'))

    def test_group_score_is_saved_for_group(self):
        sub = Submission.objects.create(user=self.s1, group=self.group, assignment_id=self.assignment_id, text='x')
        self.assertEqual(self._score(sub, 10).status_code, 201)
        score = Score.objects.get(submission=sub, member__isnull=True)
        self.assertEqual(score.score, Decimal('10.00'))

    def test_member_can_have_different_score(self):
        sub = Submission.objects.create(user=self.s1, group=self.group, assignment_id=self.assignment_id, text='x')
        self._score(sub, 10)
        self._score(sub, 5, user_id=self.s2.pk)
        self.assertEqual(Score.objects.get(submission=sub, member__isnull=True).score, Decimal('10.00'))
        self.assertEqual(Score.objects.get(submission=sub, member=self.m2).score, Decimal('5.00'))

    def test_member_score_rejected_for_individual_submission(self):
        sub = Submission.objects.create(user=self.s1, assignment_id=self.assignment_id, text='x')
        self.assertEqual(self._score(sub, 5, user_id=self.s2.pk).status_code, 400)