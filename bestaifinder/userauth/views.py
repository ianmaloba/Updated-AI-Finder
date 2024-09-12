from django.contrib.auth.views import PasswordResetView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.db.models import Count
from main.models import AITool, Bookmark
from django.contrib.auth.decorators import login_required

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password-reset/password_reset_form.html'
    email_template_name = 'password-reset/password_reset_email.html'
    subject_template_name = 'password-reset/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Override the send_mail method to use our custom email sending logic.
        """
        current_site = get_current_site(self.request)
        site_name = current_site.name
        domain = current_site.domain
        
        context.update({
            'domain': domain,
            'site_name': site_name,
            'protocol': 'https' if self.request.is_secure() else 'http',
            'static_url': static('images/app-logo/logo2.png'),
        })
        
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        
        html_message = render_to_string(email_template_name, context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )

    def form_valid(self, form):
        """
        Override form_valid to use the default password reset flow.
        """
        return super().form_valid(form)
    
@login_required
def user_dashboard(request):
    user_tools = AITool.objects.filter(user=request.user).order_by('-id')
    context = {
        'user': request.user,
        'user_tools': user_tools,
    }
    return render(request, 'dashboard/home.html', context)



User = get_user_model()

from django.core.paginator import Paginator

def user_list(request):
    users = User.objects.annotate(tool_count=Count('ai_tools')).order_by('-tool_count')
    paginator = Paginator(users, 20)  # Show 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'userauth/user_list.html', context)

from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth import get_user_model


def users_and_tools(request):
    # Get users with their tool counts
    users = User.objects.annotate(tool_count=Count('ai_tools')).order_by('-tool_count')

    # Pagination for users
    user_paginator = Paginator(users, 10)  # Show 10 users per page
    user_page_number = request.GET.get('page')
    user_page_obj = user_paginator.get_page(user_page_number)

    # Prepare tools for each user
    user_tools_pagination = []
    for user in user_page_obj:
        tools = AITool.objects.filter(user=user)
        tool_paginator = Paginator(tools, 100)  # Show 100 tools per user
        tool_page_number = request.GET.get(f'page-{user.id}')
        tool_page_obj = tool_paginator.get_page(tool_page_number)
        user_tools_pagination.append({
            'user': user,
            'tools': tool_page_obj
        })

    context = {
        'user_page_obj': user_page_obj,
        'user_tools_pagination': user_tools_pagination,
    }
    return render(request, 'userauth/users_and_tools.html', context)

# In views.py

from django.shortcuts import render
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from .models import UserActivity

@login_required
def user_activity(request):
    user = request.user
    
    # Get email addresses associated with the user
    email_addresses = EmailAddress.objects.filter(user=user)
    
    # Get social accounts associated with the user
    social_accounts = SocialAccount.objects.filter(user=user)
    
    # Get user activities
    activities = UserActivity.objects.filter(user=user).select_related('tool')[:50]
    
    context = {
        'user': user,
        'email_addresses': email_addresses,
        'social_accounts': social_accounts,
        'activities': activities,
    }
    
    return render(request, 'dashboard/user_activity.html', context)