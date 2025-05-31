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
from rest_framework import viewsets
from .models import Account, Category, Transaction
from django.views import View
from django.urls import reverse

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

# Helper to get JWT token from session
def get_token(request):
    return request.session.get('jwt_token')

# Login page override to store JWT in session
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
            request.session['jwt_token'] = token
            return redirect('/api/crud/accounts/')
        else:
            error = response.json().get('detail', 'Invalid credentials')
            return render(request, 'login.html', {'error': error})

# Serializers for CRUD
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['user']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['user']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user']

# CRUD ViewSets (all require authentication)
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

# CRUD UI Views
class AccountListView(View):
    def get(self, request):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(request.build_absolute_uri('/api/accounts/'), headers=headers)
        accounts = resp.json() if resp.status_code == 200 else []
        return render(request, 'accounts_list.html', {'accounts': accounts})

class AccountCreateView(View):
    def get(self, request):
        return render(request, 'account_form.html')
    def post(self, request):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'name': request.POST.get('name'),
            'type': request.POST.get('type'),
            'balance': request.POST.get('balance'),
            'institution': request.POST.get('institution'),
        }
        resp = requests.post(request.build_absolute_uri('/api/accounts/'), json=data, headers=headers)
        if resp.status_code == 201:
            return redirect('/api/crud/accounts/')
        return render(request, 'account_form.html', {'error': resp.text})

class AccountUpdateView(View):
    def get(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(request.build_absolute_uri(f'/api/accounts/{pk}/'), headers=headers)
        account = resp.json() if resp.status_code == 200 else None
        return render(request, 'account_form.html', {'account': account})
    def post(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'name': request.POST.get('name'),
            'type': request.POST.get('type'),
            'balance': request.POST.get('balance'),
            'institution': request.POST.get('institution'),
        }
        resp = requests.put(request.build_absolute_uri(f'/api/accounts/{pk}/'), json=data, headers=headers)
        if resp.status_code in (200, 204):
            return redirect('/api/crud/accounts/')
        return render(request, 'account_form.html', {'error': resp.text, 'account': data})

class AccountDeleteView(View):
    def post(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        requests.delete(request.build_absolute_uri(f'/api/accounts/{pk}/'), headers=headers)
        return redirect('/api/crud/accounts/')

class CategoryListView(View):
    def get(self, request):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(request.build_absolute_uri('/api/categories/'), headers=headers)
        categories = resp.json() if resp.status_code == 200 else []
        return render(request, 'categories_list.html', {'categories': categories})

class CategoryCreateView(View):
    def get(self, request):
        return render(request, 'category_form.html')
    def post(self, request):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'name': request.POST.get('name'),
            'type': request.POST.get('type'),
            'description': request.POST.get('description'),
            'color': request.POST.get('color'),
        }
        resp = requests.post(request.build_absolute_uri('/api/categories/'), json=data, headers=headers)
        if resp.status_code == 201:
            return redirect('/api/crud/categories/')
        return render(request, 'category_form.html', {'error': resp.text})

class CategoryUpdateView(View):
    def get(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(request.build_absolute_uri(f'/api/categories/{pk}/'), headers=headers)
        category = resp.json() if resp.status_code == 200 else None
        return render(request, 'category_form.html', {'category': category})
    def post(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'name': request.POST.get('name'),
            'type': request.POST.get('type'),
            'description': request.POST.get('description'),
            'color': request.POST.get('color'),
        }
        resp = requests.put(request.build_absolute_uri(f'/api/categories/{pk}/'), json=data, headers=headers)
        if resp.status_code in (200, 204):
            return redirect('/api/crud/categories/')
        return render(request, 'category_form.html', {'error': resp.text, 'category': data})

class CategoryDeleteView(View):
    def post(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        requests.delete(request.build_absolute_uri(f'/api/categories/{pk}/'), headers=headers)
        return redirect('/api/crud/categories/')

class TransactionListView(View):
    def get(self, request):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(request.build_absolute_uri('/api/transactions/'), headers=headers)
        transactions = resp.json() if resp.status_code == 200 else []
        return render(request, 'transactions_list.html', {'transactions': transactions})

class TransactionCreateView(View):
    def get(self, request):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        accounts = requests.get(request.build_absolute_uri('/api/accounts/'), headers=headers).json()
        categories = requests.get(request.build_absolute_uri('/api/categories/'), headers=headers).json()
        return render(request, 'transaction_form.html', {'accounts': accounts, 'categories': categories})
    def post(self, request):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'account': request.POST.get('account'),
            'category': request.POST.get('category'),
            'amount': request.POST.get('amount'),
            'date': request.POST.get('date'),
            'description': request.POST.get('description'),
            'is_income': request.POST.get('is_income') == 'on',
        }
        resp = requests.post(request.build_absolute_uri('/api/transactions/'), json=data, headers=headers)
        if resp.status_code == 201:
            return redirect('/api/crud/transactions/')
        accounts = requests.get(request.build_absolute_uri('/api/accounts/'), headers=headers).json()
        categories = requests.get(request.build_absolute_uri('/api/categories/'), headers=headers).json()
        return render(request, 'transaction_form.html', {'error': resp.text, 'accounts': accounts, 'categories': categories})

class TransactionUpdateView(View):
    def get(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        transaction = requests.get(request.build_absolute_uri(f'/api/transactions/{pk}/'), headers=headers).json()
        accounts = requests.get(request.build_absolute_uri('/api/accounts/'), headers=headers).json()
        categories = requests.get(request.build_absolute_uri('/api/categories/'), headers=headers).json()
        return render(request, 'transaction_form.html', {'transaction': transaction, 'accounts': accounts, 'categories': categories})
    def post(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'account': request.POST.get('account'),
            'category': request.POST.get('category'),
            'amount': request.POST.get('amount'),
            'date': request.POST.get('date'),
            'description': request.POST.get('description'),
            'is_income': request.POST.get('is_income') == 'on',
        }
        resp = requests.put(request.build_absolute_uri(f'/api/transactions/{pk}/'), json=data, headers=headers)
        if resp.status_code in (200, 204):
            return redirect('/api/crud/transactions/')
        accounts = requests.get(request.build_absolute_uri('/api/accounts/'), headers=headers).json()
        categories = requests.get(request.build_absolute_uri('/api/categories/'), headers=headers).json()
        return render(request, 'transaction_form.html', {'error': resp.text, 'transaction': data, 'accounts': accounts, 'categories': categories})

class TransactionDeleteView(View):
    def post(self, request, pk):
        token = get_token(request)
        if not token:
            return redirect('/api/login-page/')
        headers = {'Authorization': f'Bearer {token}'}
        requests.delete(request.build_absolute_uri(f'/api/transactions/{pk}/'), headers=headers)
        return redirect('/api/crud/transactions/')
