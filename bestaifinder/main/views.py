from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, F, Value
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models.functions import Greatest
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .models import AITool, Category, Bookmark
import random


from django.db.models.functions import Lower
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch

def custom_elided_page_range(current_page, total_pages, on_each_side=2, on_ends=1):
    if total_pages <= 10:
        return range(1, total_pages + 1)
    
    range_start = max(current_page - on_each_side, 1)
    range_end = min(current_page + on_each_side + 1, total_pages + 1)
    
    if range_start > 2:
        yield 1
        if range_start > 3:
            yield '...'
        elif range_start == 3:
            yield 2
    
    for i in range(range_start, range_end):
        yield i
    
    if range_end < total_pages:
        if range_end < total_pages - 1:
            yield '...'
        elif range_end == total_pages - 1:
            yield total_pages - 1
        yield total_pages

def parse_tags(tag_string):
    return [tag.strip() for tag in tag_string.split(',') if tag.strip() and tag.strip() != "#"]

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator

@require_GET
def fast_pagination(request):
    page_number = request.GET.get('page', '1')
    
    # Fetch only the necessary data for pagination
    tools_queryset = AITool.objects.only('id', 'ai_name', 'ai_short_description', 'ai_pricing_tag', 'ai_tags', 'slug').order_by(F('is_featured').desc(), '-featured_order', '-id')
    
    paginator = Paginator(tools_queryset, per_page=9)
    page_obj = paginator.get_page(page_number)
    
    elided_page_range = custom_elided_page_range(page_obj.number, paginator.num_pages)
    
    tools_html = render_to_string('partials/tools_list.html', {'page_obj': page_obj})
    pagination_html = render_to_string('partials/pagination.html', {
        'page_obj': page_obj,
        'elided_page_range': elided_page_range
    })
    
    return JsonResponse({
        'tools_html': tools_html,
        'pagination_html': pagination_html
    })
    
from django.http import JsonResponse
from django.template.loader import render_to_string

def index(request):
    search_query = request.GET.get('search', '').strip()

    # Use select_related to fetch related fields in a single query
    tools_queryset = AITool.objects.select_related('user').prefetch_related(
        Prefetch('ratings', queryset=ToolRating.objects.only('rating'))
    )

    if search_query:
        tools = tools_queryset.annotate(
            search_rank=SearchRank(F('search_vector'), search_query)
        ).filter(search_rank__gte=0.1).order_by('-search_rank', '-id')
    else:
        tools = tools_queryset.order_by(F('is_featured').desc(), '-featured_order', '-id')

    # Paginate results
    paginator = Paginator(tools, per_page=9)
    page_number = request.GET.get('page', '1')
    page_obj = paginator.get_page(page_number)

    # Use custom elided page range
    elided_page_range = custom_elided_page_range(page_obj.number, paginator.num_pages)

    # Cache random tools
    cache_key = f'randomtools_{page_number}'
    randomtools = cache.get(cache_key)
    if not randomtools:
        all_tools = list(tools[:100])  # Limit to first 100 for better performance
        sample_size = min(len(all_tools), 9)
        randomtools = random.sample(all_tools, sample_size)
        cache.set(cache_key, randomtools, timeout=300)

    # Cache unique tags
    unique_tags = cache.get('unique_tags')
    if not unique_tags:
        all_tags = tools.values_list('ai_tags', flat=True).distinct()[:1000]  # Limit to 1000 most recent
        unique_tags = set()
        for tags in all_tags:
            unique_tags.update(parse_tags(tags))
        cache.set('unique_tags', unique_tags, timeout=3600)  # Cache for 1 hour

    # Cache categories and counts
    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.annotate(tool_count=Count('name')).order_by('-tool_count')[:16]
        cache.set('categories', categories, timeout=3600)

    # Cache popular tags
    popular_tags = cache.get('popular_tags')
    if not popular_tags:
        tag_counts = {}
        for tool in tools[:1000]:  # Limit to 1000 most recent tools for performance
            for tag in parse_tags(tool.ai_tags):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:35]
        cache.set('popular_tags', popular_tags, timeout=3600)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return fast_pagination(request)

    context = {
        "randomtools": randomtools,
        "page_obj": page_obj,
        "tags": unique_tags,
        "elided_page_range": elided_page_range,
        "categories": categories,
        'all_ai_tools_count': tools.count(),
        "popular_tags": popular_tags,
    }
    return render(request, 'index.html', context)
    

