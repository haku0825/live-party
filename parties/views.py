from django.views.generic import ListView, CreateView, DetailView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from .models import Party, PartyMember
from .forms import PartyForm
from chat.models import ChatMessage  # 채팅 메시지 모델 임포트

# 1. 파티 목록
class PartyListView(ListView):
    model = Party
    template_name = 'parties/party_list.html'
    context_object_name = 'parties'
    
    def get_queryset(self):
        return Party.objects.exclude(status=Party.Status.CLOSED).order_by('-created_at')

# 2. 파티 생성
class PartyCreateView(LoginRequiredMixin, CreateView):
    model = Party
    form_class = PartyForm
    template_name = 'parties/party_create.html'

    def form_valid(self, form):
        user = self.request.user
        active_party = Party.objects.filter(host=user).exclude(status=Party.Status.CLOSED).exists()
        
        if active_party:
            form.add_error(None, "이미 모집 중인 파티가 있습니다.")
            return self.form_invalid(form)

        with transaction.atomic():
            # 유저 정보 할당 및 저장
            form.instance.host = user
            self.object = form.save()
            
            # 방장을 멤버로 자동 등록 (이때 current_member_count 1로 시작)
            PartyMember.objects.create(party=self.object, user=user, is_active=True)

        # ✅ 여기서 바로 상세 페이지로 날려줘야 500 에러가 안 납니다!
        return redirect('party_detail', pk=self.object.pk)


# 3. 파티 상세 (입장 처리 및 채팅 내역 불러오기)
class PartyDetailView(DetailView, LoginRequiredMixin):
    model = Party
    template_name = 'parties/party_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if request.user.is_authenticated:
            member = PartyMember.objects.filter(party=self.object, user=request.user).first()
            if member and not member.is_active:
                if self.object.status != Party.Status.CLOSED:
                    member.is_active = True
                    member.save()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        party = self.object

        if user.is_authenticated:
            context['is_member'] = party.members.filter(user=user, is_active=True).exists()
            context['is_host'] = (party.host == user)
            # ✅ 과거 채팅 내역 50개를 시간순으로 가져오기
            context['chat_messages'] = party.messages.select_related('user').order_by('created_at')[:50]
        else:
            context['is_member'] = False
            context['is_host'] = False
        return context

# 4. 파티 참여
class PartyJoinView(LoginRequiredMixin, View):
    def post(self, request, pk):
        party = get_object_or_404(Party, pk=pk)
        
        if party.status == Party.Status.CLOSED:
            return redirect('party_list')

        if party.current_member_count < party.max_members:
            PartyMember.objects.update_or_create(
                party=party,
                user=request.user,
                defaults={'is_active': True}
            )
        
        return redirect('party_detail', pk=pk)

# 5. 파티 나가기
class PartyLeaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        party = get_object_or_404(Party, pk=pk)
        
        if party.host == request.user:
            party.status = Party.Status.CLOSED
            party.save()
        else:
            membership = PartyMember.objects.filter(party=party, user=request.user).first()
            if membership:
                membership.is_active = False
                membership.save()
                
        return redirect('party_list')