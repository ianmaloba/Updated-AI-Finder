# custom_filters.py
from django import template

register = template.Library()

@register.filter
def split_tags(tags):
    return tags.split(',')
