# bestaifinder/main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ai-tool/<slug:slug>/', views.ai_body, name='ai_body'),
    path('search/', views.search_results, name='search_results'),
    path('tags/<slug:tag_slug>/', views.tag_list, name='tag_list'),
    path('category/<slug:category_slug>/', views.category_tools, name='category_tools'),
    path('about', views.about, name='about'),
    path('all-categories', views.all_categories_page, name='all_categories_page'),
    path('all-tags', views.all_tags_page, name='all_tags_page'),
    path('charts', views.charts, name='charts'),
    path('google-custom-search', views.google_custom_search, name='google_custom_search'),
]
