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

# Correct paths in the image URLs
for tool in all_tools:
    # Normalize ai_image paths
    if tool.ai_image:
        corrected_path = tool.ai_image.name.replace("images//images", "images")
        corrected_path = corrected_path.replace("\\", "/")  # Replace backslashes with forward slashes
        if corrected_path != tool.ai_image.name:
            tool.ai_image.name = corrected_path
            tool.save()
            print(f"Corrected ai_image path for tool: {tool.ai_name}")

    # Normalize ai_tool_logo paths
    if tool.ai_tool_logo:
        corrected_path = tool.ai_tool_logo.name.replace("images//images", "images")
        corrected_path = corrected_path.replace("\\", "/")  # Replace backslashes with forward slashes
        if corrected_path != tool.ai_tool_logo.name:
            tool.ai_tool_logo.name = corrected_path
            tool.save()
            print(f"Corrected ai_tool_logo path for tool: {tool.ai_name}")
