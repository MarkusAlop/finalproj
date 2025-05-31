from django.urls import path
from .views import RegisterView, LoginView, ProtectedView, RegisterPageView, LoginPageView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('register-page/', RegisterPageView.as_view(), name='register_page'),
    path('login-page/', LoginPageView.as_view(), name='login_page'),
] 