from django.shortcuts import redirect
from django.contrib import messages

def ai_body(request, slug):
    ai_tool = get_object_or_404(AITool, slug=slug)
    current_tags = [tag.strip() for tag in ai_tool.ai_tags.split(',') if tag.strip() and tag.strip() != "#"]

    # Handling bookmark logic
    if request.method == 'POST' and 'bookmark' in request.POST:
        if request.user.is_authenticated:
            bookmark, created = Bookmark.objects.get_or_create(user=request.user, tool=ai_tool)
            if not created:
                # Bookmark exists, so remove it
                bookmark.delete()
                messages.success(request, f'{ai_tool.ai_name} removed from bookmarks.')
            else:
                # Bookmark was created (new)
                messages.success(request, f'{ai_tool.ai_name} bookmarked.')
        else:
            return redirect('account_login')

    # Fetching bookmark status
    is_bookmarked = Bookmark.objects.filter(user=request.user, tool=ai_tool).exists() if request.user.is_authenticated else False

    related_tools = AITool.objects.exclude(id=ai_tool.id).annotate(
        num_common_tags=Count('ai_tags', filter=Q(ai_tags__icontains=current_tags[0]))
    )
    for tag in current_tags[1:]:
        related_tools = related_tools.annotate(
            num_common_tags=Count('ai_tags', filter=Q(ai_tags__icontains=tag)) + F('num_common_tags')
        )
    related_tools = related_tools.order_by('-num_common_tags')[:9]

    all_ai_tools_count = cache.get_or_set('all_ai_tools_count', AITool.objects.count(), 60 * 15)

    comment_form = ToolCommentForm()
    rating_form = ToolRatingForm()
    
    all_comments = ai_tool.comments.filter().order_by('-created_at')
    tool_avg_rating = ai_tool.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
    tool_num_ratings = ai_tool.ratings.count()

    if request.user.is_authenticated:
        user_rating = ai_tool.ratings.filter(user=request.user).first()
        user_rating = user_rating.rating if user_rating else None
    else:
        user_rating = None

    context = {
        'ai_tool': ai_tool,
        'current_tags': current_tags,
        'related_tools': related_tools,
        'all_ai_tools_count': all_ai_tools_count,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'all_comments': all_comments,
        'tool_avg_rating': tool_avg_rating,
        'tool_num_ratings': tool_num_ratings,
        'user_rating': user_rating,
        'is_bookmarked': is_bookmarked,  # Pass bookmark status to the template
    }

    return render(request, 'ai_body.html', context)


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
    tools_with_tag = AITool.objects.filter(ai_tags__icontains=tag).order_by('-id')
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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import AITool
from .forms import AIToolForm
from django.contrib import messages

@login_required
def edit_tool(request, tool_id):
    tool = get_object_or_404(AITool, id=tool_id)
    if tool.user != request.user:
        return HttpResponseForbidden("You don't have permission to edit this tool.")
    
    if request.method == 'POST':
        form = AIToolForm(request.POST, request.FILES, instance=tool)
        if form.is_valid():
            form.save()
            messages.success(request, "Tool successfully updated!")
            return redirect('home')
    else:
        initial_data = {'ai_tags': [tag.strip() for tag in tool.ai_tags.split(',') if tag.strip()]}
        form = AIToolForm(instance=tool, initial=initial_data)
    
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


def terms_of_service(request):
    return render(request, 'main/terms_of_service.html')

def privacy_policy(request):
    return render(request, 'main/privacy_policy.html')

def about_developer(request):
    return render(request, 'main/about_developer.html')

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import AITool, ToolComment, ToolRating
from .forms import ToolCommentForm, ToolRatingForm
from django.template.loader import render_to_string
from django.db.models import Avg

from django.utils import timezone

