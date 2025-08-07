import json
import os
import threading

from azure.communication.email import EmailClient
from django.shortcuts import get_object_or_404

from .secrets import azure_email_connection_string
from .models import User

def post_send(poller):
    try:
        result = poller.result()
        print(result)
    except Exception as e:
        print("Background email result error:", e)

def send_email(recipient, subject, html_body, uuid):
    try:
        try:
            name = get_object_or_404(User, pk=uuid).name
        except:
            name = "None"
        connection_string = azure_email_connection_string()
        client = EmailClient.from_connection_string(connection_string)

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
            
        }

        poller = client.begin_send(message)
        threading.Thread(target=post_send, args=(poller,)).start()

    except Exception as ex:
        print("Email Send error:", ex)

    

