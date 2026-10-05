from django.db import models
from django.utils import timezone
from classes.models import ClassRoom, MemberShip
from accounts.models import User



#============================================================================================

class Group(models.Model):
    name = models.CharField(max_length=100)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='groups')
    members = models.ManyToManyField(MemberShip, related_name='groups', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

#============================================================================================