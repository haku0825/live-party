from django.shortcuts import render
from django.views import View

# Create your views here.
class MainView(View):
    def get(self, request):
        return render(request, 'core/main.html')

class GuideView(View):
    def get(self, request):
        return render(request, 'core/guide.html')