from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages
from allauth.account.models import EmailAddress

class VerifiedEmailRequiredMixin(AccessMixin):
    """
    이메일 인증이 완료된 유저만 접근을 허용하는 Mixin
    인증이 안 된 경우: 알림 메시지를 띄우고 '메인 페이지'로 이동
    """
    
    def dispatch(self, request, *args, **kwargs):
        # 1. 혹시 로그인이 안 되어 있다면 LoginRequiredMixin이 처리하도록 넘김 (또는 로그인 페이지로)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # 2. 이메일 인증 여부 확인
        # allauth의 EmailAddress 모델을 조회하여 verified=True인 것이 있는지 확인
        if not EmailAddress.objects.filter(user=request.user, verified=True).exists():
            messages.error(request, "이메일 인증을 완료해야 파티를 생성할 수 있습니다 📧")
            return redirect('main')  # ✅ 메인 페이지('main')로 리다이렉트
            
        return super().dispatch(request, *args, **kwargs)