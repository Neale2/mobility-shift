import boto3
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from .secrets import aws_environ
#credentials in report, set as env variables:
#export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
#export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"


def send_email(recipient, subject, html_body, uuid):
    aws_environ()
    sender = 'no-reply@testing123.my'
    unsubscribe_url = "http://127.0.0.1:8000/unsubscribe/" + uuid
    client = boto3.client('ses', region_name='ap-southeast-2')

    # Construct MIME message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg['Date'] = formatdate(localtime=True)
    
    # Unsubscribe header
    msg.add_header('List-Unsubscribe', f'<{unsubscribe_url}>')

    # Email body parts
    part_html = MIMEText(html_body, 'html', 'utf-8')
    msg.attach(part_html)

    # Send email
    try:
        response = client.send_raw_email(
            Source=sender,
            Destinations=[recipient],
            RawMessage={'Data': msg.as_string()}
        )
    except Exception as e:
        return "Error: email could not be sent.", e


