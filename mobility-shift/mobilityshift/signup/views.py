from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from .forms import SignUpForm
from .models import User

def index(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['email'])
            #Checking if error in signup
            try:
                data = User(email=form.cleaned_data['email'], age_group=form.cleaned_data['age_group'], gender=form.cleaned_data['gender'])
                data.save()
                return HttpResponseRedirect("/confirm/")
            except Exception as e:
                if str(e) == "UNIQUE constraint failed: signup_user.email":
                    form.add_error(None, _("A user with this Email already exists! You might want to check your inbox, including spam."))
                elif str(e) == "database is locked":
                    form.add_error(None, _("Unable to save your response at this time - you might want to wait a couple seconds and try again."))
                else:
                    form.add_error(None, _("There's been an unidentified error! Sorry about that. The system error message is: " + str(e)))
                
            
            
    else:
        form = SignUpForm()
    return render(request, 'index.html', {"form": form})
