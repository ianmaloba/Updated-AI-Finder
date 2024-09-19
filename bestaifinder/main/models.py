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

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys, os
from django.core.files.storage import default_storage
from django.conf import settings

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
        # Fetch the existing instance to compare images, if the object exists
        existing_instance = AITool.objects.filter(pk=self.pk).first()

        # Handle ai_image
        if self.ai_image and (not existing_instance or self.ai_image != existing_instance.ai_image):
            # If the current image is not default, compress and rename it
            if self.ai_image.name != 'images/default.jpg':
                self.ai_image = self.compress_and_rename_image(self.ai_image, max_size=(575, 300), quality=90, img_type="image")
            # If the old image is not default and is being replaced, delete the old image
            if existing_instance and existing_instance.ai_image.name != 'images/default.jpg' and existing_instance.ai_image != self.ai_image:
                self.delete_old_image(existing_instance.ai_image)

        # Handle ai_tool_logo
        if self.ai_tool_logo and (not existing_instance or self.ai_tool_logo != existing_instance.ai_tool_logo):
            if self.ai_tool_logo.name != 'images/default_logo.jpg':
                self.ai_tool_logo = self.compress_and_rename_image(self.ai_tool_logo, max_size=(250, 250), quality=85, img_type="logo")
            if existing_instance and existing_instance.ai_tool_logo.name != 'images/default_logo.jpg' and existing_instance.ai_tool_logo != self.ai_tool_logo:
                self.delete_old_image(existing_instance.ai_tool_logo)

        # Generate slug if not present
        if not self.slug:
            self.slug = self._generate_unique_slug()

        super().save(*args, **kwargs)

    def compress_and_rename_image(self, image_field, max_size, quality, img_type):
        """
        Compress and rename the image by reducing its size and setting a custom file name.
        """
        img = Image.open(image_field)

        # Convert to RGB if necessary (for PNG with transparency, etc.)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize image if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Create a BytesIO buffer for the new image
        output_io = BytesIO()
        img.save(output_io, format='JPEG', quality=quality)

        output_io.seek(0)

        # Set the new file name
        new_file_name = f"{self.slug}-{img_type}.jpg"

        return InMemoryUploadedFile(
            output_io,
            'ImageField',
            new_file_name,
            'image/jpeg',
            sys.getsizeof(output_io),
            None
        )

    def delete_old_image(self, image_field):
        """
        Delete the old image if it exists and is not the default.
        """
        if image_field and image_field.name != 'images/default.jpg' and default_storage.exists(image_field.path):
            try:
                default_storage.delete(image_field.path)
            except PermissionError:
                print(f"Permission error deleting image: {image_field.path}")

    def clean(self):
        """
        If the image/logo is cleared, set it back to the default.
        """
        super().clean()
        if self.pk:
            old_instance = AITool.objects.get(pk=self.pk)

            # Handle image clearing
            if not self.ai_image and old_instance.ai_image and old_instance.ai_image.name != 'images/default.jpg':
                self.ai_image = 'images/default.jpg'

            # Handle logo clearing
            if not self.ai_tool_logo and old_instance.ai_tool_logo and old_instance.ai_tool_logo.name != 'images/default_logo.jpg':
                self.ai_tool_logo = 'images/default_logo.jpg'

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