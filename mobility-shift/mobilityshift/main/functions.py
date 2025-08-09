import json
import os
import threading
import time

from http import HTTPStatus


from azure.communication.email import EmailClient
from django.shortcuts import get_object_or_404

from .secrets import azure_email_connection_string
from .models import User, BackedEmail, Trip, DeletedUser, DeletedTrip

def delete_list_user(user):
    userdata = DeletedUser(uuid=user.uuid, age_group=user.age_group, sign_up_time=user.sign_up_time, emissions_saved=user.emissions_saved, distance=user.distance, vehicle=user.vehicle, employer=user.employer, region=user.region)
    userdata.save()
    trips = Trip.objects.filter(user_id=user.uuid)
    for trip in trips:
        tripdata = DeletedTrip(user=userdata, text_response=trip.text_response, log_time=trip.log_time, mode=trip.mode, quantity=trip.quantity)
        tripdata.save()
    trips.delete()
    user.delete()

def clear_backlog():
    wait_time = 2
    print("clog")
    while BackedEmail.objects.exists():
        time.sleep(wait_time)
        wait_time = wait_time * 2
        print("wait time", wait_time)
        emails = BackedEmail.objects.all().order_by('priority')
        for email in emails:
            code = send_email(email.recipient, email.subject, email.html_body, email.uuid, email.priority)
            email.delete()
            if code == "429":
                print("429 :(")
                break
            else:
                wait_time = 2
    return

def callback(response):
    if response.http_response.status_code == 429:
        raise Exception(response.http_response)

def post_send(poller):
    try:
        result = poller.result()
        print(result)
    except Exception as e:
        print("Background email result error:", e)

def send_email(recipient, subject, html_body, uuid, priority=2):
    try:
        try:
            name = get_object_or_404(User, pk=uuid).name
        except:
            name = "None"
        connection_string = azure_email_connection_string()
        client = EmailClient.from_connection_string(connection_string, raw_response_hook=callback)

        message = {
            "senderAddress": "no-reply@swapone.nz",
            "recipients": {
                "to": [{
                    "address": recipient,
                    "displayName": name
                }]
            },
            "content": {
                "subject": subject,
                "plainText": "Inbox not supported.",
                "html": html_body
            },
            "headers": {
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                "List-Unsubscribe": f"<app.swapone.nz/unsubscribe/{uuid}>"
            }
        }
        poller = None
        try:
            poller = client.begin_send(message)
        except Exception as e:
            if "429" in str(e):
                print("429")
                data = BackedEmail(recipient=recipient, subject=subject, html_body=html_body, uuid=uuid, priority=priority)
                data.save()
                return("429")

            else:
                raise
        if poller:
            threading.Thread(target=post_send, args=(poller,)).start()
    except Exception as ex:
        print("Email Send error:", ex)

    

