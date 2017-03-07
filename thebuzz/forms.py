#code from http://pythoncentral.io/how-to-use-python-django-forms/

from django import forms
from django.forms import ModelForm, Textarea
from datetime import datetime
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['displayName', 'firstName', 'lastName', 'email', 'githubUsername', 'bio']
        widgets = {
            'bio': Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        labels = {
            'displayName': 'Display Name:',
            'firstName': 'First Name:',
            'lastName': 'Last Name:',
            'email': 'Email:',
            'githubUsername': 'GitHub Username:',
            'bio': 'About Me:'
        }

class PostForm(forms.Form):
    posted_text = forms.CharField(max_length=2000)
    date_created = forms.DateTimeField()

class CommentForm(forms.Form):
    comment = forms.CharField(max_length=2000)
    date_created = forms.DateTimeField()
