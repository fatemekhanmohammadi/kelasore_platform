from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, login_page, register_page, dashboard_page,profile_page , ProfileUpdateView
from . import views

app_name = 'accounts'

urlpatterns = [

    path('', views.login_page, name='home'),
    # API
    path('api/token/', TokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Register API
    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('api/profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('api/profile/', ProfileUpdateView.as_view(), name='profile_api'),

    # HTML pages
    path('login/', login_page, name='login'),
    path('register-page/', register_page, name='register'),
    path('dashboard/', dashboard_page, name='dashboard'),
    path('profile/', profile_page, name='profile'),
]