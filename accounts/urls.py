from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, login_page, register_page, dashboard_page,profile_page , ProfileUpdateView

app_name = 'accounts'

urlpatterns = [
    # API
    path('api/token/', TokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Register API
    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('api/profile/update/', ProfileUpdateView.as_view(), name='profile_update'),

    # HTML pages
    path('login/', login_page, name='login'),
    path('register-page/', register_page, name='register'),
    path('dashboard/', dashboard_page, name='dashboard'),
    path('profile/', profile_page, name='profile'),
]