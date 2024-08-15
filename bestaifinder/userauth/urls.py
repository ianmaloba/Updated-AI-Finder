# bestaifinder/userauth/urls.py
from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('account/', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
]
