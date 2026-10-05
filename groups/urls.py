from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
   
    path('list/<int:pk>/', views.GroupListView.as_view(), name='group-list'),
    path('group/create/<int:class_id>/', views.GroupCreateAPIView.as_view(), name='create_group'),
    path('group/auto/<int:pk>/', views.CreateAutoGroupView.as_view(), name='group-auto'),  # ← خودکار
]