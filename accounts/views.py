from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, ProfileUpdateSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model


User=get_user_model()

# Cre your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]
    

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset=User.objects.all()
    serializer_class=ProfileUpdateSerializer
    

    def get_object(self):
        return self.request.user





def login_page(request):
    return render(request, "accounts/login.html")

def register_page(request):
    return render(request, "accounts/register.html")

def dashboard_page(request):
    return render(request, "accounts/dashboard.html")


def profile_page(request):
    return render(request, "accounts/profile.html")
