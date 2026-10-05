from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import ClassRoom, MemberShip, Invitation
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta


User = get_user_model()

#===================================================================================================
class RetrieveUpdateClassroomTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(username='teacher1', password='pass123', role='TEACHER')
        self.other_teacher = User.objects.create_user(username='teacher2', password='pass123', role='TEACHER')
        self.student = User.objects.create_user(username='student1', password='pass123', role='STUDENT')
        self.classroom = ClassRoom.objects.create(title='کلاس اصلی', owner=self.teacher, classtype='PUBLIC')
        MemberShip.objects.create(user=self.teacher, classroom=self.classroom, role='TEACHER')

    def _url(self):
        return reverse('classes:update_detail', kwargs={'pk': self.classroom.pk})
    def test_mentor_cannot_update_settings(self):
        mentor = User.objects.create_user(username='m2', password='pass123', role='STUDENT')
        MemberShip.objects.create(user=mentor, classroom=self.classroom, role='MENTOR')
        self.client.force_authenticate(mentor)
        response = self.client.patch(self._url(), {'title': 'هک شد'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.classroom.refresh_from_db()
        self.assertNotEqual(self.classroom.title, 'هک شد')
#==============================================================================================================
class AddMemberViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(username='student1', password='pass123', role='STUDENT')
        self.teacher = User.objects.create_user(username='teacher1', password='pass123', role='TEACHER')
        self.other_teacher = User.objects.create_user(username='teacher2', password='pass123', role='TEACHER')
        self.new_mentor = User.objects.create_user(username='mentor1', password='pass123', role='MENTOR')
        self.classroom = ClassRoom.objects.create(title='کلاس اصلی', owner=self.teacher, classtype='PUBLIC')
        MemberShip.objects.create(user=self.teacher, classroom=self.classroom, role='TEACHER')
        MemberShip.objects.create(user=self.student,classroom=self.classroom,role='STUDENT')

    def _url(self):
        return reverse('classes:add-member', kwargs={'pk': self.classroom.pk})
    def test_mentor_cannot_remove_member(self):
        mentor = User.objects.create_user(username='m2', password='pass123', role='STUDENT')
        MemberShip.objects.create(user=mentor, classroom=self.classroom, role='MENTOR')
        self.client.force_authenticate(mentor)
        response = self.client.post(self._url(), {'user_id': self.student.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(MemberShip.objects.filter(user=self.student, classroom=self.classroom).exists())

    def test_student_cannot_remove_member(self):
        other = User.objects.create_user(username='s2', password='pass123', role='STUDENT')
        MemberShip.objects.create(user=other, classroom=self.classroom, role='STUDENT')
        self.client.force_authenticate(self.student)
        response = self.client.post(self._url(), {'user_id': other.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(MemberShip.objects.filter(user=other, classroom=self.classroom).exists())

#===================================================================================================
class RemoveMemberViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(username='teacher1', password='pass123', role='TEACHER')
        self.other_teacher = User.objects.create_user(username='teacher2', password='pass123', role='TEACHER')
        self.student = User.objects.create_user(username='student1', password='pass123', role='STUDENT')
        self.classroom = ClassRoom.objects.create(title='کلاس اصلی', owner=self.teacher, classtype='PUBLIC')
        MemberShip.objects.create(user=self.teacher, classroom=self.classroom, role='TEACHER')
        self.student_membership = MemberShip.objects.create(user=self.student, classroom=self.classroom, role='STUDENT')

    def _url(self):
        return reverse('classes:remove-member', kwargs={'pk': self.classroom.pk})


    def test_mentor_cannot_remove_member(self):
        mentor = User.objects.create_user(username='m2', password='pass123', role='STUDENT')
        MemberShip.objects.create(user=mentor, classroom=self.classroom, role='MENTOR')
        self.client.force_authenticate(mentor)
        response = self.client.post(self._url(), {'user_id': self.student.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(MemberShip.objects.filter(user=self.student, classroom=self.classroom).exists())

    def test_student_cannot_remove_member(self):
        other = User.objects.create_user(username='s2', password='pass123', role='STUDENT')
        MemberShip.objects.create(user=other, classroom=self.classroom, role='STUDENT')
        self.client.force_authenticate(self.student)
        response = self.client.post(self._url(), {'user_id': other.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(MemberShip.objects.filter(user=other, classroom=self.classroom).exists())
# ===============================================================================================



class JoinClassroomViewTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(username="teacher1", password="Test12345", role="TEACHER")
        self.student = User.objects.create_user(username="student1", password="Test12345", role="STUDENT")
        self.public_classroom = ClassRoom.objects.create(
            title="Public Class", owner=self.owner, classtype="PUBLIC", max_members=2,
        )
        self.private_classroom = ClassRoom.objects.create(
            title="Private Class", owner=self.owner, classtype="PRIVATE",
            securitytype="PASSWORD", password="secret123",
        )
        self.invite_classroom = ClassRoom.objects.create(
            title="Invite Class", owner=self.owner, classtype="PRIVATE",
            securitytype="INVITE",  # مقدار رو مطابق choices خودت بذار
        )
        self.unlimited_classroom = ClassRoom.objects.create(
            title="Unlimited Class", owner=self.owner, classtype="PUBLIC", max_members=None,
        )

    def _join_url(self, pk):
        return reverse("classes:join-class", kwargs={"pk": pk})

    def _is_member(self, user, classroom):
        return MemberShip.objects.filter(user=user, classroom=classroom).exists()

    # --- کلاس عمومی ---
    def test_join_public_classroom_success(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(self._join_url(self.public_classroom.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self._is_member(self.student, self.public_classroom))

    def test_join_classroom_role_is_student_even_if_global_role_is_teacher(self):
        other_teacher = User.objects.create_user(username="t2", password="Test12345", role="TEACHER")
        self.client.force_authenticate(other_teacher)
        self.client.post(self._join_url(self.public_classroom.pk))
        membership = MemberShip.objects.get(user=other_teacher, classroom=self.public_classroom)
        self.assertEqual(membership.role, "STUDENT")

    def test_join_classroom_already_member(self):
        MemberShip.objects.create(user=self.student, classroom=self.public_classroom, role="STUDENT")
        self.client.force_authenticate(self.student)
        response = self.client.post(self._join_url(self.public_classroom.pk))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            MemberShip.objects.filter(user=self.student, classroom=self.public_classroom).count(), 1
        )

    # --- ظرفیت ---
    def test_join_classroom_full_capacity(self):
        s2 = User.objects.create_user(username="s2", password="Test12345", role="STUDENT")
        s3 = User.objects.create_user(username="s3", password="Test12345", role="STUDENT")
        MemberShip.objects.create(user=self.student, classroom=self.public_classroom, role="STUDENT")
        MemberShip.objects.create(user=s2, classroom=self.public_classroom, role="STUDENT")
        self.client.force_authenticate(s3)
        response = self.client.post(self._join_url(self.public_classroom.pk))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self._is_member(s3, self.public_classroom))

    def test_join_unlimited_classroom_success(self):
        for i in range(5):
            u = User.objects.create_user(username=f"u{i}", password="Test12345", role="STUDENT")
            MemberShip.objects.create(user=u, classroom=self.unlimited_classroom, role="STUDENT")
        self.client.force_authenticate(self.student)
        response = self.client.post(self._join_url(self.unlimited_classroom.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self._is_member(self.student, self.unlimited_classroom))
# --- کلاس خصوصی با رمز ---
    def test_join_private_classroom_correct_password(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(self._join_url(self.private_classroom.pk), {"password": "secret123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self._is_member(self.student, self.private_classroom))

    def test_join_private_classroom_wrong_password(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(self._join_url(self.private_classroom.pk), {"password": "wrongpass"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self._is_member(self.student, self.private_classroom))

    def test_join_private_classroom_no_password_sent(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(self._join_url(self.private_classroom.pk))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self._is_member(self.student, self.private_classroom))

    # --- کلاس فقط دعوت‌نامه ---
    def test_join_invite_only_classroom_without_invitation_rejected(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(self._join_url(self.invite_classroom.pk))
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))  # مطابق view خودت یکیش رو بذار
        self.assertFalse(self._is_member(self.student, self.invite_classroom))

    # --- احراز هویت و پیدا نشدن ---
    def test_join_classroom_invalid_pk(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(self._join_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_join_classroom_unauthenticated(self):
        response = self.client.post(self._join_url(self.public_classroom.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
class SendInvitationViewTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="teacher1", password="Test12345", role="TEACHER")
        self.student = User.objects.create_user(username="student1", password="Test12345", role="STUDENT")
        self.mentor = User.objects.create_user(username="mentor1", password="Test12345", role="STUDENT")
        self.invited = User.objects.create_user(username="invited1", password="Test12345", role="STUDENT")
        self.classroom = ClassRoom.objects.create(
            title="Class A", owner=self.owner, classtype="PRIVATE", securitytype="INVITE",
        )
        MemberShip.objects.create(user=self.owner, classroom=self.classroom, role="TEACHER")
        MemberShip.objects.create(user=self.student, classroom=self.classroom, role="STUDENT")
        MemberShip.objects.create(user=self.mentor, classroom=self.classroom, role="MENTOR")

    def _invite_url(self, pk):
        return reverse("classes:send-invitation", kwargs={"pk": pk})

    def _send(self, username=None, pk=None):
        return self.client.post(
            self._invite_url(pk or self.classroom.pk),
            {"username": username or self.invited.username},
        )

    def _invitation_exists(self):
        return Invitation.objects.filter(invited_user=self.invited).exists()

    def test_send_invitation_by_teacher_success(self):
        self.client.force_authenticate(self.owner)
        response = self._send()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        invitation = Invitation.objects.get(classroom=self.classroom, invited_user=self.invited)
        self.assertEqual(invitation.invited_by, self.owner)
        self.assertEqual(invitation.status, "PENDING")
        self.assertEqual(response.data["token"], invitation.token)

    def test_send_invitation_by_student_forbidden(self):
        self.client.force_authenticate(self.student)
        response = self._send()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self._invitation_exists())

    def test_send_invitation_by_mentor_forbidden(self):
        self.client.force_authenticate(self.mentor)
        response = self._send()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self._invitation_exists())

    def test_send_invitation_invalid_username(self):
        self.client.force_authenticate(self.owner)
        response = self._send(username="not_a_real_user")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Invitation.objects.count(), 0)

    def test_send_invitation_without_username(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self._invite_url(self.classroom.pk), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Invitation.objects.count(), 0)

    def test_send_invitation_invalid_classroom(self):
        self.client.force_authenticate(self.owner)
        response = self._send(pk=9999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(self._invitation_exists())

    def test_send_invitation_unauthenticated(self):
        response = self._send()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(self._invitation_exists())

    def test_send_invitation_to_existing_member_rejected(self):
        self.client.force_authenticate(self.owner)
        response = self._send(username=self.student.username)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Invitation.objects.filter(invited_user=self.student).exists())
    def test_send_duplicate_pending_invitation_rejected(self):
        self.client.force_authenticate(self.owner)
        self._send()
        response = self._send()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            Invitation.objects.filter(classroom=self.classroom, invited_user=self.invited).count(), 1
        )

    def test_send_invitation_after_previous_expired_allowed(self):
        Invitation.objects.create(
            classroom=self.classroom, invited_by=self.owner, invited_user=self.invited,
            token="old-token", expires_at=timezone.now() - timedelta(days=1), status="PENDING",
        )
        self.client.force_authenticate(self.owner)
        response = self._send()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Invitation.objects.filter(classroom=self.classroom, invited_user=self.invited).count(), 2
        )

    def test_send_invitation_expires_in_seven_days(self):
        self.client.force_authenticate(self.owner)
        self._send()
        invitation = Invitation.objects.get(classroom=self.classroom, invited_user=self.invited)
        delta = invitation.expires_at - timezone.now()
        self.assertGreater(delta, timedelta(days=6, hours=23))
        self.assertLess(delta, timedelta(days=7, hours=1))


class AcceptInvitationViewTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="teacher1", password="Test12345", role="TEACHER")
        self.invited = User.objects.create_user(username="invited1", password="Test12345", role="STUDENT")
        self.intruder = User.objects.create_user(username="intruder", password="Test12345", role="STUDENT")
        self.classroom = ClassRoom.objects.create(
            title="Class A", owner=self.owner, classtype="PRIVATE", securitytype="INVITE",
        )
        MemberShip.objects.create(user=self.owner, classroom=self.classroom, role="TEACHER")
        self.invitation = Invitation.objects.create(
            classroom=self.classroom, invited_by=self.owner, invited_user=self.invited,
            token="valid-token-123", expires_at=timezone.now() + timedelta(days=7),
            status="PENDING",
        )

    def _accept_url(self):
        return reverse("classes:accept-invitation")

    def _accept(self, user, token=None):
        self.client.force_authenticate(user)
        return self.client.post(self._accept_url(), {"token": token or self.invitation.token})

    def _is_member(self, user):
        return MemberShip.objects.filter(user=user, classroom=self.classroom).exists()

    def test_accept_invitation_success(self):
        response = self._accept(self.invited)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            MemberShip.objects.filter(user=self.invited, classroom=self.classroom, role="STUDENT").exists()
        )
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, "ACCEPT")

    def test_accept_invitation_invalid_token(self):
        response = self._accept(self.invited, token="fake-token")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(self._is_member(self.invited))

    def test_accept_invitation_without_token(self):
        self.client.force_authenticate(self.invited)
        response = self.client.post(self._accept_url(), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(self._is_member(self.invited))

    def test_accept_invitation_expired(self):
        self.invitation.expires_at = timezone.now() - timedelta(days=1)
        self.invitation.save()
        response = self._accept(self.invited)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self._is_member(self.invited))
    def test_accept_invitation_already_used(self):
        self.invitation.status = "ACCEPT"
        self.invitation.save()
        response = self._accept(self.invited)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self._is_member(self.invited))

    def test_accept_invitation_by_other_user_rejected(self):
        response = self._accept(self.intruder)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self._is_member(self.intruder))
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, "PENDING")

    def test_accept_invitation_full_classroom_rejected(self):
        self.classroom.max_members = 1
        self.classroom.save()
        MemberShip.objects.create(user=self.intruder, classroom=self.classroom, role="STUDENT")
        response = self._accept(self.invited)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self._is_member(self.invited))

    def test_accept_invitation_unauthenticated(self):
        response = self.client.post(self._accept_url(), {"token": self.invitation.token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(self._is_member(self.invited))

