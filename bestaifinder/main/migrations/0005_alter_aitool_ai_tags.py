# Generated by Django 5.0.6 on 2024-06-17 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aitool',
            name='ai_tags',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]