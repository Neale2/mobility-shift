from django.template.loader import get_template
from . import send_email

from .models import User

def email_users():
    template = get_template('log-email.html')
    for user in User.objects.all():
        context = {
            'email': user.email,
            'user_uuid': user.uuid,
            'emissions_saved': user.emissions_saved,
        }
        
        html_body = template.render(context)
        
        response = send_email.send_email(user.email, "It's your weekly logging time!", html_body, str(user.uuid))
        print(user.email, response)
    
            
    