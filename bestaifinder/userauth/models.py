# userauth/models.py
from django.db import models
from django.contrib.auth.models import User
from main.models import AITool, ToolComment, ToolRating, Bookmark  # Import from main

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    tool = models.ForeignKey(AITool, on_delete=models.SET_NULL, null=True, blank=True)  # Correct reference to AITool
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
