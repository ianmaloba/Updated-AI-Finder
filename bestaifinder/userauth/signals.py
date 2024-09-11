# D:\OneDrive - University of the People\Desktop\GITHUB CLONED\Updated-AI-Finder\bestaifinder\userauth\signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from main.models import AITool, ToolComment, ToolRating, Bookmark
from .models import UserActivity  # Assuming UserActivity is in userauth.models

@receiver(post_save, sender=AITool)
def log_tool_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='add_tool',
            description=f"Added tool '{instance.ai_name}'",
            tool=instance
        )
    else:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='edit_tool',
            description=f"Edited tool '{instance.ai_name}'",
            tool=instance
        )

@receiver(post_delete, sender=AITool)
def log_tool_deletion(sender, instance, **kwargs):
    UserActivity.objects.create(
        user=instance.user,
        activity_type='delete_tool',
        description=f"Deleted tool '{instance.ai_name}'",
    )

@receiver(post_save, sender=ToolComment)
def log_comment_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='comment_tool',
            description=f"Commented on tool '{instance.tool.ai_name}'",
            tool=instance.tool
        )

@receiver(post_save, sender=ToolRating)
def log_rating_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='rate_tool',
            description=f"Rated tool '{instance.tool.ai_name}'",
            tool=instance.tool
        )

@receiver(post_save, sender=Bookmark)
def log_bookmark_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='bookmark_tool',
            description=f"Bookmarked tool '{instance.tool.ai_name}'",
            tool=instance.tool
        )

@receiver(post_delete, sender=Bookmark)
def log_remove_bookmark_activity(sender, instance, **kwargs):
    UserActivity.objects.create(
        user=instance.user,
        activity_type='remove_bookmark',
        description=f"Removed bookmark for tool '{instance.tool.ai_name}'",
        tool=instance.tool
    )
