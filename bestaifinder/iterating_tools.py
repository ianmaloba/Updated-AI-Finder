import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bestaifinder.settings')

# Configure Django settings
django.setup()

# Now you can access Django settings
from main.models import AITool

# Fetch all AITool objects
all_tools = AITool.objects.all()

# Update image URLs for each AITool
for tool in all_tools:
    if tool.ai_tool_logo:
        tool.ai_tool_logo.name = tool.ai_tool_logo.name.replace('D:/OneDrive - University of the People/Desktop/GITHUB CLONED/Best-AI-Finder/bestaifinder/bestaifinder/media/', '')
        tool.save()
