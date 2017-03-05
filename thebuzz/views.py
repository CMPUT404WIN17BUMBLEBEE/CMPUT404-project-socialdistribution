from django.shortcuts import render
from django.shortcuts import render_to_response 
from django.http import HttpResponseRedirect 
from django.contrib.auth.forms import UserCreationForm 
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required

#------------------------------------------------------------------
# SIGNING UP

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

#for showing the home page/actually logging in
#3 ways to get here:
#-logged in
#-already logged in, used a cookie
#-registered
#otherwise, tell them to log in if theyre not
#edited code from here to log a user in (https://www.fir3net.com/Web-Development/Django/django.html)
@login_required(login_url = '/login/')
def homePage(request):
	 #if this person has just logged in

			return render(request, 'registration/home.html')
		#else:
			#invalid login page -- implement later	

	 #else: #change this later to account for the other 2 cases ******
	 #	return render_to_response('registration/login.html')

# END LOGIN VIEWS------------------------------------------------------------------------------------------
