#code from http://pythoncentral.io/how-to-use-python-django-forms/

from django import forms
from django.forms import ModelForm, Textarea
from datetime import datetime
import CommonMark
 
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
    title = forms.CharField(max_length = 100)
    content = forms.CharField(max_length=2000, widget=forms.Textarea)
    published = forms.DateTimeField()

    CHOICES=[('PUBLIC','Public'),
         ('FRIENDS','Friends'),
	 ('FOAF', 'Friend of A Friend'),
	 ('PRIVATE', 'Private'),
	 ('SERVERONLY', 'Members of this server only')]

    choose_Post_Visibility = forms.ChoiceField(choices=CHOICES, required=True )

    #image = forms.ImageField()

class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': 'Comment'
        }
