from django.urls import path
from . import views

app_name = 'charts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('track-tool/<slug:slug>/', views.track_tool_visit, name='track_tool'),
    path('tools/', views.tools_chart_view, name='tools_chart_view'),
    path('tools-data/', views.tools_chart_data, name='tools_chart_data'),
    path('transfer-visits/', views.transfer_session_visits, name='transfer_visits'),
]