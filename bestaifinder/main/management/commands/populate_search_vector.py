from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from main.models import AITool  # Adjust the import based on your app name

import os
import django

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bestaifinder.settings')
django.setup()

class Command(BaseCommand):
    help = 'Populate search_vector field for all AITool entries'

    def handle(self, *args, **kwargs):
        tools = AITool.objects.all()
        for tool in tools:
            tool.search_vector = (
                SearchVector('ai_name', weight='A') +
                SearchVector('ai_short_description', weight='B') +
                SearchVector('ai_tags', weight='C')
            )
            tool.save(update_fields=['search_vector'])
        self.stdout.write(self.style.SUCCESS('Successfully populated search_vector field for all AITool entries'))
