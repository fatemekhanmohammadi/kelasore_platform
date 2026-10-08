from django.urls import path
from . import views



app_name = 'forum'
urlpatterns = [
    path("questions/class/<int:pk>/", views.QuestionListCreateView.as_view(), name="question-list"),
    path("questions/<int:pk>/", views.QuestionDetailView.as_view(), name="question-detail"),

    path("questions/<int:question_id>/answers/", views.AnswerListCreateView.as_view(), name="answer-list"),
    path("answers/<int:pk>/", views.AnswerDetailView.as_view(), name="answer-detail"),
]