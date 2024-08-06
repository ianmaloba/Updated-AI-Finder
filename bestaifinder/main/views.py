from django.shortcuts import render, get_object_or_404
from .models import AITool, Category
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
import random

def index(request):
    tools = AITool.objects.all().order_by('-id')
    randomtools = random.sample(list(AITool.objects.all()), 9)
    paginator = Paginator(tools, per_page=9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch all unique tags from all AITool objects
    all_tags = AITool.objects.values_list('ai_tags', flat=True).distinct()
    
    # Split and flatten the tags list, ensuring tags are valid
    unique_tags = set(tag.strip() for tags in all_tags for tag in tags.split(',') if tag.strip() and tag.strip() != "#")

    # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()
    
    # Calculating the elided page range
    elided_page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)
    
    # Fetch categories from the database
    categories = Category.objects.all()
    
    # Calculate the number of tools associated with each category
    category_counts = {}
    for category in categories:
        filters = (Q(ai_name__icontains=category.name) | 
                   Q(ai_short_description__icontains=category.name) | 
                   Q(ai_tags__icontains=category.name))
        tools_count = AITool.objects.filter(filters).count()
        category_counts[category] = tools_count
    
    # Get the top 16 categories with the most tools
    popular_categories = sorted(category_counts.items(), key=lambda item: item[1], reverse=True)[:16]

    # Calculate the number of tools associated with each tag
    tag_counts = {}
    for tag in unique_tags:
        tools_count = AITool.objects.filter(ai_tags__icontains=tag).count()
        tag_counts[tag] = tools_count
    
    # Get the top 35 tags with the most tools
    popular_tags = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)[:35]

    context = {
        "randomtools": randomtools,
        "page_obj": page_obj,
        "tags": unique_tags,
        "elided_page_range": elided_page_range,
        "categories": categories,
        'all_ai_tools_count': all_ai_tools_count,
        "popular_categories": popular_categories,
        "popular_tags": popular_tags,
    }
    return render(request, 'index.html', context)


def ai_body(request, slug):
    ai_tool = get_object_or_404(AITool, slug=slug)

    # Get the list of tags for the current AI tool
    current_tags = ai_tool.ai_tags.split(',')
    
    # Filter out invalid tags
    current_tags = [tag for tag in current_tags if tag.strip() and tag.strip() != "#"]
    
    # Query related tools based on tags
    related_tools = AITool.objects.exclude(id=ai_tool.id).annotate(
        num_common_tags=Count('ai_tags', filter=Q(ai_tags__icontains=current_tags[0]))
    )
    for tag in current_tags[1:]:
        related_tools = related_tools.annotate(
            num_common_tags=Count('ai_tags', filter=Q(ai_tags__icontains=tag)) + F('num_common_tags')
        )
    
    # Order related tools by the number of common tags
    related_tools = related_tools.order_by('-num_common_tags')[:9]  # Get top All related tools
    
    # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()
    
    return render(request, 'ai_body.html', {
        'ai_tool': ai_tool,
        'related_tools': related_tools,
        'all_ai_tools_count': all_ai_tools_count,
    })


def search_results(request):
    randomtools = random.sample(list(AITool.objects.all()), 9) # if no tool found
    query_params = request.GET
    filters = Q()

    if 'ai_name_contains' in query_params and query_params['ai_name_contains']:
        filters &= Q(ai_name__icontains=query_params['ai_name_contains'])
    if 'ai_exact_id' in query_params and query_params['ai_exact_id']:
        filters &= Q(id=query_params['ai_exact_id'])
    if 'ai_short_description__icontains' in query_params and query_params['ai_short_description__icontains']:
        filters &= Q(ai_short_description__icontains=query_params['ai_short_description__icontains'])
    if 'free' in query_params and query_params['free'] == 'true':
        filters &= Q(ai_pricing_tag__icontains='free') | Q(ai_tags__icontains='free')
    #if 'date_min' in query_params and query_params['date_min']:
    #    filters['date_founded__gte'] = query_params['date_min']
    if 'ai_type' in query_params and query_params['ai_type']:
        ai_type = query_params['ai_type']
        filters &= (Q(ai_name__icontains=ai_type) | 
                    Q(ai_short_description__icontains=ai_type) | 
                    Q(ai_tags__icontains=ai_type))

    tools = AITool.objects.filter(filters).order_by('id')
    paginator = Paginator(tools, per_page=9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)
    
    # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()

    context = {
        "randomtools": randomtools,
        "page_obj": page_obj,
        "elided_page_range": elided_page_range,
        "query_params": query_params,
        'all_ai_tools_count': all_ai_tools_count,
    }
    return render(request, 'search_results.html', context)


