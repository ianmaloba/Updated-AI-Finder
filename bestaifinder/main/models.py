from django.db import models
from django.utils.text import slugify

class AITool(models.Model):
    ai_image = models.ImageField(upload_to='images/ai-screenshot/')
    ai_name = models.CharField(max_length=255)
    ai_tool_logo = models.ImageField(upload_to='images/logos/')
    ai_short_description = models.TextField()
    ai_pricing_tag = models.CharField(max_length=255)
    ai_tags = models.CharField(max_length=255, blank=True, default="")
    ai_tool_link = models.URLField()
    slug = models.SlugField(unique=True, blank=True, null=True, editable=False)
    
    def full_clean(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ai_name)
        super().full_clean(*args, **kwargs)

    def __str__(self):
        return f"{self.id}. {self.ai_name}"
    
    class Meta:
        app_label = 'main'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name