from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username