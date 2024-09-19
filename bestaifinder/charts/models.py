# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ToolVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tool_slug = models.CharField(max_length=255)
    visit_count = models.IntegerField(default=1)
    visit_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.tool_slug} ({self.visit_count} visits on {self.visit_date})"