@login_required
def add_comment(request, slug):
    if request.method == 'POST':
        tool = get_object_or_404(AITool, slug=slug)
        form = ToolCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tool = tool
            comment.user = request.user
            comment.save()
            return JsonResponse({
                'success': True,
                'message': 'Comment added successfully.',
                'comment': {
                    'id': comment.id,
                    'text': comment.comment,
                    'user': comment.user.username,
                    'created_at': timezone.localtime(comment.created_at).strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        return JsonResponse({'success': False, 'message': 'Invalid form data.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required
def edit_comment(request, slug, comment_id):
    comment = get_object_or_404(ToolComment, id=comment_id, tool__slug=slug)
    if comment.user != request.user:
        return JsonResponse({'success': False, 'message': 'You are not authorized to edit this comment.'}, status=403)
    
    if request.method == 'GET':
        return JsonResponse({'id': comment.id, 'comment': comment.comment})
    elif request.method == 'POST':
        form = ToolCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Comment updated successfully.'})
        return JsonResponse({'success': False, 'message': 'Invalid form data.'})

@login_required
def delete_comment(request, slug, comment_id):
    comment = get_object_or_404(ToolComment, id=comment_id, tool__slug=slug)
    if comment.user != request.user:
        return JsonResponse({'success': False, 'message': 'You are not authorized to delete this comment.'}, status=403)
    
    if request.method == 'DELETE':
        comment.delete()
        return JsonResponse({'success': True, 'message': 'Comment deleted successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

from django.db.models import Avg
from django.views.decorators.http import require_http_methods
import json

@login_required
@require_http_methods(["POST"])
def add_rating(request, slug):
    tool = get_object_or_404(AITool, slug=slug)
    data = json.loads(request.body)
    rating = data.get('rating')
    
    if not rating or not (1 <= int(rating) <= 5):
        return JsonResponse({'success': False, 'message': 'Invalid rating.'})

    rating_obj, created = ToolRating.objects.update_or_create(
        tool=tool,
        user=request.user,
        defaults={'rating': rating}
    )

    avg_rating = tool.ratings.aggregate(Avg('rating'))['rating__avg']
    num_ratings = tool.ratings.count()

    return JsonResponse({
        'success': True,
        'message': 'Rating added/updated successfully.',
        'avg_rating': avg_rating or 0,
        'num_ratings': num_ratings,
        'user_rating': int(rating)
    })

def get_ratings(request, slug):
    ai_tool = get_object_or_404(AITool, slug=slug)
    tool_avg_rating = ai_tool.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    tool_num_ratings = ai_tool.ratings.count()
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ai_tool.ratings.filter(user=request.user).first()
    return JsonResponse({
        'avg_rating': tool_avg_rating,
        'num_ratings': tool_num_ratings,
        'user_rating': user_rating.rating if user_rating else None
    })
    
def get_comments(request, slug):
    ai_tool = get_object_or_404(AITool, slug=slug)
    all_comments = ai_tool.comments.order_by('-created_at')
    html = render_to_string('includes/comments.html', {'all_comments': all_comments})
    return JsonResponse({'html': html})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Bookmark

# View for listing user's bookmarks
def bookmarks(request):
    if not request.user.is_authenticated:
        return redirect('account_login')  # Redirect to login if the user is not authenticated

    # Fetch bookmarks for the current user
    user_bookmarks = Bookmark.objects.filter(user=request.user).select_related('tool')

    context = {
        'user': request.user,
        'user_bookmarks': user_bookmarks,
    }

    return render(request, 'account/bookmarks.html', context)

from django.shortcuts import get_object_or_404, redirect
from .models import Bookmark

def remove_bookmark(request, bookmark_id):
    if request.method == 'POST':
        bookmark = get_object_or_404(Bookmark, id=bookmark_id, user=request.user)
        bookmark.delete()
        return redirect('bookmarks')
    
    return redirect('bookmarks')

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json

@require_POST
@csrf_exempt
def voice_search(request):
    data = json.loads(request.body)
    query = data.get('query', '')
    
    # Construct the URL for the search results page
    search_url = reverse('search_results') + f'?ai_name_contains={query}'
    
    return JsonResponse({'redirect_url': search_url})

def voice_search_page(request):
    return render(request, 'index.html')


