from django import forms
from django_altcha import AltchaField

class SignUpForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': "email short-text input"}), label="Input your email", max_length=320)
    age_group = forms.ChoiceField(widget=forms.Select(attrs={'class': "age multi input"}), label="Select your age group", choices=[("<13", "Less than 13"), ("13-17", "13 - 17"), ("18-24", "18 - 24"), ("25-34", "25 - 34"), ("35-44", "35 - 44"), ("45-64", "45 - 64"), (">65", "More than 65"), ("prefer_not", "Prefer not to say")])
    gender = forms.ChoiceField(widget=forms.Select(attrs={'class': "gender multi input"}), label="Select your gender", choices=[("male", "Male"), ("female", "Female"), ("other", "Other"), ("prefer_not", "Prefer not to say")])
    captcha = AltchaField(debug=False, auto='onload')

class YesLogForm(forms.Form):
    mode = forms.ChoiceField(widget=forms.Select(attrs={'class': "mode multi input"}), label="What mode of transport did you use?", choices=[("walk", "Walking"), ("bike", "Cycling"), ("bus", "Bussing")])
    #NOT when the trip was, but when trip was logged
    distance = forms.ChoiceField(widget=forms.Select(attrs={'class': "distance multi input"}), label="How far was the trip (pick the closest one to your real distance)?", choices=[(500, "0.5km"), (1000, "1km"), (2500, "2.5km"), (5000, "5km"), (10000, "10km"), (25000, "25km"), (50000, "50km")])
    captcha = AltchaField(debug=False, auto='onload')

class NoLogForm(forms.Form):
    #overriding default textinput widget since too small
    text_response = forms.CharField(widget=forms.Textarea(attrs={'class': "no-log long-text input"}), label="Why didn't you do your trip this week?")
    captcha = AltchaField(debug=False, auto='onload')
    
class UnsubForm(forms.Form):
    response = forms.ChoiceField(widget=forms.Select(attrs={'class': "unsub multi input"}), label="Do you want to unsubscribe from the program?", choices=[("no", "No :)"), ("yes", "Yes :(")])
    captcha = AltchaField(debug=False, auto='onload')