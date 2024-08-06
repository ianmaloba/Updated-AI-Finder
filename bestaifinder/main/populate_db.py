# bestaifinder/main/populate_db_from_existing.py
import os
import django
# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bestaifinder.settings')
django.setup()

import sqlite3
from models import AITool

# Connect to the existing SQLite database
conn = sqlite3.connect('D:/OneDrive - University of the People/Desktop/GITHUB CLONED/Best-AI-Finder/bestaifinder/db.sqlite3')
cursor = conn.cursor()

# Fetch data from the existing table
cursor.execute("SELECT * FROM ai_tools")  # Use the correct table name
rows = cursor.fetchall()

# Transfer data to Django models
for row in rows:
    ai_image, ai_name, ai_tool_logo, ai_short_description, ai_pricing_tag, ai_tags, ai_tool_link = row
    AITool.objects.create(
        ai_image=ai_image,
        ai_name=ai_name,
        ai_tool_logo=ai_tool_logo,
        ai_short_description=ai_short_description,
        ai_pricing_tag=ai_pricing_tag,
        ai_tags=ai_tags,
        ai_tool_link=ai_tool_link
    )

conn.close()
