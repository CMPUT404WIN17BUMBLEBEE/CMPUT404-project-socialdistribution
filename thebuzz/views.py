from urlparse import urlparse

from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404,JsonResponse,HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import timedelta


from .forms import PostForm, CommentForm, ProfileForm
from .serializers import *
from django.core.urlresolvers import reverse
import CommonMark
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import dateutil.parser
import json
import requests
from django.db.models import Lookup
from itertools import chain
from django.forms import model_to_dict
import base64

from django.contrib.sites.models import Site
from django.core import serializers
import io
import imghdr

from authorization import is_authorized_to_read_post, get_readable_posts, is_following


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
		except:
			#Setting isPostData to False since that site didn't have the data
			foundProfile = False
			pass

		#Check if we found the object and break out of searching for it
		if foundProfile:
			break

	if request.method == 'POST':
		friend_serializer = FriendSerializer(data=profile)
		friend_serializer.is_valid(raise_exception=True)
		friend_serializer.save()
		friend = Friend.objects.get(id=profile['id'])

		# follow that person
		author = request.user.profile
		author.following.add(friend)

		# send the friend request
		api_user = get_object_or_404(Site_API_User, api_site__contains=friend.host)
		api_url = api_user.api_site + "friendrequest/"
		data = {
			"query": "friendrequest",
			"author": {
				"id": author.url,
				"url": author.url,
				"host": author.host,
				"displayName": author.displayName,
			},
			"friend": {
				"id": friend.url,
				"url": friend.url,
				"host": friend.host,
				"displayName": friend.displayName,
			}
		}
		resp = requests.post(api_url, data=json.dumps(data), auth=(api_user.username, api_user.password),
							 headers={'Content-Type': 'application/json'})

	following = False
	try:
		request.user.profile.following.get(id=profile_id)
		following = True
	except Friend.DoesNotExist:
		pass

	return render(request, 'profile/profile.html', {'profile': profile, 'following': following} )



@login_required(login_url = '/login/')
@transaction.atomic
def edit_profile(request, profile_id):
	if request.method == 'POST':
		profile = Profile.objects.get(id =profile_id)
		form = ProfileForm(request.POST, instance=profile)
		form.save()

		return render(request, 'profile/profile.html', {'profile': profile} )
	else:
		profile = Profile.objects.get(id = profile_id )
		form = ProfileForm(instance=profile)

	return render(request, 'profile/edit_profile_form.html', {'form': form})
# END PROFILE VIEWS



