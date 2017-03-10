#code from http://pythoncentral.io/how-to-use-python-django-forms/

from django import forms
from django.forms import ModelForm, Textarea
from datetime import datetime
from .models import Profile, Comment, Post

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['displayName', 'firstName', 'lastName', 'email', 'github', 'bio']
        widgets = {
            'bio': Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        labels = {
            'displayName': 'Display Name:',
            'firstName': 'First Name:',
            'lastName': 'Last Name:',
            'email': 'Email:',
            'github': 'GitHub:',
            'bio': 'About Me:'
        }

class PostForm(forms.Form):
    posted_text = forms.CharField(max_length=2000)
    date_created = forms.DateTimeField()

class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': 'Comment'
        }
