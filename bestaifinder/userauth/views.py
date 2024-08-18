from django.contrib.auth.views import PasswordResetView
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

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password-reset/password_reset_form.html'
    email_template_name = 'password-reset/password_reset_email.html'
    subject_template_name = 'password-reset/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = self.get_user(email)
        
        if user:
            current_site = get_current_site(self.request)
            site_name = current_site.name
            domain = current_site.domain
            
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if self.request.is_secure() else 'http',
                'static_url': static('images/app-logo/logo2.png'),
            }
            
            subject = render_to_string(self.subject_template_name, context)
            subject = ''.join(subject.splitlines())
            
            html_message = render_to_string(self.email_template_name, context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
        
        return super().form_valid(form)
    
    def get_user(self, email):
        """
        Given an email, return matching user who should receive a reset.
        """
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

from django.shortcuts import render
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

class CustomGoogleOAuth2CallbackView(OAuth2CallbackView):
    def dispatch(self, request, *args, **kwargs):
        if 'code' in request.GET:
            # This means Google has sent the authorization code
            return render(request, 'socialaccount/google_callback.html', {
                'callback_url': request.build_absolute_uri(),
            })
        return super().dispatch(request, *args, **kwargs)

custom_google_callback = CustomGoogleOAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
