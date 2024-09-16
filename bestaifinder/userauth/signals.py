from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from main.models import AITool, ToolComment, ToolRating, Bookmark
from .models import UserActivity 

from django.utils import timezone

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
        # Check if this is a genuine edit
        update_fields = kwargs.get('update_fields')
        
        # Log edit if update_fields is None (full save) or contains fields other than 'search_vector'
        if update_fields is None or any(field != 'search_vector' for field in update_fields):
            recent_edit = UserActivity.objects.filter(
                user=instance.user,
                activity_type='edit_tool',
                tool=instance,
                timestamp__gte=timezone.now() - timezone.timedelta(minutes=1)
            ).exists()

            if not recent_edit:
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