# ------------ FRIENDS VIEWS ---------------------
def friends (request):
	invalid_url = False
	existed = False
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
			friend_data = [author for author in authors if str(author['id'])==request.POST['befriend']][0]
			invalid_url = False
		elif request.POST.get("button2"):
			#profile_url = "http://127.0.0.1:8000/api/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e"
			profile_url = str(request.POST['befriendremote'])
			try:
				host = urlparse(profile_url).hostname
				api_user = Site_API_User.objects.get(api_site__contains=host)
				resp = requests.get(profile_url, auth=(api_user.username, api_user.password))
				friend_data = resp.json()
				# for url in id field
				id = str(friend_data.get('id')).split('author/')[-1]
				id = id.replace('/', '')
				friend_data['id'] = id

				invalid_url = False
			except Exception:
				invalid_url = True
				# raise e
		else:
			friend = request.user.profile.following.get(id=request.POST['id'])
			existed = True
			invalid_url = False

		if not invalid_url:
			author = request.user.profile
			if not existed:
				friend_serializer = FriendSerializer(data=friend_data)
				friend_serializer.is_valid(raise_exception=True)
				friend_serializer.save()
				friend = Friend.objects.get(id=friend_data['id'])

				# follow that person
				author.following.add(friend)

			# send the friend request
			api_user = get_object_or_404(Site_API_User, api_site__contains=friend.host)
			api_url = api_user.api_site + "friendrequest/"
			data = {
				"query": "friendrequest",
				"author": {
					"id": author.url,
					"url": author.url,
					"host": author.host,
					"displayName": author.displayName,
				},
				"friend": {
					"id": friend.url,
					"url": friend.url,
					"host": friend.host,
					"displayName": friend.displayName,
				}
			}
			resp = requests.post(api_url, data=json.dumps(data), auth=(api_user.username, api_user.password), headers={'Content-Type':'application/json'})

	# get all the people I am currently following
	following = request.user.profile.following.all()

	# get all the people that are following me, that I am not friends with yet
	friend_requests = request.user.profile.friend_request.all()

	real_friends = list()
	for following_friend in following:
		#local friends
		try:
			author = Profile.objects.get(id=following_friend.id)
			author.following.get(id=request.user.profile.id)
			real_friends.append(following_friend)
			continue
		except:
			pass

		#remote friends
		try:
			url = request.user.profile.url
			url = url.replace('https://', '').replace('http://', '')
			api_user = Site_API_User.objects.get(api_site__contains=following_friend.host)
			# api_url = api_user.api_site + "author/" + str(following_friend.id) + '/friends/'  + str(request.user.profile.id) + '/'
			api_url = api_user.api_site + "author/" + str(following_friend.id) + '/friends/'  + url
			if not api_url.endswith('/'):
				api_url = api_url + '/'
			resp = requests.get(api_url, auth=(api_user.username, api_user.password),
							 headers={'Content-Type': 'application/json'})
			if json.loads(resp.content).get('friends'):
				real_friends.append(following_friend)
		except Exception as e:
            # team4 connection
			try:
				api_user = Site_API_User.objects.get(api_site__contains=following_friend.host)
				api_url = api_user.api_site + "author/" + str(following_friend.id) + '/friends/'  + str(request.user.profile.id) + '/'
				resp = requests.get(api_url, auth=(api_user.username, api_user.password),
									headers={'Content-Type': 'application/json'})
				if json.loads(resp.content).get('friends'):
					real_friends.append(following_friend)
			except:
				pass
			# print(e)
			continue

	return render(request, 'friends/friends.html',{'authors': authors, 'following': following, 'friend_requests': friend_requests, 'real_friends': real_friends, 'invalid_url': invalid_url })

def delete_friend (request, profile_id):
	friend = Friend.objects.get(pk=profile_id)
	request.user.profile.following.remove(friend)
	return HttpResponseRedirect(reverse('friends'))

def accept_request (request, profile_id):
	friend = Friend.objects.get(pk=profile_id)
	request.user.profile.following.add(friend)
	request.user.profile.friend_request.remove(friend)
	return HttpResponseRedirect(reverse('friends'))

def delete_request (request, profile_id):
	friend = Friend.objects.get(pk=profile_id)
	request.user.profile.friend_request.remove(friend)
	return HttpResponseRedirect(reverse('friends'))

# ----------- END FRIENDS VIEWS -------------



# POSTS AND COMMENTS
#parts of code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/
@ensure_csrf_cookie
@login_required(login_url = '/login/')
def posts(request):
	post_list = list()

	author = request.user.profile

	# retrieve posts from node sites
	sites = Site_API_User.objects.all()
	for site in sites:
		api_user = site.username
		api_password = site.password
		api_url = site.api_site + "author/posts/"

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
				if not p['unlisted']:
					post_list.append(p)
		except Exception:
			continue

	results = get_readable_posts(author, post_list)
	#createGithubPosts(author)

	context = {
		'post_list': results,
		'author_id': str(author.id)
	}

	context['user_obj'] = request.user

	return render(request, 'posts/posts.html', context)

