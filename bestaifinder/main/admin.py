from django.contrib import admin
from .models import AITool
from .models import Category, ToolComment, ToolRating

admin.site.register(AITool)
admin.site.register(Category)
admin.site.register(ToolComment)
admin.site.register(ToolRating)