def tag_list(request, tag_slug):
    # Get the tag name from the slug
    tag = tag_slug.replace('-', ' ')  # Revert slug back to tag name
    tools_with_tag = AITool.objects.filter(ai_tags__icontains=tag)
    randomtools = random.sample(list(AITool.objects.all()), 9) # If no tool associated
    
    paginator = Paginator(tools_with_tag, per_page=9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)

    # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()
    
    context = {
        "randomtools": randomtools,
        "page_obj": page_obj,
        "elided_page_range": elided_page_range,
        'tag': tag,
        'tools_with_tag': tools_with_tag,
        'all_ai_tools_count': all_ai_tools_count,
    }
    return render(request, 'tag_list.html', context)


def category_tools(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    filters = (Q(ai_name__icontains=category.name) | 
               Q(ai_short_description__icontains=category.name) | 
               Q(ai_tags__icontains=category.name))
    tools = AITool.objects.filter(filters).order_by('id')
    randomtools = random.sample(list(AITool.objects.all()), 9)  # if no tool found
    
    paginator = Paginator(tools, per_page=9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)

    # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()
    
    context = {
        "category": category.name,
        "page_obj": page_obj,
        "randomtools": randomtools,
        "elided_page_range": elided_page_range,
        'all_ai_tools_count': all_ai_tools_count,
    }
    return render(request, 'category_tools.html', context)


def about(request):
     # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()   
    
    context = {
        'all_ai_tools_count': all_ai_tools_count,
    }
    
    return render(request, 'about.html', context)


def all_categories_page(request):
    # Fetch all categories
    categories = Category.objects.all()
    
    # Create a dictionary to store tools associated with each category and their counts
    categories_with_tools = {}
    for category in categories:
        filters = (Q(ai_name__icontains=category.name) | 
                   Q(ai_short_description__icontains=category.name) | 
                   Q(ai_tags__icontains=category.name))
        tools = AITool.objects.filter(filters).order_by('id')
        categories_with_tools[category] = tools
    
    # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()
        
    context = {
        "categories_with_tools": categories_with_tools,
        'all_ai_tools_count': all_ai_tools_count,
    }
    return render(request, 'all_categories_page.html', context)


def all_tags_page(request):
    # Fetch all unique tags from all AITool objects
    all_tags = AITool.objects.values_list('ai_tags', flat=True).distinct()
    
    # Split and flatten the tags list, ensuring tags are valid
    unique_tags = set(tag.strip() for tags in all_tags for tag in tags.split(',') if tag.strip() and tag.strip() != "#")

    # Create a dictionary to store tools associated with each tag
    tags_with_tools = {}
    for tag in unique_tags:
        tools_with_tag = AITool.objects.filter(ai_tags__icontains=tag)
        tags_with_tools[tag] = tools_with_tag

    # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()
        
    context = {
        "tags_with_tools": tags_with_tools,
        "tags": unique_tags,
        'all_ai_tools_count': all_ai_tools_count,
    }
    return render(request, 'all_tags_page.html', context)

    
def charts(request):
    return render(request, 'charts.html')
    
def google_custom_search(request):
    return render(request, 'google_custom_search.html')