#def createFriendsGithubs(request):
@login_required(login_url = '/login/')
def createGithubPosts(request):
#generates the github posts of your friends. (visibility for github posts are FRIENDS so only get friend github posts!)
	#creates and returns a list of posts of ones that haven't been posted yet
    if request.user.is_authenticated:
        if request.method == 'GET':

	    user = request.user.profile
	    friends = []
	    following = user.following.all()
	    
	    w = 0
	    for person in following:
	    #while(w<len(following)):
	    
		if (is_following(request.get_host(), user.id, str(person.id))):
		    friends.append(person)
		#w += 1

	    #next, get their githubs, if they have them, otherwise don't bother keeping them
	    fgithubs = []
	    all_profiles = [] #a list of all profiles including yours so that you can use them when making the posts
	    
	    mostRecent = [] #keeps track of most recent post by each friend
	    index = 0
	    while(index<len(friends)):
		tmp =  Profile.objects.get(id=friends[index].id).github
		if(tmp.strip()):
		    all_profiles.append(Profile.objects.get(id = friends[index].id))
		    mostRecent.append(Post.objects.filter(title = "Github Activity", associated_author=all_profiles[-1]).order_by('-published').first())
		    
		    fgithubs.append(tmp)
		index += 1

	    if(user.github.strip()): #your own github posts are retrieved too!
		mostRecent.append(Post.objects.filter(title = "Github Activity", associated_author =user.id).order_by('-published').first())
		fgithubs.append(user.github)
		all_profiles.append(user)

	    jdata = []
	    index = 0
	    
	    while(index<len(fgithubs)):
		name = fgithubs[index].split("/")[-1]
		resp = requests.get("https://api.github.com/users/" + name + "/events") #gets newest to oldest events
	
		jdata.append(resp.json())
		
		if('documentation_url' in jdata[index]): #limit has been exceeded, wait 1 hour
		    print "Wait an hour -- Github request limit exceeded"
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

				#make posts for the database
			lilavatar = "<img class = 'githubAvatar' src='" + avatars[-1] + "'/>"
			post = Post.objects.create(title = gtitle,
				      content= lilavatar + "<p>" + contents[-1] ,
				      published=pubtime[-1],
				      associated_author = all_profiles[index2],
				      source = request.META.get('HTTP_REFERER'),#should pointto author/postid
				      origin = request.META.get('HTTP_REFERER'),
				      description = contents[-1][0:97] + '...',
				      visibility = 'FRIENDS',
				      visibleTo = '',
							       )
			myImg = Img.objects.create(associated_post = post,
			 				       myImg = lilavatar )
			post.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
			post.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
			post.save()
			postlist.append(post)
			
		    index2 +=1


			#if there is nothing new to send, send an empty array
	if(len(postlist) is 0):
		return HttpResponse(status=204)

	#prepare the new posts to be sent to the Ajax
	jtmp = []

	index = 0
	while(index<len(postlist)):
		jtmp.append(model_to_dict(postlist[index]))
		
		jtmp[index]['image'] = ""#base64.b64encode(jtmp[index]['image']) TODO fix me
		jtmp[index]['associated_author'] = str(Profile.objects.get(id = jtmp[index]['associated_author']).id)
		jtmp[index]['id'] = str(postlist[index].id)
		jtmp[index]['published'] = json.dumps(dateutil.parser.parse(pubtime[index] ).strftime('%B %d, %Y, %I:%M %p'))
		jtmp[index]['published'] = jtmp[index]['published'][1:-1]
		jtmp[index]['displayName'] = str(Profile.objects.get(id = jtmp[index]['associated_author']).displayName)
		jtmp[index]['currentId'] = str(user.id) #current logged in user's id #
		index += 1

        return HttpResponse(json.dumps(jtmp),content_type = "application/json")
    else:
	return HttpResponse(status=401)

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
		except:
			#Setting isPostData to False since that site didn't have the data
			isPostData = False
			pass


		#Check if we found the object and break out of searching for it
		if isPostData and not post == {u'detail': u'Not found.'}:
			break

	# for team4
	if post.get('id') is None:
		post = post['posts'][0]

	post['id'] = [x for x in post['id'].split("/") if x][-1]
	post['author']['id'] = [x for x in post['author']['id'].split("/") if x][-1]

	return post



