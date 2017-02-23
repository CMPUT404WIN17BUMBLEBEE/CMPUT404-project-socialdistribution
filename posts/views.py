from django.shortcuts import render

from django.http import HttpResponse
from .models import Post, Comment

# Create your views here.

def index(request):

	latest_posts_list = Post.objects.order_by('-pub_date')[:5]

	context = {
	
	'lastest_posts_list': latest_posts_list

	}

	return render(request, 'posts/index.html', context)
