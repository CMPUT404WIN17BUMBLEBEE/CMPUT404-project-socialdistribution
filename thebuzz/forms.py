#code from http://pythoncentral.io/how-to-use-python-django-forms/

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Textarea, ChoiceField
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

class PostForm(forms.ModelForm):
    markdown = forms.BooleanField(required=False)
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'visibility', 'visibleTo', 'categories', 'unlisted']

        CHOICES=(('PUBLIC','Public'),
            ('FRIENDS','Friends'),
            ('FOAF', 'Friend of A Friend'),
            ('PRIVATE', 'Private'),
            ('SERVERONLY', 'Friends on this server only'))

        labels = {
            'visibleTo': 'Visible to (separate with a comma)',
            'categories': 'Categories (separate with a comma)'
        }

        widgets = {
            'visibility': forms.Select(choices=CHOICES, attrs={'onChange':'privacyBox(this)', 'id': 'vis_dropdown'}),
            'visibleTo': forms.TextInput(attrs={'id': 'privacy_textbox', 'display': 'hidden'})
        }

class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['comment']
        labels = {
            'comment': 'Comment'
        }
        widgets = {
            'comment':Textarea(attrs={'cols': 70, 'rows': 10})
        }