@login_required(login_url = '/login/')
def post_action(request, post_id):


	if request.method == 'DELETE':
		post = Post.objects.get(id = post_id)

		if post == {} or post == {u'detail': u'Not found.'}:
			return HttpResponse(status = 404)
		else:
			post.delete()
			return HttpResponse(status = 204)
	else:
		post = get_Post(post_id)


        if request.method == 'GET':

	    post = get_Post(post_id)
	    #Check that we did find a post, if not raise a 404
	    if post == {} or post == {u'detail': u'Not found.'}:
		return HttpResponse(status=404)

	    if is_authorized_to_read_post(request.user.profile, post):
		post['published'] = json.dumps(dateutil.parser.parse(post['published'] ).strftime('%B %d, %Y, %I:%M %p'))
		#post['published'] = dateutil.parser.parse(post.get('published'))
		for comment in post['comments']:
		    comment['published'] = json.dumps(dateutil.parser.parse(comment['published'] ).strftime('%B %d, %Y, %I:%M %p'))

		    #remove quotations around comment and date
		    comment['published'] = comment['published'][1:-1]
		    comment['comment'] = comment['comment'][1:-1]

		#Posts returned from api's have comments on them no need to retrieve them separately
		post["currentId"] = str(request.user.profile.id);
		return HttpResponse(json.dumps(post),content_type = "application/json")
	    else:
		return HttpResponse(status=403)

@login_required(login_url='/login/')
def my_post_delete(request, profile_id, post_id):
	if request.method == 'DELETE':
		try:
			post = Post.objects.get(id=post_id)
			post.delete()
			return HttpResponse(status=204)
		except:
			return HttpResponse(status=404)

#code from http://pythoncentral.io/writing-simple-views-for-your-first-python-django-application/
@login_required(login_url = '/login/')
def post_detail(request, post_id):
		post = get_Post(post_id)
		#Check that we did find a post, if not raise a 404
		if post == {} or post == {u'detail': u'Not found.'}:
			raise Http404

		if is_authorized_to_read_post(request.user.profile, post):
			post['published'] = dateutil.parser.parse(post.get('published'))

			for comment in post['comments']:
				comment['published'] = dateutil.parser.parse(comment.get('published'))

			#Posts returned from api's have comments on them no need to retrieve them separately
			return render(request, 'posts/detail.html', {'post': post})
		else:
			return HttpResponseForbidden()

@login_required(login_url = '/login/')
def edit_post(request, post_id):
	if request.method == 'POST':
		post = Post.objects.get(id = post_id)
		form = PostForm(request.POST, request.FILES, instance=post)

		parser = CommonMark.Parser()
		renderer = CommonMark.HtmlRenderer()

		# If data is valid, proceeds to create a new post and redirect the user
		if form.is_valid():
			title = form.cleaned_data['title']
			title = makeSafe(title)
			content = form.cleaned_data['content']
			markdown = form.cleaned_data['markdown']
			description = ''


			if markdown:
				html = content
				contentType = 'text/markdown'

			else:
				html = makeSafe(content)
				contentType = 'text/plain'

			#protective measures applied here
			description = html

			if(len(description) >= 97):
				description = description[0:97] + '...'

			published = timezone.now()

			image = ''
			if 'image' in request.FILES:
				image = request.FILES['image']

			visibility = form.cleaned_data['visibility']
			visible_to = ''

			if(visibility == 'PRIVATE'):
				#glean the users by commas for now
				entries = form.cleaned_data['visibleTo']
				entries = entries.split(',')

				for item in entries:
					visible_to += item
			c = ''
			categories = form.cleaned_data['categories']

			if categories:
				cats = categories.split(',')

				for item in cats:
					item = makeSafe(item)
					c += item

			if image:
				#create second post here - Posts and Img objects!
				cType = imghdr.what(image)

				if(cType == 'png'):
					contentType2 = 'image/png;base64'
				elif(cType == 'jpeg'):
					contentType2 = 'image/jpeg;base64'

				f = image.read()
				byteString = bytearray(f)
				encodeImage = base64.b64encode(byteString)

				post2 = Post.objects.create(title = title,
						content='data:' + contentType2 + ',' + encodeImage,
						published=published,
						associated_author = request.user.profile,
						source = request.META.get('HTTP_REFERER'),#should pointto author/postid
						origin = request.META.get('HTTP_REFERER'),
						description = description,
						visibility = visibility,
						visibleTo = visible_to,
						categories = c,
						unlisted = True,

						)

				#don know if i need this anymore...
				myImg = Img.objects.create(associated_post = post2, myImg = image)

				post2.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post2.id) })
				post2.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post2.id) })

				post2.save()

				post.contentType = 'text/markdown'
				html = html + '  \n![](' + post2.content + ')'
			#can't make a whole new post for images, will look funny. Try this??
			#else:
			#create a Post without an image here!
			post.title = title
			post.content = html
			post.published = published
			post.source = request.META.get('HTTP_REFERER');#should pointto author/postid
			post.origin = request.META.get('HTTP_REFERER');
			post.description = description
			post.visibility = visibility
			post.visibleTo = visible_to
			post.categories = c
			post.unlisted = form.cleaned_data['unlisted']

			post.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
			post.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })

			post.save()

			# if image:
			# 	#attach image post to regular post
			# 	#Asked Braedy about doing this and he suggested markdown, so will try that
			# 	#post2.content += '\n ![' + post2.description + '](' + post.content + ')'
			# 	post.content += '\n <div><img src=' + post2.content + '></img></div>'
			# post.save()

			return redirect('/posts')
	else:
		post = Post.objects.get(id = post_id)
		form = PostForm(instance=post)

	return render(request, 'posts/edit_post.html', {'form': form, 'post_id': post_id})
