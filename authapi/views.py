from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import requests
from django.conf import settings

# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=make_password(validated_data['password'])
        )
        return user

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# JWT login view (using SimpleJWT's TokenObtainPairView)
class LoginView(TokenObtainPairView):
    pass

# Protected route example
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': f'Hello, {request.user.username}! This is a protected route.'})

# HTML Registration View
@method_decorator(csrf_exempt, name='dispatch')
class RegisterPageView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.data.get('username') or request.POST.get('username')
        email = request.data.get('email') or request.POST.get('email')
        password = request.data.get('password') or request.POST.get('password')
        data = {'username': username, 'email': email, 'password': password}
        # Use internal API call
        response = requests.post(request.build_absolute_uri('/api/register/'), data=data)
        if response.status_code == 201:
            return render(request, 'register.html', {'message': 'Registration successful! Please log in.'})
        else:
            error = response.json()
            return render(request, 'register.html', {'error': error})

# HTML Login View
@method_decorator(csrf_exempt, name='dispatch')
class LoginPageView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.data.get('username') or request.POST.get('username')
        password = request.data.get('password') or request.POST.get('password')
        data = {'username': username, 'password': password}
        response = requests.post(request.build_absolute_uri('/api/login/'), data=data)
        if response.status_code == 200:
            token = response.json().get('access')
            return render(request, 'login.html', {'token': token})
        else:
            error = response.json().get('detail', 'Invalid credentials')
            return render(request, 'login.html', {'error': error})
