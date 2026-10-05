from django.db import models
from classes.models import ClassRoom,MemberShip
from accounts.models import User

#================================================================================================
class Assignment(models.Model):
    class AnswerType(models.TextChoices):
                TEXT='TEXT','text'
                FILE='FILE','file'
                CODE='CODE','code'
    class AssignmentType(models.TextChoices):
                 INDIVIDUAL = 'INDIVIDUAL', 'individual'
                 GROUP = 'GROUP', 'group'

    assignment_type = models.CharField(max_length=20, choices=AssignmentType.choices, default=AssignmentType.INDIVIDUAL)
    title =models.CharField(max_length=220)
    description=models.TextField(blank=True)
    classroom=models.ForeignKey(ClassRoom, on_delete=models.CASCADE,related_name='assignments')
    score=models.DecimalField(max_digits=6,decimal_places=2)
    deadline=models.DateTimeField()
    submission_limit=models.PositiveIntegerField(default=1)
    answer_type=models.CharField(max_length=20, choices=AnswerType.choices)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE, related_name='assignments')
    late_penalty=models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    save_to_bank=models.BooleanField(default=False)

    def __str__(self):
            return self.title

#================================================================================================

class Submission(models.Model):
        user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
        group=models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name="submissions", blank=True,null=True)
        assignment=models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
        text=models.TextField(blank=True)
        file=models.FileField(upload_to='submission/files', blank=True,null=True)
        submitted_at=models.DateTimeField(auto_now_add=True)
        penalty = models.DecimalField(max_digits=5, decimal_places=2, default=0)
        final_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

        def __str__(self):
            return f"{self.user}{self.assignment}"
#================================================================================================

class Score(models.Model):
        submission=models.ForeignKey(Submission,on_delete=models.CASCADE,related_name="scores")
        scored=models.ForeignKey(User,on_delete=models.CASCADE, related_name="scored_submissions")
        score=models.DecimalField(max_digits=6,decimal_places=2)
        scored_at=models.DateTimeField(auto_now=True)
        feedback=models.TextField(blank=True)
        member=models.ForeignKey(MemberShip,blank=True,null=True,on_delete=models.SET_NULL,related_name='individyal_scores')

        def __str__(self):
                return f"score for {self.submission}"

#================================================================================================

class SubCriteria(models.Model):
        assignment=models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="subcriterias")
        title=models.CharField(max_length=200)
        max_score=models.DecimalField(max_digits=6,decimal_places=2)
        def __str__(self):
                return self.title

#================================================================================================

class ActivityBudget(models.Model):
        class ActivityType(models.TextChoices):
                WEEKLY='WEEKLY','weekly' #تمرین هفتگی 
                QUIZ='QUIZ','quiz'   # کوییز
                PROJECT='PROJECT','project'   # پروژه
        classroom=models.ForeignKey(ClassRoom,on_delete=models.CASCADE, related_name='class_activity')
        activity_type=models.CharField(max_length=50, choices=ActivityType.choices, default=ActivityType.WEEKLY)
        max_score=models.DecimalField(max_digits=6,decimal_places=2)
        created_by=models. ForeignKey(User,on_delete=models.CASCADE,related_name='created_by')
        def __str__(self):
                return self.classroom

#================================================================================================
       