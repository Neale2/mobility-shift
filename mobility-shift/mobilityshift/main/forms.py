from django import forms

class SignUpForm(forms.Form):
    email = forms.EmailField(label="Input your email", max_length=320)
    age_group = forms.ChoiceField(label="Select your age group", choices=[("<13", "Less than 13"), ("13-17", "13 - 17"), ("18-24", "18 - 24"), ("25-34", "25 - 34"), ("35-44", "35 - 44"), ("45-64", "45 - 64"), (">65", "More than 65"), ("prefer_not", "Prefer not to say")])
    gender = forms.ChoiceField(label="Select your gender", choices=[("male", "Male"), ("female", "Female"), ("other", "Other"), ("prefer_not", "Prefer not to say")])

class YesLogForm(forms.Form):
    mode = forms.ChoiceField(label="What mode of transport did you use?", choices=[("walk", "Walking"), ("bike", "Cycling"), ("bus", "Bussing")])
    #NOT when the trip was, but when trip was logged
    distance = forms.ChoiceField(label="How far was the trip (pick the closest one)?", choices=[(500, "0.5km"), (1000, "1km"), (2500, "2.5km"), (5000, "5km"), (10000, "10km"), (25000, "25km"), (50000, "50km")])

class NoLogForm(forms.Form):
    #overriding default textinput widget since too small
    text_response = forms.CharField(label="Why didn't you do your trip this week?", widget=forms.Textarea)
    
class UnsubForm(forms.Form):
    response = forms.ChoiceField(label="Do you want to unsubscribe from the program?", choices=[("no", "No :)"), ("yes", "Yes :(")])