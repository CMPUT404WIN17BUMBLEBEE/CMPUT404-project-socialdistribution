from urlparse import urlparse

from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404,JsonResponse,HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.template import Context, loader
from requests import Response

from .models import *
from .forms import PostForm, CommentForm, ProfileForm
from .serializers import *
from django.core.urlresolvers import reverse
import CommonMark, imghdr
from django.db import transaction
from django.contrib.auth import logout
from django.views.generic.edit import DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db.models import Q
import dateutil.parser
import json
import requests
from django.db.models import Lookup
from itertools import chain
from django.forms import model_to_dict
import base64
from django.contrib.sites.models import Site
from django.core import serializers

#------------------------------------------------------------------
# SIGNING UP

def register(request):
    profileForm = ProfileForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = make_password(form.cleaned_data['password1'], salt=None, hasher='default')
            #sets user to in_active, requiring admin to go in and set them to active before they can log in
            is_active = False
            user = User.objects.create(username=username, password=password, is_active=is_active)

            profile = Profile.objects.get(user_id=user.id)
            profileForm = ProfileForm(request.POST, instance=profile)

            if profileForm.is_valid():
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
def profile(request, profile_id):
    profile = {}

    sites = Site_API_User.objects.all()
    for site in sites:
        api_user = site.username
        api_password = site.password
        api_url = site.api_site + "author/" + profile_id + "/"

        global foundProfile
        foundProfile = True
        profile = {}

        try:
            resp = requests.get(api_url, auth=(api_user, api_password))
            profile = json.loads(resp.text)
            profile['id'] = profile_id

            if resp.status_code == 404:
                foundProfile = False
                pass
        #Results in an AttributeError if the object does not exist at that site
        except  AttributeError:
            #Setting isPostData to False since that site didn't have the data
            foundProfile = False
            pass

        #Check if we found the object and break out of searching for it
        if foundProfile:
            break

    return render(request, 'profile/profile.html', {'profile': profile} )

@login_required(login_url = '/login/')
@transaction.atomic
def edit_profile(request, profile_id):
    if request.method == 'POST':
        profile = Profile.objects.get(id =profile_id) #user_id=request.user.id)
        form = ProfileForm(request.POST, instance=profile)
        form.save()

        return render(request, 'profile/profile.html', {'profile': profile} ) #redirect('profile')
    else:
        profile = Profile.objects.get(id = profile_id ) #user_id=request.user.id)
        form = ProfileForm(instance=profile)

    return render(request, 'profile/edit_profile_form.html', {'form': form})
# END PROFILE VIEWS



# ------------ FRIENDS VIEWS ---------------------
def friends (request):
    invalid_url = False

    authors = list()
    sites = Site_API_User.objects.all()
    for site in sites:
        api_user = site.username
        api_password = site.password
        api_url = site.api_site + "author/"
        resp = requests.get(api_url, auth=(api_user, api_password))
        try:
            profile_list = json.loads(resp.content)
        except Exception:
            continue

        for author in profile_list:
            try:
                author['id'] = uuid.UUID(author.get('id'))
            except Exception:
                pass
            authors.append(author)


    if request.method == 'POST': #for testing purposes only

        # request.user.profile.follow(friend)
        if request.POST.get("button1"):
            # get the person i want to follow
            friend_data = [author for author in authors if author['id']==uuid.UUID(request.POST['befriend'])][0]
            invalid_url = False
        #elif request.POST.get("button2"):
        else:
            #profile_url = "http://127.0.0.1:8000/api/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e"
            profile_url = str(request.POST['befriendremote'])
            try:
                host = urlparse(profile_url).hostname
                api_user = Site_API_User.objects.get(api_site__contains=host)
                resp = requests.get(profile_url, auth=(api_user.username, api_user.password))
                friend_data = resp.json()
                invalid_url = False
            except Exception:
                invalid_url = True
                # raise e

        if not invalid_url:
            friend_serializer = FriendSerializer(data=friend_data)
            friend_serializer.is_valid(raise_exception=True)
            friend_serializer.save()
            friend = Friend.objects.get(id=friend_data['id'])

            # follow that person
            author = request.user.profile
            author.follow(friend)

            # send the friend request
            api_user = get_object_or_404(Site_API_User, api_site__contains=friend.host)
            api_url = api_user.api_site + "friendrequest/"
            data = {
                "query": "friendrequest",
                "author": {
                    "id": str(author.id),
                    "url": author.url,
                    "host": author.host,
                    "displayName": author.displayName,
                },
                "friend": {
                    "id": str(friend.id),
                    "url": friend.url,
                    "host": friend.host,
                    "displayName": friend.displayName,
                }
            }

            resp = requests.post(api_url, data=json.dumps(data), auth=(api_user.username, api_user.password), headers={'Content-Type':'application/json'})

    # get all the people I am currently following
    following = request.user.profile.get_all_following()

    # get all the people that are following me, that I am not friends with yet
    followers = request.user.profile.get_all_followers()

    friends = request.user.profile.get_all_friends()

    return render(request, 'friends/friends.html',{'authors': authors, 'following': following, 'followers': followers, 'friends': friends, 'invalid_url': invalid_url })

