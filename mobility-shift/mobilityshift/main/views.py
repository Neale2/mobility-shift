import sys
import os
import uuid
import json
import re

from .functions import send_email, delete_list_user
from .secrets import webhook_token

from django.template.loader import get_template
from django.shortcuts import HttpResponseRedirect, redirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import SignUpForm, YesLogForm, NoLogForm, UnsubForm, EditProfileForm
from .models import User, Trip, DeletedUser, DeletedTrip, Employer, Region, All, Post, FriendRequest, Friendship

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
                send_email(form.cleaned_data['email'], "Welcome to the Programme!", html_body, user_uuid, 1)
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
    import json
    user = get_object_or_404(User, pk=pk)
    employer = get_object_or_404(Employer, pk=user.employer)
    region = get_object_or_404(Region, pk=user.region)
    all_model = get_object_or_404(All, pk="all")
    #gets first post
    post = Post.objects.order_by('-updated_at').first()
    
    # Get user's friendships and friend streaks
    friendships = list(user.friendships_as_user1.all()) + list(user.friendships_as_user2.all())
    friend_data = []
    for friendship in friendships:
        other_user = friendship.user2 if friendship.user1 == user else friendship.user1
        friend_data.append({
            'name': other_user.name,
            'streak': friendship.friend_streak,
            'emissions_saved': other_user.emissions_saved
        })
    
    context = {
        'user': user, 
        'employer': employer, 
        'region': region, 
        'all': all_model, 
        'post': post,
        'friends': friend_data,
        'friends_json': json.dumps(friend_data)
    }
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

@csrf_exempt
def unsub(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if request.META.get('HTTP_LIST_UNSUBSCRIBE_POST') == 'List-Unsubscribe=One-Click':
            delete_list_user(user)
            return HttpResponse("Success", status=200)
        else:
            form = UnsubForm(request.POST)
            if form.is_valid():
                #Checking if error in saving
                try:
                    if form.cleaned_data['response'] == 'yes':
                        delete_list_user(user)

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


@csrf_exempt
def bounce(request):
    token = request.GET.get('token')
    if token == webhook_token():
        try:
            events = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")

        for event in events:
            event_type = event.get('eventType')

            if event_type == 'Microsoft.EventGrid.SubscriptionValidationEvent':
                validation_code = event['data'].get('validationCode')
                return JsonResponse({'ValidationResponse': validation_code})

            if event_type == 'Microsoft.Communication.EmailDeliveryReportReceived':
                status = event['data'].get('status')
                recipient = event['data'].get('recipient')
                error_message=event['data'].get('deliveryStatusDetails').get('statusMessage')

                if status == 'Bounced':
                    print(f"BOUNCE: {recipient}")
                    pattern = r'\b([45]\d{2})[- ]\d\.\d\.\d\b'
                    matches = re.findall(pattern, error_message)
                    print("code is:", matches)

                    four = False

                    for code in matches:
                        if code[0] == "4":
                            four = True
                    if four == False:
                        user = get_object_or_404(User, email=recipient)
                        delete_list_user(user)
                        print("user deleted :(")

                elif status == 'Suppressed':
                    print(f"SUPPRESSED: {recipient}")
                    user = get_object_or_404(User, email=recipient)
                    delete_list_user(user)

        return JsonResponse({'status': 'ok'})
    
    else:
        return HttpResponse("Unauthorized", status=401)


def send_friend_request(request, pk):
    """Send a friend request to another user by email."""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        friend_email = request.POST.get('friend_email', '').strip()
        
        if not friend_email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        if friend_email == user.email:
            return JsonResponse({'error': 'You cannot add yourself as a friend'}, status=400)
        
        # Check if friend request already exists
        existing_request = FriendRequest.objects.filter(
            from_user=user, 
            to_email=friend_email
        ).first()
        
        if existing_request:
            return JsonResponse({'error': 'Friend request already sent to this email'}, status=400)
        
        # Check if they are already friends
        try:
            to_user = User.objects.get(email=friend_email)
            existing_friendship = Friendship.get_friendship(user, to_user)
            if existing_friendship:
                return JsonResponse({'error': 'You are already friends with this user'}, status=400)
        except User.DoesNotExist:
            to_user = None
        
        try:
            # Create friend request
            friend_request = FriendRequest.objects.create(
                from_user=user,
                to_email=friend_email,
                to_user=to_user
            )
            
            # Send friend request email
            template = get_template('friend-request-email.html')
            context = {
                'from_user_name': user.name,
                'from_user_emissions': user.emissions_saved,
                'request_id': friend_request.id,
            }
            
            html_body = template.render(context)
            send_email(friend_email, f"Friend request from {user.name}", html_body, str(user.uuid))
            
            return JsonResponse({'success': 'Friend request sent successfully!'})
            
        except Exception as e:
            return JsonResponse({'error': f'Error sending friend request: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def accept_friend_request(request, request_id):
    """Accept a friend request."""
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    
    if friend_request.is_accepted or friend_request.is_declined:
        return render(request, 'friend_request_already_handled.html', {'request': friend_request})
    
    try:
        # Get or create the target user
        to_user = friend_request.to_user
        if not to_user:
            try:
                to_user = User.objects.get(email=friend_request.to_email)
                friend_request.to_user = to_user
            except User.DoesNotExist:
                return render(request, 'friend_request_no_account.html', {'request': friend_request})
        
        # Mark request as accepted
        friend_request.is_accepted = True
        friend_request.save()
        
        # Create friendship (ensure consistent ordering)
        user1, user2 = (friend_request.from_user, to_user) if str(friend_request.from_user.uuid) < str(to_user.uuid) else (to_user, friend_request.from_user)
        
        friendship, created = Friendship.objects.get_or_create(
            user1=user1,
            user2=user2
        )
        
        return render(request, 'friend_request_accepted.html', {
            'request': friend_request,
            'friendship': friendship
        })
        
    except Exception as e:
        return render(request, 'friend_request_error.html', {'error': str(e)})


def decline_friend_request(request, request_id):
    """Decline a friend request."""
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    
    if friend_request.is_accepted or friend_request.is_declined:
        return render(request, 'friend_request_already_handled.html', {'request': friend_request})
    
    friend_request.is_declined = True
    friend_request.save()
    
    return render(request, 'friend_request_declined.html', {'request': friend_request})
