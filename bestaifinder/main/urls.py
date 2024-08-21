# bestaifinder/main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ai-tool/<slug:slug>/', views.ai_body, name='ai_body'),
    path('search/', views.search_results, name='search_results'),
    path('about/', views.about, name='about'),
    path('tags/<slug:tag_slug>/', views.tag_list, name='tag_list'),
    path('category/<slug:category_slug>/', views.category_tools, name='category_tools'),
    path('all-categories', views.all_categories_page, name='all_categories_page'),
    path('category-tools/', views.get_category_tools, name='get_category_tools'),
    path('all-tags', views.all_tags_page, name='all_tags_page'),
    path('tag-tools/', views.tag_tools_ajax, name='tag_tools_ajax'),
    path('charts', views.charts, name='charts'),
    path('google-custom-search', views.google_custom_search, name='google_custom_search'),
    path('data-deletion-instructions', views.data_deletion_instructions, name='data_deletion_instructions'),
    path('add-tool/', views.add_tool, name='add_tool'),
    path('edit-tool/<int:tool_id>/', views.edit_tool, name='edit_tool'),
    path('delete-tool/<int:tool_id>/', views.delete_tool, name='delete_tool'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('about-developer/', views.about_developer, name='about_developer'),
]
