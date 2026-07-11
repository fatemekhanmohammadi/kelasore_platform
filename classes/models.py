from django.db import models
from django.contrib.auth import get_user_model


User=get_user_model()

# Create your models here.
class ClassRoom(models.Model):
    class ClassType(models.TextChoices):
        PUBLIC='PUBLIC','public'
        PRIVATE='PRIVATE','private'
    class SecurityType(models.TextChoices):
        PASSWORD='PASSWORD','password'
        INVITE_ONLY='INVITE_ONLY','invite_only'



    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    max_members=models.PositiveIntegerField(null=True, blank=True)
    classtype=models.CharField(max_length=50, choices=ClassType.choices, default=ClassType.PUBLIC)
    securitytype=models.CharField(max_length=50,choices=SecurityType.choices , null=True, blank=True)
    password=models.CharField(max_length=150, blank=True)
    start_date=models.DateField(null=True, blank=True)
    end_date=models.DateField(null=True, blank=True)
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_classroom')
    created_date=models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.title
    



class MemberShip(models.Model):
    class Role(models.TextChoices):
        STUDENT='STUDENT','student'
        TEACHER='TEACHER','teacher'
        MENTOR='MENTOR','mentor'

    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    classroom=models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='members')
    role=models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)
    joined_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together= ('user', 'classroom')
     


    def __str__(self):
        return f'{self.user}----{self.classroom}--{(self.role)}'





class Invitation(models.Model):
    class Sstatus(models.TextChoices):
         PENDING='PENDING','pending'
         ACCEPT='ACCEPT','accept'
         REJECTED='REJECTED','rejected'
         EXPIRED='EXPIRED','expired'



    classroom=models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='invitation')
    invited_by=models.ForeignKey(User,on_delete=models.CASCADE, related_name='sent_invitation' )
    invited_user=models.ForeignKey(User,on_delete=models.CASCADE, related_name='received_invitation')
    email=models.EmailField(blank=True,null=True)
    token=models.CharField(max_length=225,unique=True)
    status=models.CharField(max_length=20,choices=Sstatus.choices, default=Sstatus.PENDING)
    expires_at=models.DateTimeField()
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"invitation to {self.classroom} {(self.status)}"