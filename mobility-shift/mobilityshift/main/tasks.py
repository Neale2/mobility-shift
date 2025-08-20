#tasks to be run at a certain time - add function here, then call from management/commands/runapscheduler.py
import os
import csv

from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta
from .secrets import azure_storage_connection_string, azure_spreadsheet_bucket_name

import time

from concurrent.futures import ThreadPoolExecutor

from django.template.loader import get_template
from .functions import send_email
from .models import User, Trip, DeletedUser, DeletedTrip

#hacked together way to send a single user an email for demos
def email_user(imp_user):
    from datetime import date, timedelta
    
    template = get_template('log-email.html')
    streak_loss_template = get_template('streak-loss-email.html')
    users = [imp_user]
    
    # Get current week start (Monday) for tracking
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    for user in users:
        # Handle streak logic before sending weekly email
        if user.logged_this_week:
            # User logged this week - increment or start streak
            user.current_streak += 1
            user.last_logged_week = week_start
        else:
            # User didn't log this week - check if they had a streak to lose
            if user.current_streak > 0:
                # Send streak loss email
                previous_streak = user.current_streak
                user.current_streak = 0
                
                streak_context = {
                    'email': user.email,
                    'user_uuid': user.uuid,
                    'emissions_saved': user.emissions_saved,
                    'name': user.name,
                    'previous_streak': previous_streak,
                }
                
                streak_html_body = streak_loss_template.render(streak_context)
                send_email(user.email, "You lost your streak :(", streak_html_body, str(user.uuid))
        
        # Send regular weekly reminder email
        context = {
            'email': user.email,
            'user_uuid': user.uuid,
            'emissions_saved': user.emissions_saved,
            'name': user.name,
            'current_streak': user.current_streak,
        }
        
        html_body = template.render(context)      
        response = send_email(user.email, "It's your weekly logging time!", html_body, str(user.uuid))
        
        # Reset weekly logging flag
        user.logged_this_week = False
        user.save()
    

#weekly email sent to all users asking if they had done a trip
def email_users():
    from datetime import date, timedelta
    
    template = get_template('log-email.html')
    streak_loss_template = get_template('streak-loss-email.html')
    users = list(User.objects.all())
    
    # Get current week start (Monday) for tracking
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    for user in users:
        # Handle streak logic before sending weekly email
        if user.logged_this_week:
            # User logged this week - increment or start streak
            user.current_streak += 1
            user.last_logged_week = week_start
        else:
            # User didn't log this week - check if they had a streak to lose
            if user.current_streak > 0:
                # Send streak loss email
                previous_streak = user.current_streak
                user.current_streak = 0
                
                streak_context = {
                    'email': user.email,
                    'user_uuid': user.uuid,
                    'emissions_saved': user.emissions_saved,
                    'name': user.name,
                    'previous_streak': previous_streak,
                }
                
                streak_html_body = streak_loss_template.render(streak_context)
                send_email(user.email, "You lost your streak :(", streak_html_body, str(user.uuid))
        
        # Send regular weekly reminder email
        context = {
            'email': user.email,
            'user_uuid': user.uuid,
            'emissions_saved': user.emissions_saved,
            'name': user.name,
            'current_streak': user.current_streak,
        }
        
        html_body = template.render(context)      
        response = send_email(user.email, "It's your weekly logging time!", html_body, str(user.uuid))
        
        # Reset weekly logging flag
        user.logged_this_week = False
        user.save()


def make_spreadsheet():
    all_data_list = [
        [
            'UUID',
            'Age Group',
            'Sign Up Time',
            'Emissions Saved (g)',
            'Mode',
            'Number of Trips',
            'Log Time',
            'Text Response',
            'Commute Distance (m)',
            'Primary Vehicle (emission factor)',
            'Employer',
            'Region',
            
        ]
    ]
    trips = []
    for trip in Trip.objects.all():
        trips.append(trip)
    for trip in DeletedTrip.objects.all():
        trips.append(trip)
    for trip in trips:
        try:
            data = [
                str(trip.user.uuid),
                trip.user.age_group,
                str(trip.user.sign_up_time.strftime('%Y-%m-%d %H:%M:%S')),
                trip.user.emissions_saved,
                trip.mode,
                trip.quantity,
                str(trip.log_time.strftime('%Y-%m-%d %H:%M:%S')),
                trip.text_response,
                str(trip.user.distance),
                str(trip.user.vehicle),
                trip.user.employer,
                trip.user.region,
                
            ]
            
        except Exception as e:
            data=["ERROR WITH USER. ERROR CODE:", e]
            
        all_data_list.append(data)
        
    
    try:
        csv_file_path = 'data.csv'
        # Open the file in write mode
        with open(csv_file_path, 'w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)

            # Write the data rows
            writer.writerows(all_data_list)
    except Exception as e:
        print("CSV GEN ERROR:", e)
    

    #azure connect to storage
    blob_service_client = BlobServiceClient.from_connection_string(azure_storage_connection_string())
    blob_client = blob_service_client.get_blob_client(container=azure_spreadsheet_bucket_name(), blob="data.csv")

    with open("data.csv", "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=azure_spreadsheet_bucket_name(),
        blob_name="data.csv",
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(days=1)
    )

    download_url = f"{blob_client.url}?{sas_token}"
    
    
    #second link for users :(
    all_data_list = [
        [
            'UUID',
            'Age Group',
            'Sign Up Time',
            'Emissions Saved (g)',
            'Commute Distance (m)',
            'Primary Vehicle (emission factor)',
            'Employer',
            'Region',
            'Email',
            'Name',
            'Logged this week?'

        ]
    ]
    users = []
    for user in User.objects.all():
        users.append(user)
    for user in DeletedUser.objects.all():
        users.append(user)
    for user in users:
        try:
            data = [
                str(user.uuid),
                user.age_group,
                str(user.sign_up_time.strftime('%Y-%m-%d %H:%M:%S')),
                user.emissions_saved,
                str(user.distance),
                str(user.vehicle),
                user.employer,
                user.region,
                
            ]
            #deleted accounds don't have emails
            try:
                data.append(user.email)
            except:
                data.append("DELETED")
            #deleted accounds don't have names
            try:
                data.append(user.name)
            except:
                data.append("DELETED")
            #deleted accounts don't have trip logged
            try:
                data.append(user.logged_this_week)
            except:
                data.append("False")
            
        except Exception as e:
            data=["ERROR WITH USER. ERROR CODE:", e]
            
        all_data_list.append(data)
        
    try:
        csv_file_path = 'users.csv'
        # Open the file in write mode
        with open(csv_file_path, 'w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)

            # Write the data rows
            writer.writerows(all_data_list)
    except Exception as e:
        print("CSV GEN ERROR:", e)
    

    #azure connect to storage
    blob_service_client = BlobServiceClient.from_connection_string(azure_storage_connection_string())
    blob_client = blob_service_client.get_blob_client(container=azure_spreadsheet_bucket_name(), blob="users.csv")

    with open("users.csv", "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=azure_spreadsheet_bucket_name(),
        blob_name="users.csv",
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(days=1)
    )

    user_download_url = f"{blob_client.url}?{sas_token}"
    
    email_response = send_email("arturo.neale@gmail.com", "Daily Database Dump", "Hi! Here's the trips database from today: " + download_url + " And here's the users: " + user_download_url, 'N/A', 3)
    print(email_response)
    
    