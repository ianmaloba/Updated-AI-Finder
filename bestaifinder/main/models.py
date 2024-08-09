from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

class AITool(models.Model):
    ai_image = models.ImageField(
        upload_to='images/ai-screenshot/',
        default='images/default.jpg'
        )
    ai_name = models.CharField(max_length=255)
    ai_tool_logo = models.ImageField(
        upload_to='images/logos/',
        default='images/default_logo.jpg'
        )
    ai_short_description = models.TextField()
    ai_pricing_tag = models.CharField(max_length=255, db_index=True)
    ai_tags = models.CharField(max_length=255, blank=True, default="", db_index=True)
    ai_tool_link = models.URLField()
    slug = models.SlugField(unique=True, blank=True, null=True, editable=True, db_index=True)
    
    # Add a SearchVectorField for full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    def full_clean(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ai_name)
        super().full_clean(*args, **kwargs)

    def __str__(self):
        return f"{self.id}. {self.ai_name}"

    class Meta:
        app_label = 'main'
        indexes = [
            models.Index(fields=['ai_name']),
            models.Index(fields=['ai_pricing_tag']),
            models.Index(fields=['ai_tags']),
            GinIndex(fields=['search_vector']),
        ]

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]
        
# populate the search_vector field
from django.contrib.postgres.search import SearchVector

def update_search_vector(sender, instance, **kwargs):
    AITool.objects.filter(id=instance.id).update(search_vector=
        SearchVector('ai_name', weight='A') +
        SearchVector('ai_short_description', weight='B') +
        SearchVector('ai_tags', weight='C')
    )

models.signals.post_save.connect(update_search_vector, sender=AITool)