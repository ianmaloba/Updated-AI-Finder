from django.shortcuts import render, get_object_or_404
from .models import AITool, Category
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
import random
from django.core.cache import cache

def index(request):
    # Get all tools, ordered by ID for pagination
    tools = AITool.objects.all().order_by('-id')

    # Get current page number for pagination
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

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, Q, Value
from django.db.models.functions import Greatest

def search_results(request):
    randomtools = cache.get_or_set('randomtools', random.sample(list(AITool.objects.all()), 9), 60 * 15)
    query_params = request.GET
    search_query = query_params.get('ai_name_contains', '')

    if search_query:
        # Split the search query into words
        search_words = search_query.split()
        
        # Create individual SearchVector for each field
        name_vector = SearchVector('ai_name', weight='A')
        description_vector = SearchVector('ai_short_description', weight='B')
        tags_vector = SearchVector('ai_tags', weight='C')
        
        # Combine vectors
        search_vector = name_vector + description_vector + tags_vector
        
        # Create a SearchQuery that combines all words with OR
        search_query_obj = SearchQuery(search_words[0])
        for word in search_words[1:]:
            search_query_obj |= SearchQuery(word)
        
        # Annotate the queryset with SearchRank and TrigramSimilarity for each field
        tools = AITool.objects.annotate(
            search_rank=SearchRank(search_vector, search_query_obj),
            name_similarity=TrigramSimilarity('ai_name', search_query),
            description_similarity=TrigramSimilarity('ai_short_description', search_query),
            tags_similarity=TrigramSimilarity('ai_tags', search_query)
        ).annotate(
            # Combine SearchRank and weighted TrigramSimilarity
            combined_rank=Greatest(
                F('search_rank'),
                F('name_similarity') * Value(0.3),
                F('description_similarity') * Value(0.2),
                F('tags_similarity') * Value(0.1)
            )
        )

        # Create individual word similarity for multi-word searches
        for word in search_words:
            tools = tools.annotate(**{
                f'name_similarity_{word}': TrigramSimilarity('ai_name', word),
                f'description_similarity_{word}': TrigramSimilarity('ai_short_description', word),
                f'tags_similarity_{word}': TrigramSimilarity('ai_tags', word)
            })

        # Filter based on any match in SearchRank or individual word similarities
        filter_condition = Q(search_rank__gt=0)
        for word in search_words:
            filter_condition |= Q(**{f'name_similarity_{word}__gt': 0.1})
            filter_condition |= Q(**{f'description_similarity_{word}__gt': 0.1})
            filter_condition |= Q(**{f'tags_similarity_{word}__gt': 0.1})

        tools = tools.filter(filter_condition).order_by('-combined_rank')

    else:
        # Your existing filter logic for non-search queries
        filters = Q()
        if 'ai_exact_id' in query_params and query_params['ai_exact_id']:
            filters &= Q(id=query_params['ai_exact_id'])
        if 'ai_short_description__icontains' in query_params and query_params['ai_short_description__icontains']:
            filters &= Q(ai_short_description__icontains=query_params['ai_short_description__icontains'])
        if 'free' in query_params and query_params['free'] == 'true':
            filters &= Q(ai_pricing_tag__icontains='free') | Q(ai_tags__icontains='free')
        if 'ai_type' in query_params and query_params['ai_type']:
            filters &= (Q(ai_name__icontains=query_params['ai_type']) |
                        Q(ai_short_description__icontains=query_params['ai_type']) |
                        Q(ai_tags__icontains=query_params['ai_type']))
        tools = AITool.objects.filter(filters).order_by('id')

    # Pagination logic
    paginator = Paginator(tools, per_page=9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)

    all_ai_tools_count = cache.get_or_set('all_ai_tools_count', AITool.objects.count(), 60 * 15)

    context = {
        "randomtools": randomtools,
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
