# Generated by Django 5.0.6 on 2024-08-21 20:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_toolcomment_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toolcomment',
            name='parent',
        ),
    ]