@ensure_csrf_cookie
@login_required(login_url = '/login/')
def add_comment(request, post_id):
	post = get_Post(post_id)
	#Check that we did find a post, if not raise a 404
	if post == {} or post == {u'detail': u'Not found.'}:
		return HttpResponse(status=404)

	author = Profile.objects.get(user_id=request.user.id)

	if request.method == 'POST':
		#now accepts comments without the need for forms or csrf validation
		postedComment = json.dumps(request.body)
		try:
			post_host = post.get('author').get('host')
			api_user = Site_API_User.objects.get(api_site__contains=post_host)
			api_url = api_user.api_site + 'posts/' + str(post_id) + '/comments/'
			data = {
					"query": "addComment",
					"post": api_user.api_site + 'posts/' + str(post_id) + '/',
					"comment":{
						"author": {
							"id": author.url,
							"url": author.url,
							"host": author.host,
							"displayName": author.displayName,
							"github": author.github
						},
						"comment": postedComment,
						"contentType": "text/plain",
						"published":str(datetime.now()),
						"id":str(uuid.uuid4())
					}
			}

			resp = requests.post(api_url, data=json.dumps(data), auth=(api_user.username, api_user.password),
							 headers={'Content-Type': 'application/json'})
		except Exception as e:
			# print("Error: views-addingcomment   "+ str(e))
			pass

		newpost = get_Post(post_id) #get the version with the new comment in it


		if newpost == {} or newpost == {u'detail': u'Not found.'}:
			return HttpResponse(status=404)

		newcomment = newpost["comments"][0]
		newcomment['published'] = json.dumps(dateutil.parser.parse(newcomment['published'] ).strftime('%B %d, %Y, %I:%M %p'))
		#remove quotations around comment and date
		newcomment['published'] = newcomment['published'][1:-1]
		newcomment['comment'] = newcomment['comment'][1:-1]
		newcomment["currentId"] = str(request.user.profile.id);

		if(resp.status_code == 200):
			resp = JsonResponse(newcomment)
			resp.status_code = 201
			return resp
		if(resp.status_code == 404):
			return HttpResponse(status=404)
		if(resp.status_code == 403):
			return HttpResponse(status=403)
		if(resp.status_code == 500):
			return HttpResponse(status=500)

