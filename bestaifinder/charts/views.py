from django.shortcuts import render, get_object_or_404
from main.models import AITool
from django.db.models import Count, Avg
import random
from django.http import JsonResponse
from .models import ToolVisit
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime

def dashboard(request):
    return render(request, 'charts/dashboard.html')

def track_tool_visit(request, slug):
    tool = get_object_or_404(AITool, slug=slug)
    
    if request.user.is_authenticated:
        tool_visit, created = ToolVisit.objects.get_or_create(
            user=request.user,
            tool_slug=slug,
            visit_date=timezone.now().date()
        )
        if not created:
            tool_visit.visit_count += 1
        else:
            tool_visit.visit_count = 1
        tool_visit.save()
    else:
        if 'tool_visits' not in request.session:
            request.session['tool_visits'] = []
        
        visit = next((v for v in request.session['tool_visits'] if v['slug'] == slug), None)
        if visit:
            visit['visit_count'] += 1
        else:
            request.session['tool_visits'].append({
                'slug': slug,
                'visit_date': str(timezone.now().date()),
                'visit_count': 1
            })
        request.session.modified = True

    return JsonResponse({'status': 'success'})

@login_required
def tools_chart_view(request):
    return render(request, 'charts/tools_chart.html')

@login_required
def tools_chart_data(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date = timezone.now().date()

    tool_visits = ToolVisit.objects.filter(user=request.user, visit_date__range=[start_date, end_date])
    
    tool_data = {}
    for visit in tool_visits:
        if visit.tool_slug in tool_data:
            tool_data[visit.tool_slug] += visit.visit_count
        else:
            tool_data[visit.tool_slug] = visit.visit_count

    return JsonResponse(tool_data)

@login_required
def transfer_session_visits(request):
    if 'tool_visits' in request.session:
        for visit in request.session['tool_visits']:
            tool_visit, created = ToolVisit.objects.get_or_create(
                user=request.user,
                tool_slug=visit['slug'],
                visit_date=datetime.strptime(visit['visit_date'], "%Y-%m-%d").date()
            )
            if not created:
                tool_visit.visit_count += visit['visit_count']
            else:
                tool_visit.visit_count = visit['visit_count']
            tool_visit.save()

        del request.session['tool_visits']
        request.session.modified = True

    return JsonResponse({'status': 'transferred'})

def generate_random_colors(count):
    colors = []
    for _ in range(count):
        color = f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
        colors.append(color)
    return colors