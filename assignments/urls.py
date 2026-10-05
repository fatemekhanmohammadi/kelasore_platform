# accounts/urls.py
from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
  
   path('bank/reuse/<int:pk>/', views.ReuseAssignmentView.as_view(), name='bank-reuse'),
   path('submit/<int:pk>/', views.SubmitAnswerView.as_view(), name='submit'),
   path('score/<int:pk>/', views.ScoreView.as_view(), name='score'),
   path('subcriteria/<int:pk>/', views.SubCriteriaView.as_view(), name='sub-criteria'),
   path('activity/<int:pk>/', views.ActivityBudgetView.as_view(), name='activitybudget'),
   path('create/assignment/<int:pk>', views.CreateAssignmentView.as_view(), name='createassignment'),
   path('list/<int:pk>/', views.ClassAssignmentListView.as_view(), name='class-assignment-list'),
   path('bank/', views.BankListView.as_view(), name='bank-list'),  # ← بانک سوالات
   path('detail/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment-detail'),
   path('submissions/list/<int:pk>/', views.AssignmentSubmissionsListView.as_view(), name='submissions-list'),
   path('submissions/user/<int:pk>/', views.UserSubmissionsView.as_view(), name='user-submissions'),
   path('my-grades/', views.MyGradesView.as_view(), name='my-grades'),
   path('budget/<int:pk>/', views.BudgetListView.as_view(), name='budget-list'),
   path('grade-table/<int:pk>/', views.ClassGradeTableView.as_view(), name='grade-table'),
  path('student-activity/<int:class_id>/<int:student_id>/',views.StudentActivityView.as_view(),name='student-activity')



]