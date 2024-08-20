from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, F, Value
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models.functions import Greatest
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .models import AITool, Category
import random

def index(request):
    # Get the search query
    search_query = request.GET.get('search', '').strip()
    
    # Initialize filters
    filters = Q()
    
    # Apply search filter if there is a search query
    if search_query:
        search_vector = (
            SearchVector('ai_name', weight='A') +
            SearchVector('ai_short_description', weight='B') +
            SearchVector('ai_tags', weight='C')
        )
        tools = AITool.objects.annotate(
            search_rank=SearchRank(search_vector, search_query)
        ).filter(
            search_rank__gte=0.1  # Adjust this threshold as needed
        ).order_by('-search_rank')
    else:
        # Get all tools, ordered by ID for pagination
        tools = AITool.objects.all().order_by('-id')
    
    # Pagination
    page_number = request.GET.get('page')
    paginator = Paginator(tools, per_page=9)
    page_obj = paginator.get_page(page_number)

    # Cache random tools selection to avoid repeated sampling
    randomtools = cache.get('randomtools')
    if not randomtools:
        randomtools = random.sample(list(tools), 9)
        cache.set('randomtools', randomtools, timeout=300)  # Cache for 5 minutes

    # Fetch and cache all unique tags
    unique_tags = cache.get('unique_tags')
    if not unique_tags:
        all_tags = tools.values_list('ai_tags', flat=True).distinct()
        unique_tags = set(tag.strip() for tags in all_tags for tag in tags.split(',') if tag.strip() and tag.strip() != "#")
        cache.set('unique_tags', unique_tags, timeout=300)

    # Fetch categories and cache category counts
    categories = Category.objects.all()
    popular_categories = cache.get('popular_categories')
    if not popular_categories:
        category_counts = {category: tools.filter(
            Q(ai_name__icontains=category.name) |
            Q(ai_short_description__icontains=category.name) |
            Q(ai_tags__icontains=category.name)
        ).count() for category in categories}
        popular_categories = sorted(category_counts.items(), key=lambda item: item[1], reverse=True)[:16]
        cache.set('popular_categories', popular_categories, timeout=300)

    # Cache tag counts
    popular_tags = cache.get('popular_tags')
    if not popular_tags:
        tag_counts = {tag: tools.filter(ai_tags__icontains=tag).count() for tag in unique_tags}
        popular_tags = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)[:35]
        cache.set('popular_tags', popular_tags, timeout=300)

    context = {
        "randomtools": randomtools,
        "page_obj": page_obj,
        "tags": unique_tags,
        "elided_page_range": paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1),
        "categories": categories,
        'all_ai_tools_count': tools.count(),
        "popular_categories": popular_categories,
        "popular_tags": popular_tags,
    }
    return render(request, 'index.html', context)


def ai_body(request, slug):
    ai_tool = get_object_or_404(AITool, slug=slug)
    current_tags = [tag.strip() for tag in ai_tool.ai_tags.split(',') if tag.strip() and tag.strip() != "#"]

    related_tools = AITool.objects.exclude(id=ai_tool.id).annotate(
        num_common_tags=Count('ai_tags', filter=Q(ai_tags__icontains=current_tags[0]))
    )
    for tag in current_tags[1:]:
        related_tools = related_tools.annotate(
            num_common_tags=Count('ai_tags', filter=Q(ai_tags__icontains=tag)) + F('num_common_tags')
        )

    related_tools = related_tools.order_by('-num_common_tags')[:9]

    all_ai_tools_count = cache.get_or_set('all_ai_tools_count', AITool.objects.count(), 60 * 15)

    return render(request, 'ai_body.html', {
        'ai_tool': ai_tool,
        'related_tools': related_tools,
        'all_ai_tools_count': all_ai_tools_count,
    })


def search_results(request):
    # Cache key based on the search query and filters
    cache_key = f"search_results_{request.GET.urlencode()}"
    tools = cache.get(cache_key)
    
    if tools is None:
        query_params = request.GET
        search_query = query_params.get('ai_name_contains', '')
        
        filters = Q()
        
        if 'free' in query_params and query_params['free'] == 'true':
            filters &= (
                Q(ai_pricing_tag__icontains='free') |
                Q(ai_pricing_tag__icontains='Pricing Not Specified')
            )

        if search_query:
            search_words = search_query.split()
            search_query_obj = SearchQuery(' '.join(search_words))
            search_vector = (
                SearchVector('ai_name', weight='A') +
                SearchVector('ai_short_description', weight='B') +
                SearchVector('ai_tags', weight='C')
            )
            tools = AITool.objects.annotate(
                search_rank=SearchRank(search_vector, search_query_obj),
                name_similarity=TrigramSimilarity('ai_name', search_query),
                description_similarity=TrigramSimilarity('ai_short_description', search_query),
                tags_similarity=TrigramSimilarity('ai_tags', search_query)
            ).annotate(
                combined_rank=Greatest(
                    F('search_rank'),
                    F('name_similarity') * Value(0.3),
                    F('description_similarity') * Value(0.2),
                    F('tags_similarity') * Value(0.1)
                )
            ).filter(filters).order_by('-combined_rank')
            
        else:
            if 'ai_exact_id' in query_params and query_params['ai_exact_id']:
                filters &= Q(id=query_params['ai_exact_id'])
            if 'ai_short_description__icontains' in query_params and query_params['ai_short_description__icontains']:
                filters &= Q(ai_short_description__icontains=query_params['ai_short_description__icontains'])
            if 'ai_type' in query_params and query_params['ai_type']:
                filters &= (Q(ai_name__icontains=query_params['ai_type']) |
                            Q(ai_short_description__icontains=query_params['ai_type']) |
                            Q(ai_tags__icontains=query_params['ai_type']))

            tools = AITool.objects.filter(filters).order_by('id')
        
        # Cache the full result set
        cache.set(cache_key, tools, 60 * 15)
    
    paginator = Paginator(tools, per_page=9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)
    
    # Cache total tools count if necessary
    all_ai_tools_count = cache.get_or_set('all_ai_tools_count', AITool.objects.count(), 60 * 15)

    context = {
        "randomtools": random.sample(list(AITool.objects.all()), 9),
        "page_obj": page_obj,
        "elided_page_range": elided_page_range,
        "query_params": query_params,
        'all_ai_tools_count': all_ai_tools_count,
    }
    return render(request, 'search_results.html', context)



