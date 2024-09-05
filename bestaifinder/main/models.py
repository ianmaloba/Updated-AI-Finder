from django.db import models
from django.template.defaultfilters import register
from django.utils.text import slugify
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey

class AITool(models.Model):
    ai_image = models.ImageField(upload_to='images/ai-screenshot/', default='images/default.jpg', blank=True)
    ai_name = models.CharField(max_length=255)
    ai_tool_logo = models.ImageField(upload_to='images/logos/', default='images/default_logo.jpg', blank=True)
    ai_short_description = RichTextUploadingField()
    ai_pricing_tag = models.CharField(max_length=255, db_index=True)
    ai_tags = models.CharField(max_length=255, blank=True, default="", db_index=True)
    ai_tool_link = models.URLField()
    slug = models.SlugField(unique=True, blank=True, null=True, editable=False, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_tools')        
    search_vector = SearchVectorField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    featured_order = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Generate slug only if this is a new object (no slug exists yet)
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        slug = slugify(self.ai_name)
        unique_slug = slug
        num = 1
        while AITool.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{num}"
            num += 1
        return unique_slug

    def __str__(self):
        return f"{self.id}. {self.ai_name}"

    class Meta:
        app_label = 'main'
        indexes = [
            models.Index(fields=['ai_name']),
            models.Index(fields=['ai_pricing_tag']),
            models.Index(fields=['ai_tags']),
            GinIndex(fields=['search_vector']),
            models.Index(fields=['is_featured', 'featured_order']),
        ]

# Avoid recursion by checking if the save was triggered by the signal
@receiver(post_save, sender=AITool)
def update_search_vector(sender, instance, **kwargs):
    # Only update the search_vector if it's not being set from this signal
    if not getattr(instance, '_search_vector_updated', False):
        # Flag to avoid recursion
        instance._search_vector_updated = True
        
        # Update the search_vector field
        instance.search_vector = (
            SearchVector('ai_name', weight='A') +
            SearchVector('ai_short_description', weight='B') +
            SearchVector('ai_tags', weight='C')
        )
        # Save the instance without triggering the signal again
        instance.save(update_fields=['search_vector'])


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

class ToolComment(models.Model):
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tool_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.id}. {self.tool}"

class ToolRating(models.Model):
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tool_ratings')
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.id}. {self.tool}"
    
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.tool.ai_name}"

    class Meta:
        unique_together = ('user', 'tool')