from django.contrib import admin

# Register your models here.

from .models import Assignment,Submission,Score,SubCriteria,ActivityBudget


admin.site.register(Assignment)
admin.site.register(Score)
admin.site.register(SubCriteria)
admin.site.register(Submission)
admin.site.register(ActivityBudget)


