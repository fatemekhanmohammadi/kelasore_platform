from rest_framework import serializers
from django.contrib.auth import get_user_model
from classes.models import ClassRoom, MemberShip
from .models import Assignment, Submission,SubCriteria,Score,ActivityBudget
User = get_user_model()

#================================================================================================

class AssignmentSerializer(serializers.ModelSerializer):
   class Meta:
      model=Assignment
      fields='__all__'
      read_only_fields=['created_by','classroom']

#================================================================================================


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model=Assignment
        fields=['assignment_type','title','description','classroom','score',
         'deadline','submission_limit','answer_type','created_by','late_penalty','save_to_bank']  
        read_only_fields=['created_by','classroom']


#================================================================================================


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
     model=Submission
     fields=["id","user","group","assignment","text","file","submitted_at"]
     read_only_fields=['submitted_at','user']


#================================================================================================

class ScoreSerializer(serializers.ModelSerializer):
    assignment_title = serializers.SerializerMethodField()
    scored_by = serializers.SerializerMethodField()
    penalty = serializers.SerializerMethodField()
    subcriteria = serializers.SerializerMethodField()

    class Meta:
        model = Score
        fields = ['id', 'submission', 'score', 'scored_at', 'feedback', 
                  'assignment_title', 'scored_by', 'penalty', 'subcriteria']

    def get_assignment_title(self, obj):
        return obj.submission.assignment.title

    def get_scored_by(self, obj):
        return obj.scored.get_full_name() or obj.scored.username

    def get_penalty(self, obj):
        return obj.submission.penalty

    def get_subcriteria(self, obj):
        assignment = obj.submission.assignment
        subcriteria = SubCriteria.objects.filter(assignment=assignment)
        return [{'title': s.title, 'max_score': float(s.max_score)}for s in subcriteria]

#================================================================================================

class SubCriteriaSerializer(serializers.ModelSerializer):
   class Meta:
     model=SubCriteria
     fields=["id","assignment","title","max_score"]


#================================================================================================

class ActivityBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityBudget
        fields = ['id', 'classroom', 'activity_type', 'max_score', 'created_by',]
        read_only_fields = ['created_by',]


#================================================================================================
