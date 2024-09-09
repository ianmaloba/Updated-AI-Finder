from django.shortcuts import render
from main.models import AITool, Category
from django.db.models import Count
import random

def dashboard(request):
    return render(request, 'charts/dashboard.html')

def tools_chart(request):
    # Get data for tools
    tools = AITool.objects.all().values('ai_name').annotate(count=Count('id')).order_by('-count')
    tool_names = [tool['ai_name'] for tool in tools]
    tool_counts = [tool['count'] for tool in tools]

    context = {
        'tool_names': tool_names,
        'tool_counts': tool_counts,
        'colors': generate_random_colors(len(tool_names)),
    }
    return render(request, 'charts/tools_chart.html', context)

def categories_chart(request):
    # Get data for categories
    categories = Category.objects.all().annotate(count=Count('ai_tools')).order_by('-count')
    category_names = [category.name for category in categories]
    category_counts = [category.count for category in categories]

    context = {
        'category_names': category_names,
        'category_counts': category_counts,
        'colors': generate_random_colors(len(category_names)),
    }
    return render(request, 'charts/categories_chart.html', context)

def tags_chart(request):
    # Logic to generate chart data for tags (similar to tools and categories)
    return render(request, 'charts/tags_chart.html')

def date_added_chart(request):
    # Logic to generate chart data for date tools were added (line graphs)
    return render(request, 'charts/date_added_chart.html')

def generate_random_colors(count):
    colors = []
    for _ in range(count):
        color = f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
        colors.append(color)
    return colors
