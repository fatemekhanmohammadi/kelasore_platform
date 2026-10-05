from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, ProfileUpdateSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

User=get_user_model()

#====================================================================
@extend_schema(tags=['accounts'])

class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]
    
#====================================================================
@extend_schema(tags=['accounts'])

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset=User.objects.all()
    serializer_class=ProfileUpdateSerializer
    permission_classes=[permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

#=====================================================================

@extend_schema(tags=['accounts'])
class MyTokenObtainPairView(TokenObtainPairView):
    pass
#=====================================================================
@extend_schema(tags=['accounts'])
class MyTokenRefreshView(TokenRefreshView):
    pass

#=====================================================================




