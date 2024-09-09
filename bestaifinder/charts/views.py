from django.shortcuts import render
from main.models import AITool, Category
from django.db.models import Count, Avg
import random
from django.http import JsonResponse

def dashboard(request):
    return render(request, 'charts/dashboard.html')

def tools_data(request):
    filter_criteria = request.GET.get('filter', 'most_popular')
    
    if filter_criteria == 'most_popular':
        tools = AITool.objects.annotate(count=Count('bookmarked_by')).order_by('-count')[:10]
    elif filter_criteria == 'highest_rated':
        tools = AITool.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:10]
    elif filter_criteria == 'recently_added':
        tools = AITool.objects.order_by('-id')[:10]
    else:
        return JsonResponse({'error': 'Invalid filter'}, status=400)

    tool_names = [tool.ai_name for tool in tools]
    tool_counts = [tool.count if hasattr(tool, 'count') else (tool.avg_rating if hasattr(tool, 'avg_rating') else tool.id) for tool in tools]

    return JsonResponse({
        'tool_names': tool_names,
        'tool_counts': tool_counts,
    })

def tools_chart(request):
    return render(request, 'charts/tools_chart.html')

def generate_random_color():
    return f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'

def generate_random_colors(count):
    return [generate_random_color() for _ in range(count)]

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
