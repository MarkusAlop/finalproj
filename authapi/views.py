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
from django.core.cache import cache
from functools import wraps
from rest_framework.exceptions import Throttled
from rest_framework import status as drf_status

# Custom rate limiting decorator
# Example: @rate_limit(key_func, limit=5, period=60)
def rate_limit(key_func=None, limit=5, period=60):
    """
    Rate limit decorator for Django views.
    :param key_func: function(request) -> str, unique key per user/IP
    :param limit: max requests
    :param period: seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Use user id if authenticated, else IP
            if key_func:
                key = key_func(request)
            else:
                if hasattr(request, 'user') and request.user.is_authenticated:
                    key = f"rl:{request.user.id}"
                else:
                    ip = request.META.get('REMOTE_ADDR', 'anon')
                    key = f"rl:ip:{ip}"
            count = cache.get(key, 0)
            if count >= limit:
                resp = Response({
                    'detail': f'Rate limit exceeded. Max {limit} requests per {period} seconds.'
                }, status=429)
                return resp
            else:
                cache.set(key, count + 1, timeout=period)
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

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
    @method_decorator(rate_limit(limit=10, period=60))
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# JWT login view (using SimpleJWT's TokenObtainPairView)
class LoginView(TokenObtainPairView):
    @method_decorator(rate_limit(limit=10, period=60))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# Protected route example
class ProtectedView(APIView):
    """
    GET /api/protected/
    Protected route. Requires JWT authentication. Rate limited to 5 requests per minute.
    Response: {"message": "Hello, <username>! This is a protected route."}
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(rate_limit(limit=5, period=60))
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

    @method_decorator(rate_limit(limit=10, period=60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(rate_limit(limit=10, period=60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(rate_limit(limit=10, period=60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @method_decorator(rate_limit(limit=10, period=60))
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

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