def delete_friend (request, profile_id):

    friend = Friend.objects.get(pk=profile_id)
    request.user.profile.unfriend(friend)
    return HttpResponseRedirect(reverse('friends'))

# ----------- END FRIENDS VIEWS -------------



# POSTS AND COMMENTS
#parts of code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/
@login_required(login_url = '/login/')
def posts(request):
    two_days_ago = datetime.now() - timedelta(days=2)

    post_list = list()

    author = request.user.profile

    # retrieve posts from node sites
    sites = Site_API_User.objects.all()
    for site in sites:
        api_user = site.username
        api_password = site.password
        api_url = site.api_site + "author/posts/"
        if "blooming-mountain" in site.api_site:
            api_url = site.api_site + "author/posts"
        resp = requests.get(api_url, auth=(api_user, api_password))
        try:
            data = json.loads(resp.text)
            posts = data["posts"]

            for p in posts:
                split = p['id'].split("/")
                split = [x for x in split if x]
                actual_id = split[-1]
                p['id'] = actual_id

                split = p['author']['id'].split("/")
                split = [x for x in split if x]
                actual_id = split[-1]
                p['author']['id'] = actual_id

                p['published'] = dateutil.parser.parse(p.get('published'))
                post_list.append(p)
        except Exception:
            continue


    results = get_readable_posts(author.id, post_list)

    context = {}

    context = {
        'post_list': results,
        'author_id': str(author.id)
    }

    context['user_obj'] = request.user

    return render(request, 'posts/posts.html', context)


