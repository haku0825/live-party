from django.views.generic import TemplateView, View  # ✅ View 추가
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from allauth.account.models import EmailAddress
from parties.models import PartyMember
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from .forms import ProfileUpdateForm
from django.urls import reverse_lazy
from django.contrib import messages 
from django.views.generic.edit import FormView
from .forms import EmailChangeForm
from allauth.account.models import EmailAddress, EmailConfirmation

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

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'account/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # ✅ 스마트한 처리: 변경된 내용이 있는지 검사
        if not form.has_changed():
            # 변경된 게 없으면 DB 저장 건너뛰고 바로 리다이렉트
            messages.info(self.request, "변경된 내용이 없어 저장하지 않았습니다. 🤔")
            return redirect(self.success_url)
            
        # 변경된 게 있을 때만 저장 + 성공 메시지
        messages.success(self.request, "프로필이 성공적으로 수정되었습니다! ✨")
        return super().form_valid(form)

# ✅ 이메일 변경 뷰 (수정됨)
class EmailChangeView(LoginRequiredMixin, FormView):
    template_name = 'account/email.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        try:
            # 1. [정리] 기존 이메일 정보 싹 지우기 (충돌 방지)
            EmailAddress.objects.filter(user=user).delete()

            # 2. [생성] 새 이메일 등록 (아직 미인증 상태)
            new_email_obj = EmailAddress.objects.create(
                user=user,
                email=new_email,
                primary=True,
                verified=False
            )

            # 3. [동기화] 유저 모델의 이메일 컬럼도 업데이트
            user.email = new_email
            user.save()

            # 🔥 4. [핵심 - 강제 발송 로직] 
            # 함수(send_confirmation)를 믿지 않고, 인증서(Confirmation)를 직접 발급해서 쏩니다.
            # 이 방법은 설정 탓을 하지 않고 무조건 날아갑니다.
            confirmation = EmailConfirmation.create(new_email_obj)
            confirmation.send(self.request, signup=False) # signup=False로 명시

            # (디버깅용 로그 - 터미널 확인용)
            print(f"✅ [성공] {new_email}로 인증 메일 강제 발송 완료!")

            # 5. [피드백] 사용자에게 알림
            messages.success(self.request, f"이메일이 {new_email}로 변경되었습니다! 📩 인증 메일을 꼭 확인해주세요.")
            
            # 6. [이동] 메인 페이지로 확실하게 보냄
            return redirect('main')
            
        except Exception as e:
            # 혹시 모를 에러가 나면 터미널에 찍어줍니다.
            print(f"❌ [오류] 이메일 변경 중 에러 발생: {e}")
            messages.error(self.request, f"오류가 발생했습니다: {str(e)}")
            return self.form_invalid(form)