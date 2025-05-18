#tasks to be run at a certain time - add function here, then call from management/commands/runapscheduler.py
import os
import csv
import boto3
from botocore.exceptions import ClientError


from django.template.loader import get_template
from .functions import send_email
from .secrets import aws_environ, bucket_name

from .models import User, Trip, DeletedUser, DeletedTrip



#weekly email sent to all users asking if they had done a trip
def email_users():
    template = get_template('log-email.html')
    for user in User.objects.all():
        context = {
            'email': user.email,
            'user_uuid': user.uuid,
            'emissions_saved': user.emissions_saved,
            'name': user.name,
        }
        
        html_body = template.render(context)
        
        response = send_email(user.email, "It's your weekly logging time!", html_body, str(user.uuid))
        print(user.email, response)


def make_spreadsheet():
    all_data_list = [
        [
            'UUID',
            'Age Group',
            'Sign Up Time',
            'Emissions Saved (g)',
            'Mode',
            'Log Time',
            'Text Response',
            'Commute Distance (m)',
            'Primary Vehicle (emission factor)',
            'Employer',
            'Region',
            'Email',
            'Name',
            
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
                str(trip.user.sign_up_time),
                trip.user.emissions_saved,
                trip.mode,
                str(trip.log_time),
                trip.text_response,
                str(trip.user.distance),
                str(trip.user.vehicle),
                trip.user.employer,
                trip.user.region,
                
            ]
            #deleted accounds don't have emails
            try:
                data.append(trip.user.email)
            except:
                data.append("DELETED")
            #deleted accounds don't have names
            try:
                data.append(trip.user.name)
            except:
                data.append("DELETED")
            
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
    
    file_size = os.path.getsize("data.csv")
    
    #configure AWS keys as environment variables
    aws_environ()
    
    s3 = boto3.client('s3')
    s3.upload_file('data.csv', bucket_name(), 'data.csv')
    
    try:
        response = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                #returns string of bucket name
                'Bucket': bucket_name(),
                'Key': 'data.csv'
            },
            #86400s = one day
            ExpiresIn=86400
        )
    except ClientError as e:
        raise RuntimeError(f"Could not generate presigned URL: {e}")
    if response:
        email_response = send_email("arturo.neale@gmail.com", "Daily Database Dump", "Hi! Here's the database from today!" + response, 'N/A')
        print(email_response)
    