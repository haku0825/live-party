from django.views.generic import TemplateView, View  # ✅ View 추가
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from allauth.account.models import EmailAddress
from parties.models import PartyMember

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "account/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_matches'] = PartyMember.objects.filter(user=self.request.user) \
                                    .select_related('party__game') \
                                    .order_by('-joined_at')[:5]
        return context

# ✅ [수정] 클래스 기반 뷰(CBV)로 변경
class ResendVerificationEmailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        email_obj = EmailAddress.objects.filter(user=request.user, primary=True).first()
        
        if email_obj and not email_obj.verified:
            # 모델 메서드로 메일 발송
            email_obj.send_confirmation(request)
            
        # ✅ [2] 수정 포인트: 'account/email_sent.html' (X) -> 'email_sent_page' (O)
        # 반드시 urls.py에 등록한 'name'을 써야 합니다.
        return redirect('email_sent_page')