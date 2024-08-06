import os
import django

# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bestaifinder.settings')
django.setup()

import sqlite3
from django.utils.text import slugify
from main.models import AITool



# Path to your SQLite database
db_path = 'D:/OneDrive - University of the People/Desktop/GITHUB CLONED/Best-AI-Finder/bestaifinder/db.sqlite3'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Clear the slug field for all AITool objects
AITool.objects.update(slug=None)

# Retrieve all AITool objects from the database
tools = AITool.objects.all()

# Generate and save unique slugs for each AITool
for tool in tools:
    # Generate slug based on ai_name
    slug = slugify(tool.ai_name)
    # Check if the generated slug is already used
    if AITool.objects.filter(slug=slug).exists():
        # If slug is already used, append a number to make it unique
        counter = 1
        while True:
            new_slug = f"{slug}-{counter}"
            if not AITool.objects.filter(slug=new_slug).exists():
                slug = new_slug
                break
            counter += 1
    # Assign the unique slug to the AITool object
    tool.slug = slug
    # Save the AITool object
    tool.save()

# Close the connection
conn.close()

print("Slugs updated successfully.")
