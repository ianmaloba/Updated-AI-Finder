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
with open('db.json', 'w', encoding='utf-8') as f:
    # Dump data into the file, ensuring non-ASCII characters are handled
    call_command('dumpdata', '--indent=2', stdout=f)
