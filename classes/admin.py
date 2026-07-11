from django.contrib import admin
from .models import ClassRoom, MemberShip, Invitation
# Register your models here.
admin.site.register(ClassRoom)
admin.site.register(MemberShip)
admin.site.register(Invitation)
