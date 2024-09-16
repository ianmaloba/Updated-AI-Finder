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
        # Only process images if they are new or have been changed
        if self.pk:
            # Fetch the existing instance to compare images
            existing_instance = AITool.objects.get(pk=self.pk)

            # Check if the image or logo has been changed
            if self.ai_image and self.ai_image != existing_instance.ai_image:
                old_image_path = existing_instance.ai_image.path if existing_instance.ai_image else None
                self.ai_image = self.compress_and_rename_image(self.ai_image, max_size=(575, 300), quality=90, img_type="image")
                if old_image_path and os.path.isfile(old_image_path):
                    try:
                        os.remove(old_image_path)
                    except PermissionError:
                        print(f"Permission error deleting old image: {old_image_path}")

            else:
                # If the image is not changed, retain the existing image
                self.ai_image = existing_instance.ai_image

            if self.ai_tool_logo and self.ai_tool_logo != existing_instance.ai_tool_logo:
                old_logo_path = existing_instance.ai_tool_logo.path if existing_instance.ai_tool_logo else None
                self.ai_tool_logo = self.compress_and_rename_image(self.ai_tool_logo, max_size=(250, 250), quality=85, img_type="logo")
                if old_logo_path and os.path.isfile(old_logo_path):
                    try:
                        os.remove(old_logo_path)
                    except PermissionError:
                        print(f"Permission error deleting old logo: {old_logo_path}")

            else:
                # If the logo is not changed, retain the existing logo
                self.ai_tool_logo = existing_instance.ai_tool_logo

        else:
            # For new instances, compress and rename the image
            if self.ai_image:
                self.ai_image = self.compress_and_rename_image(self.ai_image, max_size=(575, 300), quality=90, img_type="image")

            if self.ai_tool_logo:
                self.ai_tool_logo = self.compress_and_rename_image(self.ai_tool_logo, max_size=(250, 250), quality=85, img_type="logo")

        if not self.slug:
            self.slug = self._generate_unique_slug()

        super().save(*args, **kwargs)

    def compress_and_rename_image(self, image_field, max_size, quality, img_type):
        """
        Compress and rename the image by reducing its size and setting a custom file name.
        """
        img = Image.open(image_field)

        # Convert to RGB if the image is in a different mode (PNG with transparency, etc.)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize image if it's larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)  # High-quality downsampling

        # Create a BytesIO buffer to save the new image
        output_io = BytesIO()
        img.save(output_io, format='JPEG', quality=quality)  # Adjust 'quality' to optimize compression

        output_io.seek(0)

        # Generate the new file name using the slug and the image type
        if img_type == "image":
            new_file_name = f"{self.slug}-image.jpg"
        else:
            new_file_name = f"{self.slug}-logo.jpg"

        # Remove the old image file if it exists
        old_file_path = os.path.join(settings.MEDIA_ROOT, image_field.name)
        if os.path.isfile(old_file_path):
            os.remove(old_file_path)

        # Return the compressed image as an InMemoryUploadedFile with the new file name
        return InMemoryUploadedFile(
            output_io,
            'ImageField',
            new_file_name,
            'image/jpeg',
            sys.getsizeof(output_io),
            None
        )

    def clean(self):
        super().clean()
        
        if self.pk:
            old_instance = AITool.objects.get(pk=self.pk)
            
            # Handle ai_image deletion
            if old_instance.ai_image and not self.ai_image:
                # 'clear' checkbox was checked
                if default_storage.exists(old_instance.ai_image.path):
                    default_storage.delete(old_instance.ai_image.path)
                self.ai_image = None
            
            # Handle ai_tool_logo deletion
            if old_instance.ai_tool_logo and not self.ai_tool_logo:
                # 'clear' checkbox was checked
                if default_storage.exists(old_instance.ai_tool_logo.path):
                    default_storage.delete(old_instance.ai_tool_logo.path)
                self.ai_tool_logo = None
                            
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