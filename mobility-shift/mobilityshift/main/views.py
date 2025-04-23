from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic

from .forms import SignUpForm, YesLogForm, NoLogForm
from .models import User, Trip

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            #Checking if error in saving
            try:
                data = User(email=form.cleaned_data['email'], age_group=form.cleaned_data['age_group'], gender=form.cleaned_data['gender'])
                data.save()
                return HttpResponseRedirect("confirm/")
            except Exception as e:
                if str(e) == "UNIQUE constraint failed: main_user.email":
                    form.add_error(None, _("A user with this Email already exists! You might want to check your inbox, including spam."))
                elif str(e) == "database is locked":
                    form.add_error(None, _("Unable to save your response at this time - you might want to wait a couple seconds and try again."))
                else:
                    form.add_error(None, _("There's been an unidentified error! Sorry about that. The system error message is: " + str(e)))
                
            
            
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {"form": form})

def confirm(request):
    return render(request, 'confirm.html')

def thanks(request):
    return render(request, 'thanks.html')

def yes(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        form = YesLogForm(request.POST)
        if form.is_valid():
            #Checking if error in saving
            try:
                data = Trip(user=user, mode=form.cleaned_data['mode'], distance=form.cleaned_data['distance'])
                data.save()
                return HttpResponseRedirect("thanks/")
            except Exception as e:
                if str(e) == "database is locked":
                    form.add_error(None, _("Unable to save your response at this time - you might want to wait a couple seconds and try again."))
                else:
                    form.add_error(None, _("There's been an unidentified error! Sorry about that. The system error message is: " + str(e)))
        
    else:
        form = YesLogForm()
        
    context = {'user': user, 'form': form}
    
    return render(request, 'yes.html', context)
    
def no(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        form = NoLogForm(request.POST)
        if form.is_valid():
            #Checking if error in saving
            try:
                #no mode included
                data = Trip(user=user, distance=0, text_response=form.cleaned_data['text_response'])
                data.save()
                return HttpResponseRedirect("thanks/")
            except Exception as e:
                if str(e) == "database is locked":
                    form.add_error(None, _("Unable to save your response at this time - you might want to wait a couple seconds and try again."))
                else:
                    form.add_error(None, _("There's been an unidentified error! Sorry about that. The system error message is: " + str(e)))
        
    else:
        form = NoLogForm()
        
    context = {'user': user, 'form': form}
    return render(request, 'no.html', context)
