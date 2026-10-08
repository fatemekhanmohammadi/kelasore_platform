from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer


from .permissions import IsQuestionClassroomMember ,IsClassroomMember

#===================================================================================


class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated,IsClassroomMember]

    def get_queryset(self):
       classroom_id=self.kwargs.get('pk')
       return Question.objects.filter(classroom_id=classroom_id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,classroom_id=self.kwargs['pk'])

#===================================================================================

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.select_related("classroom", "user").all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

#===================================================================================

class AnswerListCreateView(generics.ListCreateAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated, IsQuestionClassroomMember]

    def get_queryset(self):
        return Answer.objects.filter(question_id=self.kwargs['question_id'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,question_id=self.kwargs['question_id'])


#==================================================================================


class AnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.select_related("question", "user").all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]