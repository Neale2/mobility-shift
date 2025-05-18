from django import forms
from django.db.models import Case, When, Value, IntegerField
from django_altcha import AltchaField
from .models import Employer, Region

class SignUpForm(forms.Form):
    
    name = forms.CharField(widget=forms.TextInput(attrs={'class': "name short-text input"}), label="What would you like us to call you?", max_length=20)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': "email short-text input"}), label="Input your email", max_length=320)
    age_group = forms.ChoiceField(widget=forms.Select(attrs={'class': "age multi input"}), label="Select your age group", choices=[("<13", "Less than 13"), ("13-17", "13 - 17"), ("18-24", "18 - 24"), ("25-34", "25 - 34"), ("35-44", "35 - 44"), ("45-64", "45 - 64"), (">65", "More than 65"), ("prefer_not", "Prefer not to say")])
    distance = forms.ChoiceField(widget=forms.Select(attrs={'class': "distance multi input"}), label="Approximately how far is your typical commute?", choices=[(500, "0.5km"), (1000, "1km"), (2500, "2.5km"), (5000, "5km"), (10000, "10km"), (25000, "25km"), (50000, "50km")])
    #numbers returned are emission factors (g/km) for ease. Don't know/other returns typical petrol number
    vehicle = forms.ChoiceField(widget=forms.Select(attrs={'class': "vehicle multi input"}), label="What type of vehicle do you normally use to commute?", choices=[(243, "Petrol"), (265, "Diesel"), (192, "Hybrid"), (98, "Plug-in Hybrid"), (19, "Electric"), (243, "Other / Don't know")])
    employer = forms.ModelChoiceField(widget=forms.Select(attrs={'class': "employerMode multi input"}), label="Who is your employer?", queryset=Employer.objects.annotate(
        #orders list so none at top
        priority=Case(
        When(name='None / Other / Prefer Not To Say', then=Value(0)),
        default=Value(1),
        output_field=IntegerField()
    )
).order_by('priority', 'name'), blank=False, initial='None / Other / Prefer Not To Say')
    region = forms.ModelChoiceField(widget=forms.Select(attrs={'class': "employerMode multi input"}), label="What region do you live in?", queryset=Region.objects.all(), blank=False, initial='Nelson')
    captcha = AltchaField(debug=False, auto='onload')
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        return name.title()

class YesLogForm(forms.Form):
    mode = forms.ChoiceField(widget=forms.Select(attrs={'class': "mode multi input"}), label="What mode of transport did you use?", choices=[("walk", "Walking"), ("bike", "Cycling"), ("bus", "Bussing")])
    captcha = AltchaField(debug=False, auto='onload')

class NoLogForm(forms.Form):
    #overriding default textinput widget since too small
    text_response = forms.CharField(widget=forms.Textarea(attrs={'class': "no-log long-text input"}), label="Why didn't you do your trip this week?")
    captcha = AltchaField(debug=False, auto='onload')
    
class UnsubForm(forms.Form):
    response = forms.ChoiceField(widget=forms.Select(attrs={'class': "unsub multi input"}), label="Do you want to unsubscribe from the program?", choices=[("no", "No :)"), ("yes", "Yes :(")])
    captcha = AltchaField(debug=False, auto='onload')