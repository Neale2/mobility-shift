from django.shortcuts import render
from django.views import generic
from signup.models import User

def confirm(request):
    return render(request, 'confirm.html')
    

class YesUUIDView(generic.DetailView):
    model = User
    template_name = 'yes.html'
    
class NoUUIDView(generic.DetailView):
    model = User
    template_name = 'no.html'