def tag_list(request, tag_slug):
    tag = tag_slug.replace('-', ' ')
    tools_with_tag = AITool.objects.filter(ai_tags__icontains=tag)
    randomtools = cache.get_or_set('randomtools', random.sample(list(AITool.objects.all()), 9), 60 * 15)
    
    paginator = Paginator(tools_with_tag, per_page=9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)

    all_ai_tools_count = cache.get_or_set('all_ai_tools_count', AITool.objects.count(), 60 * 15)

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
    randomtools = cache.get_or_set('randomtools', random.sample(list(AITool.objects.all()), 9), 60 * 15)
    
    paginator = Paginator(tools, per_page=9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)

    all_ai_tools_count = cache.get_or_set('all_ai_tools_count', AITool.objects.count(), 60 * 15)

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
    # Get all tools, ordered by ID for pagination
    tools = AITool.objects.all().order_by('-id')
    
    # Fetch all categories
    categories = Category.objects.all()
    
    # Fetch the total count of AI tools
    all_ai_tools_count = AITool.objects.count()
    
    context = {
        "categories": categories,
        'all_ai_tools_count': all_ai_tools_count,
        'tools': tools,
    }
    return render(request, 'all_categories_page.html', context)

def get_category_tools(request):
    category_slug = request.GET.get('category_slug')
    category = get_object_or_404(Category, slug=category_slug)
    
    filters = (Q(ai_name__icontains=category.name) | 
               Q(ai_short_description__icontains=category.name) | 
               Q(ai_tags__icontains=category.name))
    tools = AITool.objects.filter(filters).order_by('id')
    
    tools_list = list(tools.values(
        'id', 'ai_name', 'slug', 'ai_short_description', 'ai_pricing_tag', 'ai_tags'
    ))
    
    return JsonResponse({'tools': tools_list})

def all_tags_page(request):
    all_tags = AITool.objects.values_list('ai_tags', flat=True).distinct()
    unique_tags = set(tag.strip() for tags in all_tags for tag in tags.split(',') if tag.strip() and tag.strip() != "#")

    tags_with_tools = {}
    for tag in unique_tags:
        tools_with_tag = AITool.objects.filter(ai_tags__icontains=tag)
        tags_with_tools[tag] = tools_with_tag

    all_ai_tools_count = AITool.objects.count()
        
    context = {
        "tags_with_tools": tags_with_tools,
        "tags": unique_tags,
        'all_ai_tools_count': all_ai_tools_count,
    }
    return render(request, 'all_tags_page.html', context)

def tag_tools_ajax(request):
    tag_slug = request.GET.get('tag_slug')
    if not tag_slug:
        return JsonResponse({'error': 'No tag provided'}, status=400)
    
    tag = tag_slug.replace('-', ' ')
    
    tools = AITool.objects.filter(ai_tags__icontains=tag)
    
    tools_list = [{
        'ai_name': tool.ai_name,
        'slug': tool.slug,
        'ai_short_description': tool.ai_short_description,
        'ai_pricing_tag': tool.ai_pricing_tag,
        'ai_tags': tool.ai_tags,
        'ai_tool_link': tool.ai_tool_link,
        'ai_image_url': tool.ai_image.url if tool.ai_image else '',
        'ai_tool_logo_url': tool.ai_tool_logo.url if tool.ai_tool_logo else '',
    } for tool in tools]
    
    return JsonResponse({'tools': tools_list})

    
def charts(request):
    return render(request, 'charts.html')
    
def google_custom_search(request):
    return render(request, 'google_custom_search.html')

def data_deletion_instructions(request):
    return render(request, 'data_deletion_instructions.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import AIToolForm
import logging

logger = logging.getLogger(__name__)

@login_required
def add_tool(request):
    if request.method == 'POST':
        form = AIToolForm(request.POST, request.FILES)
        if form.is_valid():
            tool = form.save(commit=False)
            # Set the search vector (this will be handled by the signal we already have)
            tool.user = request.user
            tool.save()
            logger.debug(f"Tool '{tool.ai_name}' added by user {request.user.username}")
            return redirect('home')  # or wherever you want to redirect after successful submission
    else:
        form = AIToolForm()
    return render(request, 'add_tool.html', {'form': form})

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def edit_tool(request, tool_id):
    tool = get_object_or_404(AITool, id=tool_id)
    if tool.user != request.user:
        return HttpResponseForbidden("You don't have permission to edit this tool.")
    
    if request.method == 'POST':
        form = AIToolForm(request.POST, request.FILES, instance=tool)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AIToolForm(instance=tool)
    
    return render(request, 'edit_tool.html', {'form': form, 'tool': tool})

@login_required
def delete_tool(request, tool_id):
    tool = get_object_or_404(AITool, id=tool_id)
    if tool.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this tool.")
    
    if request.method == 'POST':
        tool.delete()
        return redirect('home')
    
    return render(request, 'delete_tool_confirm.html', {'tool': tool})