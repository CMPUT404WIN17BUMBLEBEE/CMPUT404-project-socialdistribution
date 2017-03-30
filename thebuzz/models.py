import ast

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
import uuid
import json

#---------------------------------------------------------------------------------------------

class Friend(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    displayName = models.CharField(max_length=200,blank=True)
    host = models.URLField()
    url = models.URLField()
    def __str__(self):
        return self.displayName

# PROFILE AND USER STUFF
@python_2_unicode_compatible
class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    displayName = models.CharField(max_length=200,blank=False,null=False)
    github = models.CharField(max_length=200,blank=True,default='')
    firstName = models.CharField(max_length=200,blank=True,default='')
    lastName = models.CharField(max_length=200,blank=True,default='')
    email = models.CharField(max_length=400,blank=True,default='')
    bio = models.CharField(max_length=2000,blank=True,default='')

    host = models.URLField()
    url = models.URLField()

    following = models.ManyToManyField(Friend, symmetrical = False, blank=True, related_name='who_im_following')

    followers = models.ManyToManyField(Friend, symmetrical = False, blank=True, related_name='my_followers')

    # people who i am following and are following me
    friends = models.ManyToManyField(Friend, blank=True, related_name='my_friends')

    #the following lines onward are from here:
    #https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

    def follow(self, user_to_follow):
        if user_to_follow in self.followers.all():
            self.friend(user_to_follow)
        else:
            self.following.add(user_to_follow)
        self.save()

    def get_all_following(self):
        return self.following.all()

    # add someone is following me
    def add_user_following_me(self, user_whos_following):

        if user_whos_following in self.following.all():
            self.friend(user_whos_following)
        else:
            self.followers.add(user_whos_following)
        self.save()

    def friend(self, user_to_befriend):
        self.friends.add(user_to_befriend)
        self.followers.remove(user_to_befriend)
        self.following.remove(user_to_befriend)
        self.save()

    def get_all_friends(self):
        return self.friends.all()

    # delete friend from friends list and from following list (they can still be following me)
    def unfriend(self, friend):
        self.friends.remove(friend)
        self.following.remove(friend)

    # get those that are only following me
    def get_all_followers(self):
        pending = self.followers.all()
        # exclude the people we are already friends with
        #pending = pending.exclude(pk__in=self.friends.all())
        return pending


#these two functions act as signals so a profile is created/updated and saved when a new user is created/updated.
@receiver(post_save,sender=User)
def create_user_profile(sender,instance, created, **kwargs):
    if created:
        # Based on  Southpaw Hare & Carl Meyer
        # http://stackoverflow.com/a/1454986
        # Todo: Does not work
        host = Site.objects.get_current().domain
        id = uuid.uuid4()
        url = host + 'author/' + str(id)
        Profile.objects.create(user=instance, id=id, host=host, url=url, displayName=instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender,instance, **kwargs):
    instance.profile.save()


#END PROFILE AND USER STUFF
#-----------------------------------------------------

#POSTS AND COMMENTS

#taking influence from http://pythoncentral.io/writing-models-for-your-first-python-django-application/
@python_2_unicode_compatible
class Post(models.Model):
	#OVERRIDDING the primary key id that django implements
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length = 100, default='No Title')
    source = models.CharField(max_length = 2000)
    origin = models.CharField(max_length = 2000)
    description = models.CharField(max_length =100)

    content = models.TextField(max_length =2000)
    contentType_choice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base65'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )
    contentType = models.CharField(max_length=2000, default='text/plain', choices=contentType_choice)

	#content types can be:
	#text/markdown -> included markdown in their post
	#text/plain    -> plain ol' post. No images or nothing. Default value for now
	#application/base64 -> dunno yet, just an image?
	#image/png;base64 ->an embedded png. It's two posts if a post includes an image

    #image/jpeg;base64 ->embedded jpeg. Same as above I assume

    image = models.ImageField(null=True, blank=True)

    published = models.DateTimeField(auto_now=True)
    categories = models.CharField(max_length =100)

    visibility_choice = (
        ('PUBLIC', 'PUBLIC'),
        ('FOAF', 'FOAF'),
        ('FRIENDS', 'FRIENDS'),
        ('PRIVATE', 'PRIVATE'),
        ('SERVERONLY', 'SERVERONLY'),
    )
    visibility = models.CharField(default ="PUBLIC", max_length=20, choices=visibility_choice)

    visibleTo = models.CharField(max_length = 500)
    unlisted = models.BooleanField(default=False)

    associated_author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def setVisibleTo(self, x): #writes over it for now
	    self.visibleTo = json.dumps(x)

    def getVisibleTo(self):
	    return json.loads(self.visibleTo)

    def __str__(self):  # __unicode__ for Python 2
        return self.title


class Img(models.Model):
	associated_post = models.ForeignKey(Post, on_delete=models.CASCADE)
	myImg = models.ImageField() #upload_to='images'



class CommentAuthor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    host = models.URLField()
    displayName = models.CharField(max_length=200, blank=True)
    github = models.CharField(max_length=200, blank=True)
    def __str__(self):
        return self.displayName

class Comment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    associated_post= models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(CommentAuthor, on_delete=models.CASCADE)
    comment =  models.TextField(max_length =2000)

    contentType_choice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base65'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )
    contentType = models.CharField(max_length=2000, default='text/plain', choices=contentType_choice)

    date_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content + '    ----' + self.author.displayName


# ------------------- END POST AND COMMENTS -----------------------

# ----------------------- Node Site User -------------------------

class Site_API_User(models.Model):
    id = models.AutoField(primary_key=True)
    api_site = models.CharField(max_length = 2000, blank=True)
    username = models.CharField(max_length = 150)
    password = models.CharField(max_length = 72)

    def __str__(self):
        return str(self.api_site)


# ----------------------- End Node Site User -------------------------
