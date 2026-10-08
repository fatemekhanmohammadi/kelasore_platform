
from rest_framework import serializers
from .models import Question, Answer





#===================================================================================================================
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id","classroom","user","title","body","created_at",]
        read_only_fields = ["id", "user", "created_at"]

#===================================================================================================================
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id","question","user","body","created_at",]
        read_only_fields = ["id", "user", "created_at"]