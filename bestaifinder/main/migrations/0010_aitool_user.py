# Generated by Django 5.0.6 on 2024-08-20 04:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_aitool_ai_image_alter_aitool_ai_tool_logo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='aitool',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ai_tools', to=settings.AUTH_USER_MODEL),
        ),
    ]
