#code from http://pythoncentral.io/how-to-use-python-django-forms/

from django import forms
from datetime import datetime
 
class PostForm(forms.Form):
    posted_text = forms.CharField(max_length=2000)
    date_created = forms.DateTimeField()

class CommentForm(forms.Form):
    comment = forms.CharField(max_length=2000)
    date_created = forms.DateTimeField()
