#code from http://pythoncentral.io/how-to-use-python-django-forms/

from django import forms
from datetime import datetime
 
class PostForm(forms.Form):
    title = forms.CharField(max_length = 100)
    content = forms.CharField(max_length=2000)
    published = forms.DateTimeField()

    #CHOICES=[('select1','select 1'),
    #     ('select2','select 2')]

    #radio = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

class CommentForm(forms.Form):
    comment = forms.CharField(max_length=2000)
    date_created = forms.DateTimeField()
