from django import forms

class SignUpForm(forms.Form):
    email = forms.EmailField(label="Input your email", max_length=320)
    age_group = forms.ChoiceField(label="Select your age group", choices=[("<13", "Less than 13"), ("13-17", "13 - 17"), ("18-24", "18 - 24"), ("25-34", "25 - 34"), ("35-44", "35 - 44"), ("45-64", "45 - 64"), (">65", "More than 65"), ("prefer_not", "Prefer not to say")])
    gender = forms.ChoiceField(label="Select your gender", choices=[("male", "Male"), ("female", "Female"), ("other", "Other"), ("prefer_not", "Prefer not to say")])