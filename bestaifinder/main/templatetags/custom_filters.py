# File: yourapp/templatetags/custom_filters.py

from django import template
from django.utils.html import strip_tags
import base64

register = template.Library()

@register.filter
def split_tags(tags):
    return tags.split(',')

@register.filter(name='strip_html')
def strip_html_tags(value):
    return strip_tags(value)

@register.filter(name='obfuscate_url')
def obfuscate_url(url):
    return base64.b64encode(url.encode()).decode()