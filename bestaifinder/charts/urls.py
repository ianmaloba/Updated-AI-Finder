from django.urls import path
from . import views

app_name = 'charts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tools/', views.tools_chart, name='tools_chart'),
    path('categories/', views.categories_chart, name='categories_chart'),
    path('tags/', views.tags_chart, name='tags_chart'),
    path('date_added/', views.date_added_chart, name='date_added_chart'),
]