#@login_required(login_url = '/login/')
def DELETEMEcreateGithubPosts(request):
#get github activity of myself - and create posts to store in the database

    #if not request.user.is_authenticated:
	#return HttpResponse(status=204)
    #if request.user.is_authenticated:
	    if request.method == 'GET':
		    user = request.user.profile
		    
		    if not user.github.strip():
			return HttpResponse(status=204)
		    #make a GET request to github for my github name, if I have one
		    if(user.github):

			#first get the most recent github post, so we can stop if we hit this time or later
			postQuery = Post.objects.filter(title = "Github Activity", associated_author = user).order_by('-published').first()

			rurl = 'https://api.github.com/users/' + user.github + '/events'
			resp = requests.get(rurl) #gets newest to oldest events
			jdata = resp.json()
		
			avatars = []
			gtitle = "Github Activity"
			contents = []
			pubtime = []
			count = 0
			postlist = [] #for sending a response

			if('https://developer.github.com/v3/#rate-limiting' in jdata): #limit has been exceeded, wait 1 hour
			    
			    return HttpResponse(status=204)
		
			#get the data
			for item in jdata:
			    if(postQuery is not None):
				    cmpareDate = dateutil.parser.parse(item['created_at'])

				    if(cmpareDate<=postQuery.published): #is the latest github post newer than the retrieved ones?dont create duplicates
					continue

			    avatars.append(item['actor']['avatar_url']) #TODO:implement this after images with text is fixed
			    pubtime.append(item['created_at'])

			    if( "commits" in item['payload'] ):
			    #if there is commit data
				    if( not item['payload']['commits']): #empty commit
					    contents.append(item['type'] + " by " + item['actor']['display_login'] + " in <a href = 'https://github.com/" + item['repo']['name'] + "'> " + item['repo']['name'] + "</a> <br/>")
				    else:
					    contents.append(item['type'] + " by " + item['actor']['display_login'] +" (" + item['payload']['commits'][0]['author']['email'] + ")" + " in <a href = 'https://github.com/" + item['repo']['name'] + "'> " + item['repo']['name'] + "</a> <br/> \"" + item['payload']['commits'][0]['message'] + "\"")
				 #           count += 1
			    else:
			    #there is no commit data
				    contents.append(item['type'] + " by " + item['actor']['display_login'] + " in <a href = 'https://github.com/" + item['repo']['name'] + "'> " + item['repo']['name'] + "</a> <br/>")
			#            count += 1

			#make posts for the database
			for i in range(0,len(contents)):
			    lilavatar = "<img src='" + avatars[i] + "'/>"

			    post = Post.objects.create(title = gtitle,
				                       content= lilavatar + "<p>" + contents[i] ,
				                       published=pubtime[i],
						       associated_author = user,
						       source = 'http://127.0.0.1:8000/',
						       origin = 'huh',
						       description = contents[i][0:97] + '...',
						       visibility = 'FRIENDS',
						       visibleTo = '',
				                       )
			    myImg = Img.objects.create(associated_post = post,
							 myImg = lilavatar )
			    post.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
			    post.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
			    post.save()
			    postlist.append(post)
		
			createFriendsGithubs( request ) #returns postlist of ppl youre following

			#if there is nothing new to send, send an empty array
			if(len(postlist) is 0):	
			    return HttpResponse(status=204)	
	#prepare the new posts to be sent to the Ajax
			jtmp = []
			#print(len(postlist))
			#print(postlist[0].id)
		
			index = 0
			while(index<len(postlist)):
			   
			    jtmp.append(model_to_dict(postlist[index]))
			    #print(jtmp[index])
			    jtmp[index]['image'] = ""#base64.b64encode(jtmp[index]['image']) TODO fix me
			    jtmp[index]['associated_author'] = str(Profile.objects.get(id = jtmp[index]['associated_author']).id)
			    jtmp[index]['id'] = str(postlist[index].id)
			    jtmp[index]['published'] = json.dumps(dateutil.parser.parse(pubtime[index] ).strftime('%B %d, %Y, %I:%M %p'))
			    jtmp[index]['published'] = jtmp[index]['published'][1:-1]
			    jtmp[index]['displayName'] = user.displayName #will have to make two of these to compare if its the current user's or not
			    jtmp[index]['currentId'] = str(user.id) #current logged in user's id #
			    index += 1

			#print(json.dumps(jtmp))
			return HttpResponse(json.dumps(jtmp),content_type = "application/json")

#def createFriendsGithubs(request):
@login_required(login_url = '/login/')
def createGithubPosts(request):
#generates the github posts of your friends. (visibility for github posts are FRIENDS so only get friend github posts!)
#creates and returns a list of posts of ones that haven't been posted yet

    user = request.user.profile
    friends = user.get_all_friends() #array of usernames of my friends
    #next, get their githubs, if they have them, otherwise don't bother keeping them
    fgithubs = []
    mostRecent = [] #keeps track of most recent post by each friend
    index = 0
    while(index<len(friends)):
	tmp =  Profile.objects.get(id=friends[index].id).github
	if(tmp is not ""):
	    mostRecent.append(Post.objects.filter(title = "Github Activity", associated_author =Profile.objects.get(id = friends[index].id)).order_by('-published').first())
	    #print tmp
            fgithubs.append(tmp)
	index += 1

    if(user.github is not ""): #your own github posts are retrieved too!
        mostRecent.append(Post.objects.filter(title = "Github Activity", associated_author =user.id).order_by('-published').first())
	fgithubs.append(user.github)

    jdata = []
    index = 0
    while(index<len(fgithubs)):
        resp = requests.get("https://api.github.com/users/" + fgithubs[index] + "/events") #gets newest to oldest events
	
	jdata.append(resp.json())
	if('https://developer.github.com/v3/#rate-limiting' in jdata[index]): #limit has been exceeded, wait 1 hour
	    return HttpResponse(status=204)

	index += 1


    avatars = []
    gtitle = "Github Activity"
    contents = []
    pubtime = []
    postlist = []
    index2 = 0
    

    #get the data
    while(index2<len(jdata)):
	    for item in jdata[index2]:
		if(mostRecent[index2] is not None):
		    cmpareDate = dateutil.parser.parse(item['created_at'])

		    if(cmpareDate<=mostRecent[index2].published): #is the latest github post newer than the retrieved ones?dont create duplicates
			continue

		avatars.append(item['actor']['avatar_url']) 
		pubtime.append(item['created_at'])

		if( "commits" in item['payload'] ):
		    #if there is commit data
		    if( not item['payload']['commits']): #empty commit
			    contents.append(item['type'] + " by " + item['actor']['display_login'] + " in <a href = 'https://github.com/" + item['repo']['name'] + "'> " + item['repo']['name'] + "</a> <br/>")
		    else:
		        contents.append(item['type'] + " by " + item['actor']['display_login'] +" (" + item['payload']['commits'][0]['author']['email'] + ")" + " in <a href = 'https://github.com/" + item['repo']['name'] + "'> " + item['repo']['name'] + "</a> <br/> \"" + item['payload']['commits'][0]['message'] + "\"")
					 
		else:
		   #there is no commit data
		    contents.append(item['type'] + " by " + item['actor']['display_login'] + " in <a href = 'https://github.com/" + item['repo']['name'] + "'> " + item['repo']['name'] + "</a> <br/>")

	    index2 +=1	
    #make posts for the database
    print len(contents)
    for i in range(0,len(contents)):
	lilavatar = "<img src='" + avatars[i] + "'/>"

	post = Post.objects.create(title = gtitle,
	          content= lilavatar + "<p>" + contents[i] ,
	          published=pubtime[i],
	          associated_author = user,
		  source = 'http://127.0.0.1:8000/',
		  origin = 'huh',
		  description = contents[i][0:97] + '...',
		  visibility = 'FRIENDS',
		  visibleTo = '',
				               )
	myImg = Img.objects.create(associated_post = post,
	 				       myImg = lilavatar )
	post.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
	post.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
	#post.save()
	postlist.append(post)
	print len(postlist)
	    

