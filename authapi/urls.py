from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, ProtectedView, RegisterPageView, LoginPageView, AuthorViewSet, PublisherViewSet, BookViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'publishers', PublisherViewSet, basename='publisher')
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('register-page/', RegisterPageView.as_view(), name='register_page'),
    path('login-page/', LoginPageView.as_view(), name='login_page'),
]
urlpatterns += router.urls 