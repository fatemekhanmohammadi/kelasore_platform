from django.db import models
from accounts.models import User
from classes.models import ClassRoom

#===================================================================================================================


class Question(models.Model):
    classroom = models.ForeignKey(ClassRoom,on_delete=models.CASCADE,related_name="questions")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="questions")
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.title

#===================================================================================================================

class Answer(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name="answers")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="answers")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Answer by {self.user.username}"