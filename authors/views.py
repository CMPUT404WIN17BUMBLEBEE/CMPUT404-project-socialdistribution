# Code altered from http://code.techandstartup.com/django/registration/

from django.shortcuts import render
from django.shortcuts import render_to_response 
from django.http import HttpResponseRedirect 
from django.contrib.auth.forms import UserCreationForm 
from django.core.context_processors import csrf

# Create your views here.
#for signing up
def register(request):
     if request.method == 'POST':
         form = UserCreationForm(request.POST)
         if form.is_valid():
             form.save()
             return HttpResponseRedirect('/register/complete')

     else:
         form = UserCreationForm()
     token = {}
     token.update(csrf(request))
     token['form'] = form

     return render_to_response('registration/registration_form.html', token)

def registration_complete(request):
     return render_to_response('registration/registration_complete.html')

#for logging in
#code edited from https://docs.djangoproject.com/en/dev/topics/auth/default/#user-objects
def logIn(request):
	 return render_to_response('registration/login.html')
        
