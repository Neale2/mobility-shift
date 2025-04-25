import sys
import os
import uuid

from . import send_email

from django.template.loader import get_template
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic

from .forms import SignUpForm, YesLogForm, NoLogForm, UnsubForm
from .models import User, Trip, DeletedUser, DeletedTrip



def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            #Checking if error in saving
            try:
                user_uuid = str(uuid.uuid4())
                template = get_template('signedup-email.html')
                context = {
                    'email': form.cleaned_data['email'],
                    'user_uuid': user_uuid,
                }
        
                html_body = template.render(context)
                
                print(send_email.send_email(form.cleaned_data['email'], "Welcome to the Programme!", html_body, user_uuid))
                data = User(email=form.cleaned_data['email'], age_group=form.cleaned_data['age_group'], gender=form.cleaned_data['gender'], uuid=user_uuid)
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
                #based on petrol emissions of 0.243kg/km -> 0.243g/m so all values will be int
                user.emissions_saved = user.emissions_saved + int(float(form.cleaned_data['distance']) * 0.243)
                user.save()
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

def unsub(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        form = UnsubForm(request.POST)
        if form.is_valid():
            #Checking if error in saving
            try:
                if form.cleaned_data['response'] == 'yes':
                    userdata = DeletedUser(uuid=user.uuid, age_group=user.age_group, gender=user.gender, sign_up_time=user.sign_up_time, emissions_saved=user.emissions_saved)
                    userdata.save()
                    trips = Trip.objects.filter(user_id=user.uuid)
                    for trip in trips:
                        tripdata = DeletedTrip(user=userdata, distance=trip.distance, text_response=trip.text_response, log_time=trip.log_time)
                        tripdata.save()
                    trips.delete()
                    user.delete()
                        
                    return HttpResponseRedirect("unsubbed/")
                else:
                    return HttpResponseRedirect("stillsubbed/")
            except Exception as e:
                if str(e) == "database is locked":
                    form.add_error(None, _("Unable to unsubscribe at this time since the database is in use - you might want to wait a couple seconds and try again."))
                else:
                    form.add_error(None, _("There's been an unidentified error! Sorry about that. The system error message is: " + str(e)))
        
    else:
        form = UnsubForm()
        
    context = {'user': user, 'form': form}
    return render(request, 'unsub.html', context)

def stillsubbed(request):
    return render(request, 'stillsubbed.html')

def unsubbed(request):
    return render(request, 'unsubbed.html')
