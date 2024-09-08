from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView
from .views import user_dashboard
from . import views 

urlpatterns = [
    path('account/', user_dashboard, name='home'),
    path('account/', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password-reset/password_reset_done.html'), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password-reset/password_reset_confirm.html'), 
        name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password-reset/password_reset_complete.html'), 
        name='password_reset_complete'),
    path('accounts/google/login/', TemplateView.as_view(template_name='socialaccount/login.html'), name='google_login'),
    path('user-list/', views.user_list, name='user_list'),
    path('users-tools/', views.users_and_tools, name='users_and_tools'),
]