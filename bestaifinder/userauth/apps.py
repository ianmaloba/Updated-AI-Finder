# D:\OneDrive - University of the People\Desktop\GITHUB CLONED\Updated-AI-Finder\bestaifinder\userauth\apps.py
from django.apps import AppConfig

class UserauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userauth'

    def ready(self):
        import userauth.signals  # Ensure signals are registered when app is ready
