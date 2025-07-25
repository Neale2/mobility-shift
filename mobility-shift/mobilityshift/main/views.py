import sys
import os
import uuid

from .functions import send_email

from django.template.loader import get_template
from django.shortcuts import HttpResponseRedirect, redirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic

from .forms import SignUpForm, YesLogForm, NoLogForm, UnsubForm, EditProfileForm
from .models import User, Trip, DeletedUser, DeletedTrip, Employer, Region, All, Post

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            #Checking if error in saving
            try:
                user_uuid = str(uuid.uuid4())
                template = get_template('signedup-email.html')
                context = {
                    'name': form.cleaned_data['name'],
                    'user_uuid': user_uuid,
                }
        
                html_body = template.render(context)
                
                data = User(email=form.cleaned_data['email'], age_group=form.cleaned_data['age_group'], uuid=user_uuid, name=form.cleaned_data['name'], distance=form.cleaned_data['distance'], vehicle=form.cleaned_data['vehicle'], employer=form.cleaned_data['employer'], region=form.cleaned_data['region'])
                data.save()
                send_email(form.cleaned_data['email'], "Welcome to the Programme!", html_body, user_uuid)
                return HttpResponseRedirect("/signup/confirm/")
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

def edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            #Checking if error in saving
            try:
                form.save()
                
                return redirect(f"/dash/{pk}?confirm_edit=true")
            except Exception as e:
                if str(e) == "UNIQUE constraint failed: main_user.email":
                    form.add_error(None, _("A user with this Email already exists! You might want to check your inbox, including spam."))
                elif str(e) == "database is locked":
                    form.add_error(None, _("Unable to save your response at this time - you might want to wait a couple seconds and try again."))
                else:
                    form.add_error(None, _("There's been an unidentified error! Sorry about that. The system error message is: " + str(e)))

    else:
        form = EditProfileForm(instance=user)
    context = {'user': user, 'form': form}
    return render(request, 'edit.html', context)

def confirm(request):
    return render(request, 'confirm.html')

def dash(request, pk):
    user = get_object_or_404(User, pk=pk)
    employer = get_object_or_404(Employer, pk=user.employer)
    region = get_object_or_404(Region, pk=user.region)
    all_model = get_object_or_404(All, pk="all")
    #gets first post
    post = Post.objects.order_by('-updated_at').first()
    
    context = {'user': user, 'employer': employer, 'region': region, 'all': all_model, 'post': post}
    return render(request, 'dash.html', context)

def yes(request, pk):
    user = get_object_or_404(User, pk=pk)
    employer = get_object_or_404(Employer, pk=user.employer)
    region = get_object_or_404(Region, pk=user.region)
    all_model = get_object_or_404(All, pk="all")
    
    if request.method == "POST":
        form = YesLogForm(request.POST)
        #grams of emissions per km - carpool is half of personal vehicle emissions - assuming 2 people carpooling
        mode_emissions = {'walk': 0, 'bike': 0, 'bus': 15, 'ev': 19, 'carpool': user.vehicle / 2, 'wfh': 0}
        choices=[("walk", "Walk"), ("bike", "Bike / Scooter"), ("bus", "Bus"), ("ev", "EV"), ('carpool', "Carpool"), ('wfh', 'Work from Home')]
        if form.is_valid():
            #Checking if error in saving
            try:
                print(mode_emissions[form.cleaned_data['mode']])
                #gets emission factor in grams per km. subtracts factor of changed mode of transport. div by 1000 to get grams per meter. multiply by meters traveled and number of trips.
                emissions_saved = int(form.cleaned_data['quantity'] * user.distance * (user.vehicle - mode_emissions[form.cleaned_data['mode']]) / 1000)
                user.emissions_saved = user.emissions_saved + emissions_saved
                user.logged_this_week = True
                user.save()
                region.emissions_saved = region.emissions_saved + emissions_saved
                region.save()
                employer.emissions_saved = employer.emissions_saved + emissions_saved
                employer.save()
                all_model.emissions_saved = all_model.emissions_saved + emissions_saved
                all_model.save()
                
                
                data = Trip(user=user, mode=form.cleaned_data['mode'], quantity=form.cleaned_data['quantity'])
                data.save()
                return redirect(f"/dash/{pk}")
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
                #no mode or quantity included
                user.logged_this_week = True
                user.save()
                data = Trip(user=user, text_response=form.cleaned_data['text_response'], quantity=0)
                data.save()
                return redirect(f"/dash/{pk}")
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
                    userdata = DeletedUser(uuid=user.uuid, age_group=user.age_group, sign_up_time=user.sign_up_time, emissions_saved=user.emissions_saved, distance=user.distance, vehicle=user.vehicle, employer=user.employer, region=user.region)
                    userdata.save()
                    trips = Trip.objects.filter(user_id=user.uuid)
                    for trip in trips:
                        tripdata = DeletedTrip(user=userdata, text_response=trip.text_response, log_time=trip.log_time, mode=trip.mode, quantity=trip.quantity)
                        tripdata.save()
                    trips.delete()
                    user.delete()
                        
                    return HttpResponseRedirect("unsubbed/")
                else:
                    return HttpResponseRedirect(f"stillsubbed/{pk}")
            except Exception as e:
                if str(e) == "database is locked":
                    form.add_error(None, _("Unable to unsubscribe at this time since the database is in use - you might want to wait a couple seconds and try again."))
                else:
                    form.add_error(None, _("There's been an unidentified error! Sorry about that. The system error message is: " + str(e)))
        
    else:
        form = UnsubForm()
        
    context = {'user': user, 'form': form}
    return render(request, 'unsub.html', context)

def stillsubbed(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {'user': user}
    return render(request, 'stillsubbed.html', context)

def unsubbed(request):
    return render(request, 'unsubbed.html')
