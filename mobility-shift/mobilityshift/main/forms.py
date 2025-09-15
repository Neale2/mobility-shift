from django import forms
from django.forms import ModelForm
from django.db.models import Case, When, Value, IntegerField
from turnstile.fields import TurnstileField
from .models import Employer, Region, User

class SignUpForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': "name short-text input", 'id': 'name', 'placeholder': 'type your name'}), label="What's your name?", max_length=320)
    age_group = forms.ChoiceField(widget=forms.Select(attrs={'class': "age multi input", 'id': 'age'}), label="How old are you?", choices=[("<13", "Under 13"), ("13-17", "13 - 17"), ("18-24", "18 - 24"), ("25-34", "25 - 34"), ("35-44", "35 - 44"), ("45-64", "45 - 64"), (">65", "More than 65"), ("prefer_not", "Prefer not to say")])
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': "email short-text input info", 'id': 'email', 'placeholder': 'type your email'}), label="Email", max_length=320)
    distance = forms.ChoiceField(widget=forms.Select(attrs={'class': "distance multi input info", 'id': 'distance'}), label="Commute Distance", choices=[(500, "0.5km"), (1000, "1km"), (2500, "2.5km"), (5000, "5km"), (10000, "10km"), (25000, "25km"), (50000, "50km")])
    #numbers returned are emission factors (g/km) for ease. Don't know/other returns typical petrol number
    vehicle = forms.ChoiceField(widget=forms.Select(attrs={'class': "vehicle multi input", 'id': 'vehicle'}), label="Vehicle Type", choices=[(243, "Petrol"), (265, "Diesel"), (192, "Hybrid"), (98, "Plug-in Hybrid"), (19, "Electric"), (243, "Other / Don't know")])
    employer = forms.ModelChoiceField(widget=forms.Select(attrs={'class': "employer multi input", 'id': "employer"}), label="Employer", queryset=Employer.objects.annotate(
        #orders list so none at top
        priority=Case(
        When(name='None / Other / Prefer Not To Say', then=Value(0)),
        default=Value(1),
        output_field=IntegerField()
    )
    ).order_by('priority', 'name'), blank=False, initial='None / Other / Prefer Not To Say')
    region = forms.ModelChoiceField(widget=forms.Select(attrs={'class': "region multi input", 'id': 'region'}), label="Region", queryset=Region.objects.all(), blank=False, initial='Nelson')
    captcha = TurnstileField(label="")
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        return name.title()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already in use. Please try another.")
        return email

class YesLogForm(forms.Form):
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': "quantity multi input"}), label="How many high carbon trips (one way) did you swap this week?", min_value=1, max_value=14)
    mode = forms.ChoiceField(widget=forms.Select(attrs={'class': "mode multi input"}), label="What mode of transport did you use?", choices=[("walk", "Walk"), ("bike", "Bike / Scooter"), ("bus", "Bus"), ("ev", "EV"), ('carpool', "Carpool"), ('wfh', 'Work from Home')])
    captcha = TurnstileField(label="")

class NoLogForm(forms.Form):
    text_response = forms.CharField(widget=forms.TextInput(attrs={'class': "no-log long-text input"}), required=False, label="Other:")
    captcha = TurnstileField(label="")
    
class UnsubForm(forms.Form):
    response = forms.ChoiceField(widget=forms.Select(attrs={'class': "unsub multi input"}), label="Do you want to unsubscribe from the program?", choices=[("no", "No :)"), ("yes", "Yes :(")])
    captcha = TurnstileField(label="")
    
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "email", "age_group", "distance",
                  "vehicle", "employer", "region"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "name short-text input"}),
            "email": forms.EmailInput(attrs={"class": "email short-text input"}),
            "age_group": forms.Select(attrs={"class": "age multi input"}),
            "distance": forms.Select(attrs={"class": "distance multi input"}),
            "vehicle": forms.Select(attrs={"class": "vehicle multi input"}),
            "employer": forms.Select(attrs={"class": "employer multi input"}),
            "region":  forms.Select(attrs={"class": "region multi input"}),
        }
        
        labels = {
            'email': 'Email Address',
            'age_group': 'Age Group',
            'name': 'Name',
            'distance': 'Travel Distance (One Way)',
            'vehicle': 'Vehicle Type',
            'employer': 'Employer Name',
            'region': 'Region',
        }

    employer = forms.ModelChoiceField(widget=forms.Select(attrs={'class': "region multi input"}),
        queryset=Employer.objects.annotate(
            priority=Case(
                When(name="None / Other / Prefer Not To Say", then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            )
        ).order_by("priority", "name"),
        label="Who is your employer?",
    )

    region = forms.ModelChoiceField(widget=forms.Select(attrs={'class': "widget multi input"}),
        queryset=Region.objects.all(),
        label="What region do you live in?",
    )

    captcha = TurnstileField(label="")