#if there is nothing new to send, send an empty array
    if(len(postlist) is 0):	
	return HttpResponse(status=204)	
	#prepare the new posts to be sent to the Ajax
    jtmp = []
			#print(len(postlist))
			#print(postlist[0].id)
    #print len(pubtime)		
    index = 0
    while(index<len(postlist)):
			   
       jtmp.append(model_to_dict(postlist[index]))
       #print(jtmp[index])
       jtmp[index]['image'] = ""#base64.b64encode(jtmp[index]['image']) TODO fix me
       jtmp[index]['associated_author'] = str(Profile.objects.get(id = jtmp[index]['associated_author']).id)
       jtmp[index]['id'] = str(postlist[index].id)
       jtmp[index]['published'] = json.dumps(dateutil.parser.parse(pubtime[index] ).strftime('%B %d, %Y, %I:%M %p'))
       jtmp[index]['published'] = jtmp[index]['published'][1:-1]
       jtmp[index]['displayName'] = user.displayName
       jtmp[index]['currentId'] = str(user.id) #current logged in user's id #
       index += 1

    #print(json.dumps(jtmp))
    return HttpResponse(json.dumps(jtmp),content_type = "application/json")
		

def get_Post(post_id):
    post = {}
    sites = Site_API_User.objects.all()

    for site in sites:
        api_url = site.api_site + "posts/" + post_id + "/"

        global isPostData
        isPostData = True
        post = {}
        try:
            api_user = site.username
            api_password = site.password
            resp = requests.get(api_url, auth=(api_user, api_password))
            post = resp.json()

            if resp.status_code == 404:
                isPostData = False
                pass
        #Results in an AttributeError if the object does not exist at that site
        except  AttributeError:
            #Setting isPostData to False since that site didn't have the data
            isPostData = False
            pass

        #Check if we found the object and break out of searching for it
        if isPostData and not post == {u'detail': u'Not found.'}:
            break

    split = post['id'].split("/")
    actual_id = split[0]

    if len(split) > 1:
        actual_id = split[4]

    post['id'] = actual_id

    return post

#code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/
@login_required(login_url = '/login/')
def post_detail(request, post_id):
    post = get_Post(post_id)

    #Check that we did find a post, if not raise a 404
    if post == {} or post == {u'detail': u'Not found.'}:
        raise Http404

    if is_authorized_to_read(request.user.profile.id, post):
        post['published'] = dateutil.parser.parse(post.get('published'))
        for comment in post['comments']:
            comment['published'] = dateutil.parser.parse(comment.get('published'))

        #Posts returned from api's have comments on them no need to retrieve them separately
        return render(request, 'posts/detail.html', {'post': post})
    else:
        return HttpResponseForbidden()


