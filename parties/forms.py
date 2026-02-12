from django import forms
from .models import Party

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        # 모델의 필드명과 일치하게 구성
        fields = ['game', 'mode', 'description', 'max_members', 'mic_required']
        widgets = {
            'game': forms.Select(attrs={
                'style': 'width:100%; padding:12px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1); border-radius:8px;'
            }),
            # ✅ 이제 일반 텍스트 입력창으로 나옵니다.
            'mode': forms.TextInput(attrs={
                'placeholder': '예: 랭크, 일반, 칼바람, 신속, 내전',
                'style': 'width:100%; padding:12px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1); border-radius:8px;'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': '내용을 입력하세요', 
                'rows': 3,
                'style': 'width:100%; padding:12px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1); border-radius:8px; resize:none;'
            }),
            'max_members': forms.NumberInput(attrs={
                'style': 'width:100%; padding:12px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1); border-radius:8px;'
            }),
            'mic_required': forms.CheckboxInput(attrs={
                'id': 'mic_checkbox',
                'style': 'display:none;'
            }),
        }
        labels = {
            'game': '게임 선택',
            'mode': '게임 모드',
            'description': '내용',
            'max_members': '최대 인원',
            'mic_required': '마이크 필수 여부',
        }