from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
import uuid
import json

#---------------------------------------------------------------------------------------------
# PROFILE AND USER STUFF
@python_2_unicode_compatible
class Profile(models.Model):

    #uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    displayName = models.CharField(max_length=200,blank=True)
    github = models.CharField(max_length=200,blank=True)
    firstName = models.CharField(max_length=200,blank=True)
    lastName = models.CharField(max_length=200,blank=True)
    email = models.CharField(max_length=400,blank=True)
    bio = models.CharField(max_length=2000,blank=True)
    
    following = models.ManyToManyField('self', symmetrical = False, blank=True, related_name='who_im_following')

    followers = models.ManyToManyField('self', symmetrical = False, blank=True, related_name='my_followers')

    # people who i am following and is following me
    friends = models.ManyToManyField('self', blank=True, related_name='my_friends')

    #friends = models.ManyToManyField('self', through = 'Friends', through_fields=("sourceFriend","targetFriend"), symmetrical = False, blank = True)

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
        self.save

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
        
#class Friends(models.Model):
#   sourceFriend = models.ForeignKey(Profile, related_name = 'source',default="")
#   targetFriend = models.ForeignKey(Profile, related_name = 'target',default="")

#these two functions act as signals so a profile is created/updated and saved when a new user is created/updated.
@receiver(post_save,sender=User)
def create_user_profile(sender,instance, created, **kwargs):
    if created:
         Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender,instance, **kwargs):
    instance.profile.save()


#END PROFILE AND USER STUFF
#-----------------------------------------------------

#POSTS AND COMMENTS

#taking influence from http://pythoncentral.io/writing-models-for-your-first-python-django-application/
#because I have no idea what im doing

class Post(models.Model):
	#assuming links would go in as text? may have to change later
    id = models.UUIDField(primary_key=True, default=uuid.uuid4) #OVERRIDDING the primary key id that django implements
    title = models.CharField(max_length = 100, default='No Title')
    source = models.CharField(max_length = 2000)
    origin = models.CharField(max_length = 2000)
    description = models.CharField(max_length =100)
    content = models.TextField(max_length =2000)
	#content types can be:
	#text/markdown -> included markdown in their post
	#text/plain    -> plain ol' post. No images or nothing. Default value for now
	#application/base64 -> dunno yet, just an image?
	#image/png;base64 ->an embedded png. It's two posts if a post includes an image
    #image/jpeg;base64 ->embedded jpeg. Same as above I assume
    image = models.ImageField(null=True, blank=True)
    contentType = models.CharField(max_length = 2000, default='text/plain')   
    published = models.DateTimeField(default=datetime.now)   #auto_now=True) 
    categories = []
    # visibility ["PUBLIC","FOAF","FRIENDS","PRIVATE","SERVERONLY"]
    visibility = models.CharField(default ="PUBLIC", max_length=20)
    visibleTo = models.CharField(max_length = 1000, blank=True) #need to CONVERT this into JSON. Functions below
    unlisted = False
    associated_author = models.ForeignKey(User, blank=True)

    def setVisibleTo(self, x): #writes over it for now
	    self.visibleTo = json.dumps(x)
	    print visibleTo

    def getVisibleTo(self):
	    return json.loads(self.visibleTo)


class Img(models.Model):
	associated_post = models.ForeignKey(Post, on_delete=models.CASCADE)
	myImg = models.ImageField() #upload_to='images'

class Comment(models.Model):

    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    associated_post= models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content =  models.TextField(max_length =2000)
    date_created = models.DateTimeField(auto_now=True)

# ------------------- END POST AND COMMENTS -----------------------
