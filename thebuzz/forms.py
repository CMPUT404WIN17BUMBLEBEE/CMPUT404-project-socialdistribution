#code from http://pythoncentral.io/how-to-use-python-django-forms/

from django import forms
from django.core.exceptions import ValidationError
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

    # def __init__(self, *args, **kwargs):
    #     super(ProfileForm, self).__init__(*args, **kwargs)
    #
    #     self.fields['displayName'].error_messages = {'null':'Display name is required.', 'blank':'Display name is required.', 'required':'Display name is required.'}

class PostForm(forms.Form):
    title = forms.CharField(max_length = 100)
    content = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'cols': 70, 'rows': 10}))

    CHOICES=[('PUBLIC','Public'),
         ('FRIENDS','Friends'),
	 ('FOAF', 'Friend of A Friend'),
	 ('PRIVATE', 'Private'),
	 ('SERVERONLY', 'Members of this server only')]

    choose_Post_Visibility = forms.ChoiceField(choices=CHOICES, required=True, widget=forms.Select(attrs={"onChange":'privacyBox(this)', 'id': 'vis_dropdown'}) )

    image_upload = forms.ImageField(label='Image', required=False)

    privacy_textbox = forms.CharField(label='Visible to', required=False, max_length =200, widget=forms.TextInput(attrs={'id': 'privacy_textbox', 'display': 'hidden'}))

    markdown = forms.BooleanField(required=False)

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