@login_required(login_url = '/login/')
def delete_comment(request, comment_id):
	if request.method == 'DELETE':
		#delete a comment of your own
		try:
			comment = Comment.objects.get(id = comment_id)
			comment.delete()
			return HttpResponse(status=204)
		except:
			return HttpResponse(status = 404)



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
			description = ''


			if markdown:
				html = content
				contentType = 'text/markdown'

			else:
				html = makeSafe(content)
				contentType = 'text/plain'
			#protective measures applied here

			description = html

			if(len(description) >= 97):
				description = description[0:97] + '...'
			published = timezone.now()

			image = ''
			if 'image' in request.FILES:
				image = request.FILES['image'] #form.cleaned_data['image_upload']

			visibility = form.cleaned_data['visibility']
			visible_to = ''

			if(visibility == 'PRIVATE'):
				#glean the users by commas for now
				entries = form.cleaned_data['visibleTo']
				#visible_to = form.cleaned_data['privacy_textbox']
				entries = entries.split(',')

				for item in entries:
					visible_to += item

			c = ''
			categories = form.cleaned_data['categories']
			if categories:
				cats = categories.split(',')

				for item in cats:
					item = makeSafe(item)
					c += item

			print 'checking for an image'
			if image:
				print 'i found an image'
				#create second post here - Posts and Img objects!
				cType = imghdr.what(image)
				if(cType == 'png'):
					contentType2 = 'image/png;base64'
				elif(cType == 'jpeg'):
					contentType2 = 'image/jpeg;base64'

				f = image.read()
				byteString = bytearray(f)
				encodeImage = base64.b64encode(byteString)

				post = Post.objects.create(title = title,
					content='data:' + contentType2 + ',' + encodeImage,
					contentType=contentType2,
					published=published,
					associated_author = request.user.profile,
					source = request.META.get('HTTP_REFERER'),#should pointto author/postid
					origin = request.META.get('HTTP_REFERER'),
					description = description,
					visibility = visibility,
					visibleTo = visible_to,
					categories = c,
					unlisted = True,
					)
				#don know if i need this anymore...
				myImg = Img.objects.create(associated_post = post,
					 myImg = image )

				post.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
				post.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post.id) })
				print 'i made an image'
				post.save()

				contentType = 'text/markdown'
				html = html + '  \n![](' + post.content + ')'
				#can't make a whole new post for images, will look funny. Try this??
				#else:
				#create a Post without an image here!
			post2 = Post.objects.create(title = title,
				content=html ,
				contentType = contentType,
				published=published,
				associated_author = request.user.profile,
				source = request.META.get('HTTP_REFERER'),
				origin = request.META.get('HTTP_REFERER'),
				description = description,
				visibility = visibility,
				visibleTo = visible_to,
				categories = c,
				unlisted = form.cleaned_data['unlisted'],
				)

			#update post object to proper origin and source
			post2.origin = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post2.id) })
			post2.source = 'http://' + request.get_host() + '/api' + reverse('post_detail', kwargs={'post_id': str(post2.id) })
			post2.save()

			#if image:
			#attach image post to regular post
			#Asked Braedy about doing this and he suggested markdown, so will try that
			#post2.content += '\n ![' + post2.description + '](' + post.content + ')'
			#  post2.content += '\n <div><img src=' + post.content + '></img></div>'
			#post2.save()

			return redirect('/posts')

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

def DeletePost(request, post_id):
   post = get_object_or_404(Post, pk=post_id).delete()
   return HttpResponseRedirect(reverse('posts'))

@login_required(login_url = '/login/')
def author_post(request, profile_id):
	post_list = list()
	author = request.user.profile

	api_user = Site_API_User.objects.get(api_site__contains=request.get_host())
	api_url = api_user.api_site + "author/" + profile_id + "/posts/"
	resp = requests.get(api_url, auth=(api_user.username, api_user.password))
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
		pass

	results = get_readable_posts(author, post_list)
	# createGithubPosts(author)

	context = {
		'post_list': results,
		'author_id': str(author.id)
	}

	context['user_obj'] = request.user

	return render(request, 'posts/my_posts.html', context)

# END POSTS AND COMMENTS
