from django import template
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def split_tags(tags):
    return tags.split(',')

@register.filter(name='strip_html')
def strip_html_tags(value):
    return strip_tags(value)
