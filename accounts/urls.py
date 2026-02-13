from django.urls import path
from .views import ProfileView  # 작성한 뷰 임포트
from django.views.generic import TemplateView
from .views import ResendVerificationEmailView
from .views import ProfileUpdateView
from .views import EmailChangeView

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path("resend-email/", ResendVerificationEmailView.as_view(), name="resend-email"),
    path('email-sent/', TemplateView.as_view(template_name="account/email_sent.html"), name='email_sent_page'),
    path('email-confirmation-done/', TemplateView.as_view(template_name="account/email_confirm_done.html"), name='account_email_confirmation_done'),
    path("email/change/", EmailChangeView.as_view(), name="email_change_custom"),
]