@login_required(login_url = '/login/')
def add_comment(request, post_id):
    post = get_Post(post_id)

    #Check that we did find a post, if not raise a 404
    if post == {} or post == {u'detail': u'Not found.'}:
        raise Http404

    author = Profile.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)

            post_host = post.get('author').get('host')
            if not post_host.endswith("/"):
                post_host = post_host + "/"

            id = str(author.id)
            if not post_host == Site.objects.get_current().domain:
                id = author.url

            api_url = str(post_host) + 'posts/' + str(post_id) + '/comments/'
            data = {
                "query": "addComment",
                "post": post_host + 'posts/' + str(post_id) + '/',
                "comment":{
                    "author": {
                        "id": id,
                        "url": author.url,
                        "host": author.host,
                        "displayName": author.displayName,
                        "github": author.github
                    },
                    "comment":form.cleaned_data['comment'],
                    "contentType": "text/plain",
                    "published":str(datetime.now()),
                    "id":str(uuid.uuid4())
                }
            }

            api_user = Site_API_User.objects.get(api_site=post_host)

            resp = requests.post(api_url, data=json.dumps(data), auth=(api_user.username, api_user.password), headers={'Content-Type':'application/json'})

            return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post_id }))
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
        form = PostForm(request.POST, request.FILES) # Bind data from request.POST into a PostForm

	parser = CommonMark.Parser()
	renderer = CommonMark.HtmlRenderer()

        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            title = form.cleaned_data['title']
	    title = makeSafe(title)
            content = form.cleaned_data['content']
	    markdown = form.cleaned_data['markdown']
	    if markdown:
	      ast = parser.parse(content)
	      html = renderer.render(ast)
	      contentType = 'text/markdown'
	    else:
	      #protective measures applied here
	      html = makeSafe(content)
	      contentType = 'text/plain'
            published = timezone.now()
	    image = form.cleaned_data['image_upload']
	    visibility = form.cleaned_data['choose_Post_Visibility']
	    visible_to = ''

	    if(visibility == 'PRIVATE'):
	      #glean the users by commas for now
	      entries = form.cleaned_data['privacy_textbox']
	      #visible_to = form.cleaned_data['privacy_textbox']
	      entries = entries.split(',')

	      for item in entries:
		visible_to += item
                #visible_to.append(item)


	    if image:
	      #create Posts and Img objects here!
	      #cType = imghdr.what(image.name)
	      #if(cType == 'png'):
	      #  contentType = 'image/png;base64'
	      #elif(cType == 'jpeg'):
	      #	contentType = 'image/jpeg;base64'
	      imgItself = "<img src=\'" + "/images/" + image.name + "\'/>"
              post = Post.objects.create(title = title,
                                       content=html + "<p>" + imgItself,
                                       published=published,
				       associated_author = request.user.profile,
				       source = request.META.get('HTTP_REFERER'),#should pointto author/postid
				       origin = request.META.get('HTTP_REFERER'),
				       description = content[0:97] + '...',
				       visibility = visibility,
				       visibleTo = visible_to,
                                       ) #json.dumps(visible_to)
              myImg = Img.objects.create(associated_post = post,
					 myImg = image )

	      post.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
	      post.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })

	      post.save()

	    #can't make a whole new post for images, will look funny. Try this??
	    else:
	      #create a Post without an image here!
	      post = Post.objects.create(title = title,
                                       content=html ,
                                       published=published,
				       associated_author = request.user.profile,
				       source = request.META.get('HTTP_REFERER'),
				       origin = request.META.get('HTTP_REFERER'),
				       description = content[0:97] + '...',
				       visibility = visibility,
				       visibleTo = visible_to,
                                       ) #json.dumps(visible_to)

	    #update post object to proper origin and source
	    post.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
	    post.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
	    post.save()

	    test = reverse('post_detail', kwargs={'post_id': str(post.id) })


	    return HttpResponseRedirect(reverse('post_detail',
                                                kwargs={'post_id': str(post.id) }))

    return render(request, 'posts/post_form_upload.html', {
        'form': form,
    })

#makes a string of stuff safe to post
def makeSafe(content):

  problematics = ['"', '&', '<', '>']
  #Credit to ghostdog74 for the makeup of this function
  #http://stackoverflow.com/questions/3411771/multiple-character-replace-with-python
  #http://stackoverflow.com/users/131527/ghostdog74
  for c in problematics:
    if c in content:
      if(c == '"'):
        content = content.replace(c, '&quot;')
      elif(c == '&'):
        content = content.replace(c, '&amp;')
      elif(c == '<'):
        content = content.replace(c, '&lt;')
      elif(c == '>'):
        content = content.replace(c, '&gt;')

  return content

