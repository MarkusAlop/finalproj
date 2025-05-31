from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, ProtectedView, RegisterPageView, LoginPageView,
    AccountViewSet, CategoryViewSet, TransactionViewSet,
    AccountListView, AccountCreateView, AccountUpdateView, AccountDeleteView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    TransactionListView, TransactionCreateView, TransactionUpdateView, TransactionDeleteView
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('register-page/', RegisterPageView.as_view(), name='register_page'),
    path('login-page/', LoginPageView.as_view(), name='login_page'),
    path('crud/accounts/', AccountListView.as_view(), name='accounts_list'),
    path('crud/accounts/create/', AccountCreateView.as_view(), name='account_create'),
    path('crud/accounts/<int:pk>/edit/', AccountUpdateView.as_view(), name='account_update'),
    path('crud/accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
    path('crud/categories/', CategoryListView.as_view(), name='categories_list'),
    path('crud/categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('crud/categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('crud/categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('crud/transactions/', TransactionListView.as_view(), name='transactions_list'),
    path('crud/transactions/create/', TransactionCreateView.as_view(), name='transaction_create'),
    path('crud/transactions/<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('crud/transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),
]
urlpatterns += router.urls 