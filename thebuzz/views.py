from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.template import Context, loader
from .models import Post, Comment, Profile
from .forms import PostForm, CommentForm, ProfileForm
from django.core.urlresolvers import reverse
import CommonMark
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

#for showing the home page/actually logging in
#3 ways to get here:
#-logged in
#-already logged in, used a cookie
#-registered
#edited code from here to log a user in (https://www.fir3net.com/Web-Development/Django/django.html)
@login_required(login_url = '/login/')
def homePage(request):
	 #if this person has just logged in
    if request.method == 'POST': #for testing purposes only
        
        # get the person i want to follow
        friend = User.objects.get(username = request.POST['befriend'])
        friend_profile = Profile.objects.get(pk=friend.id)

        # follow that person
        request.user.profile.follow(friend_profile)
        friend_profile.add_user_following_me(request.user.profile)

    users = User.objects.all() #for testing purposes only
    
    # get all the people I am currently following
    following = request.user.profile.get_all_following()

    # get all the people that are following me, that I am not friends with yet
    followers = request.user.profile.get_all_followers()

    friends = request.user.profile.get_all_friends()

    return render(request, 'friends/friends.html',{'users': users, 'following': following, 'followers': followers, 'friends': friends  })
		

	 #else: #change this later to account for the other 2 cases ******
	 #	return render_to_response('registration/login.html')

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



# ------------ FRIENDS VIEWS ---------------------
def friends (request):
    #TODO: add retrieval of friends list and such for viewing

    context = {
	   #TODO: add your objects here you want to display in the form
	}

    return render(request, 'friends/friends.html', context)

def add_friends (request):
    if request.method == 'POST':
        #TODO: Retrieve form data and save to model
        return redirect('friends')
    else:
        #TODO: Retrieve set correct form
        form = ""

    return render(request, 'profile/edit_profile_form.html', {'form': form})

# ----------- END FRIENDS VIEWS -------------



# POSTS AND COMMENTS
#parts of code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/
@login_required(login_url = '/login/')
def posts(request):
	two_days_ago = datetime.utcnow() - timedelta(days=2)

	latest_posts_list = Post.objects.filter(published__gt=two_days_ago).all()

	#template = loader.get_template('index.html')

	context = {
	   'latest_posts_list': latest_posts_list
	}

	return render(request, 'posts/posts.html', context)

#code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/
@login_required(login_url = '/login/')
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

    displayName = Profile.objects.get(user_id=post.associated_author).displayName
    return render(request, 'posts/detail.html', {'post': post, 'comments': comments, 'post_author': displayName})


@login_required(login_url = '/login/')
def add_comment(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    author = Profile.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.content = form.cleaned_data['content']
            comment.author = Profile.objects.get(pk=request.user.id)
            comment.associated_post = post
            comment.date_created = timezone.now()
            comment.save()


            return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': str(post.id) }))


    else:
        form = CommentForm()


    return render(request, 'posts/add_comment.html', {'form': form, 'post': post})


#code from http://pythoncentral.io/how-to-use-python-django-forms/

#CommonMark code help from: https://pypi.python.org/pypi/CommonMark
@login_required(login_url = '/login/')
def post_form_upload(request):
    if request.method == 'GET':
        form = PostForm()
    else:
        # A POST request: Handle Form Upload
        form = PostForm(request.POST) # Bind data from request.POST into a PostForm

	parser = CommonMark.Parser()
	renderer = CommonMark.HtmlRenderer()

        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            ast = parser.parse(content)
            html = renderer.render(ast)
            published = timezone.now()
            post = Post.objects.create(title = title,
                                       content=html,
                                       published=published,
				       associated_author = request.user,
				       source = request.META.get('HTTP_REFERER'),
				       origin = 'huh',
				       description = content[0:97] + '...',
				       visibility = form.cleaned_data['choose_Post_Visibility'],
                                       )
            return HttpResponseRedirect(reverse('post_detail',
                                                kwargs={'post_id': str(post.id) }))

    return render(request, 'posts/post_form_upload.html', {
        'form': form,
    })


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
