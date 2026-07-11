# accounts/urls.py
from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # ✅ صفحه HTML برای ساخت کلاس
    path('create-page/', views.create_classroom_page, name='create_classroom_page'),
    path('list/', views.list_classrooms_page, name='list'),
    path('detail/<int:pk>/', views.classroom_detail_page, name='detail'),
    
    
    # ✅ API برای ساخت کلاس (که داری)
    path('create/', views.CreateClassroomView.as_view(), name='create-class'),
    path('join/<int:pk>/', views.JoinClassroomView.as_view(), name='join-class'),
    path('list/api/', views.ListClassroomView.as_view(), name='list-api'),
    path('detail/api/<int:pk>/', views.ClassroomDetailView.as_view(), name='detail-api'), 
    path('leave/<int:pk>/', views.LeaveClassroomView.as_view(), name='leave-class'),
    path('invite/<int:pk>/', views.SendInvitationView.as_view(), name='send-invitation'),
    path('invite/accept/', views.AcceptInvitationView.as_view(), name='accept-invitation'),

]