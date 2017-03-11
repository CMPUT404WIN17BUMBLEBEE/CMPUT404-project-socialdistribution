from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.template import Context, loader
from .models import Post, Comment, Profile
from .forms import PostForm, CommentForm, ProfileForm
from django.core.urlresolvers import reverse
from django.db import transaction
from django.contrib.auth import logout
from django.views.generic.edit import DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone

#------------------------------------------------------------------
# SIGNING UP

def register(request):
     if request.method == 'POST':
         form = UserCreationForm(request.POST)

         if form.is_valid():
             username = form.cleaned_data['username']
             password = make_password(form.cleaned_data['password1'], salt=None, hasher='default')
             user = User.objects.create(username=username, password=password)

             profile = Profile.objects.get(user_id=user.id)
             profileForm = ProfileForm(request.POST, instance=profile)
             profileForm.save()

             return HttpResponseRedirect('/register/complete')

     else:
         form = UserCreationForm()
         profileForm = ProfileForm()
     token = {}
     token.update(csrf(request))
     token['form'] = form
     token['profileForm'] = profileForm

     return render_to_response('registration/registration_form.html', token)

def registration_complete(request):
     return render_to_response('registration/registration_complete.html')
# END LOGIN VIEWS------------------------------------------------------------------------------------------

# PROFILE VIEWS
@login_required(login_url = '/login/')
def profile(request):
    profile = Profile.objects.get(user_id=request.user.id)
    return render(request, 'profile/profile.html', {'profile': profile})

@login_required(login_url = '/login/')
@transaction.atomic
def edit_profile(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user_id=request.user.id)
        form = ProfileForm(request.POST, instance=profile)
        form.save()

        return redirect('profile')
    else:
        profile = Profile.objects.get(user_id=request.user.id)
        form = ProfileForm(instance=profile)

    return render(request, 'profile/edit_profile_form.html', {'form': form})
# END PROFILE VIEWS

# POSTS AND COMMENTS
#parts of code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/
@login_required(login_url = '/login/')
def posts(request):
	two_days_ago = datetime.utcnow() - timedelta(days=2)

	latest_posts_list = Post.objects.filter(date_created__gt=two_days_ago).all()

	#template = loader.get_template('index.html')

	context = {

	'latest_posts_list': latest_posts_list

	}

	return render(request, 'posts/posts.html', context)

#code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/

def post_detail(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        # If no Post has id post_id, we raise an HTTP 404 error.
        raise Http404

    try :
        comments  = Comment.objects.filter(associated_post=post_id)
    except Comment.DoesNotExist:
        comments = Comment.objects

    return render(request, 'posts/detail.html', {'post': post, 'comments': comments})


def add_comment(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    author = Profile.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.content = form.cleaned_data['content']
            comment.author = author
            comment.associated_post = post
            comment.date_created = timezone.now()
            comment.save()

        return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id}))

    else:
        form = CommentForm()

    return render(request, 'posts/add_comment.html', {'form': form, 'post': post})


#code from http://pythoncentral.io/how-to-use-python-django-forms/
def post_form_upload(request):
    if request.method == 'GET':
        form = PostForm()
    else:
        # A POST request: Handle Form Upload
        form = PostForm(request.POST) # Bind data from request.POST into a PostForm

        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            posted_text = form.cleaned_data['posted_text']
            date_created = form.cleaned_data['date_created']
            post = Post.objects.create(posted_text=posted_text,
                                         date_created=date_created)
            return HttpResponseRedirect(reverse('post_detail',
                                                kwargs={'post_id': post.id}))

    return render(request, 'posts/post_form_upload.html', {
        'form': form,
    })

#again parts of code from
#http://pythoncentral.io/writing-views-to-upload-posts-for-your-first-python-django-application/
# NOT WORKING
def post_upload(request):
	if request.method =='GET':

		two_days_ago = datetime.utcnow() - timedelta(days=2)

		latest_posts_list = Post.objects.filter(date_created__gt=two_days_ago).all()

		#template = loader.get_template('index.html')

		context = {

		'post_upload': latest_posts_list

		}

		return render(request, 'posts/post_form_upload.html', context)
	elif request.method == 'POST':
		#fix after GET is working...
		post = Post.objects.create(content=request.POST['posted_text'],
			date_created=datetime.utcnow() )
		return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id}))

def DeletePost(request, post_id):
   post = get_object_or_404(Post, pk=post_id).delete()
   return HttpResponseRedirect(reverse('posts'))


# Based on http://www.django-rest-framework.org/tutorial/quickstart/
from rest_framework import viewsets
from .serializers import PostSerializer, CommentSerializer
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

# END POSTS AND COMMENTS
