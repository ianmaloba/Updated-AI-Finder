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

# Dictionary to track unique tool names and their IDs
unique_tools = {}

# Iterate through all tools and store the first occurrence of each tool by name
for tool in all_tools:
    tool_name = tool.ai_name.strip().lower()
    if tool_name not in unique_tools:
        unique_tools[tool_name] = tool.id
    else:
        print(f"Duplicate found and deleted: {tool.ai_name}")
        tool.delete()

print("Completed removing duplicates. Each tool is now unique by name.")
