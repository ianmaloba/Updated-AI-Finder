import json
from django.core.management import call_command
from django.core.serializers import serialize
import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bestaifinder.settings')

# Configure Django settings
django.setup()

# Use `open` with utf-8 encoding
with open('new_db.json', 'w', encoding='utf-8') as f:
    # Dump data into the file, excluding auth.permission and contenttypes
    call_command('dumpdata', 
                 exclude=['auth.permission', 'contenttypes'],
                 indent=2, 
                 stdout=f)

print("Data has been dumped to new_db.json")