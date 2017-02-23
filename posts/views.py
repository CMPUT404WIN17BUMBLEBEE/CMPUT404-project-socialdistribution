from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template import Context, loader
from .models import Post, Comment

# Create your views here.

#parts of code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/

def index(request):
	two_days_ago = datetime.utcnow() - timedelta(days=2)

	latest_posts_list = Post.objects.filter(date_created__gt=two_days_ago).all()

	#template = loader.get_template('index.html')

	context = {
	
	'latest_posts_list': latest_posts_list

	}

	return render(request, 'posts/index.html', context)
