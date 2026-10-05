from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileUpdateView , MyTokenObtainPairView,MyTokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [

  
    # API
    path('api/token/', MyTokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),

    # Register API
    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('api/profile/', ProfileUpdateView.as_view(), name='profile_api'),
]