#again parts of code from
#http://pythoncentral.io/writing-views-to-upload-posts-for-your-first-python-django-application/
# NOT WORKING
def post_upload(request):
	if request.method =='GET':

		two_days_ago = datetime.now() - timedelta(days=2)

		latest_posts_list = Post.objects.filter(date_created__gt=two_days_ago).all()

		#template = loader.get_template('index.html')

		context = {

		'post_upload': latest_posts_list

		}

		return render(request, 'posts/post_form_upload.html', context)
	elif request.method == 'POST':
		#fix after GET is working...
		post = Post.objects.create(content=request.POST['posted_text'],
			date_created=datetime.now())
		return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id}))

def DeletePost(request, post_id):
   post = get_object_or_404(Post, pk=post_id).delete()
   return HttpResponseRedirect(reverse('posts'))


# END POSTS AND COMMENTS


#CUSTOM QUERY STUFF ------------------------------------------------
#from django.db.models.fields import Field
#Field.register_lookup(Is_My_Friend)


#class Is_My_Friend(Lookup):
#    lookup_name = 'is_my_friend'

#    def as_sql(self, compiler, connection):
#        lhs, lhs_params = self.process_lhs(compiler, connection)
#        rhs, rhs_params = self.process_rhs(compiler, connection)
#        params = lhs_params + rhs_params
#        return '%s <> %s' % (lhs, rhs), params

#END OF CUSTOM QUERY STUFF -----------------------------------------

# Authorization
def is_authorized_to_read(requestor_id, post):
    try:
        requestor_id = uuid.UUID(requestor_id)
    except Exception:
        pass
    # Public
    if post['visibility'] == "PUBLIC":
        return True
    # Private
    if post['visibility'] == "PRIVATE" :
        if str(requestor_id) in post['visibleTo']:
            return True
    try:
        requestor = Profile.objects.get(id=requestor_id)
        # admin
        if requestor.user.is_superuser:
            return True
        # Server Only
        if post['visibility'] == "SERVERONLY" and post['author']['host'] == requestor.host:
            return True
        # Own
        if str(post['author']['id']) == str(requestor_id):
            return True
        #todo: FRIEND AND FOAF =>POST to post/{post.id}
        #todo: check if the post is local?
        # send the friend request
        if post['visibility'] == "FRIENDS" or post['visibility'] == "FOAF":
            try:
                post = Post.objects.get(id=post['id'])
            except Post.DoesNotExist:
                if post['visibility'] == "FOAF":
                    api_user = get_object_or_404(Site_API_User, api_site=post['author']['host'])
                    api_url = api_user.api_site + "posts/" + str(post['id']) + "/"
                    data = {
                        "query": "getPost",
                        "postid": str(post['id']),
                        "url": api_url,
                        "author": {
                            "id": str(requestor.id),
                            "url": requestor.url,
                            "host": requestor.host,
                            "displayName": requestor.displayName,
                        },
                        "friends": [friend.url for friend in requestor.friends.all()]
                    }
                    resp = requests.post(api_url, data=json.dumps(data), auth=(api_user.username, api_user.password),
                                         headers={'Content-Type': 'application/json'})
                    if resp.status_code == 200:
                        return True
                    else:
                        return False
                else: # visibility:friend
                    api_user = get_object_or_404(Site_API_User, api_site=post['author']['host'])
                    api_url = api_user.api_site + "author/" + str(post['author']['id']) + "/friends/" + str(requestor_id) + '/'
                    resp = requests.get(api_url, auth=(api_user.username, api_user.password))
                    try:
                        return json.loads(resp.content).get('friends')
                    except Exception:
                        return False
            else:
                for friend in post.associated_author.friends.all():
                    if friend.id == requestor_id:
                        return True
                    for requestor_friend in requestor.friends.all():
                        if friend.id == requestor_friend.id:
                            return True
    except Profile.DoesNotExist:
        pass

    return False


def get_readable_posts(requestor_id, posts):
    results = list()
    for post in posts:
        if is_authorized_to_read(requestor_id, post):
            results.append(post)
    # Based on code from alecxe
    # http://stackoverflow.com/questions/26924812/python-sort-list-of-json-by-value
    results.sort(key=lambda k: k['published'], reverse=True)
    return results
