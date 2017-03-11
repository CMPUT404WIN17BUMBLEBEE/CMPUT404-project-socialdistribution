from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime, uuid

import uuid

#---------------------------------------------------------------------------------------------
# PROFILE AND USER STUFF
@python_2_unicode_compatible
class Profile(models.Model):
    displayName = models.CharField(max_length=200,blank=True)
    github = models.CharField(max_length=200,blank=True)
    firstName = models.CharField(max_length=200,blank=True)
    lastName = models.CharField(max_length=200,blank=True)
    email = models.CharField(max_length=400,blank=True)
    bio = models.CharField(max_length=2000,blank=True)
    #TODO: put friends list and posts in here

#the following lines onward are from here:
#https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

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
	contentType = models.CharField(max_length = 2000, default='text/plain')   
	published = models.DateTimeField('DateTime created') 
	categories = []
	# visibility ["PUBLIC","FOAF","FRIENDS","PRIVATE","SERVERONLY"]
	visibility = models.CharField(default ="PUBLIC", max_length=20)  
	visibileTo = []
	unlisted = False
        #idk, added default so it would stop complaining
        associated_author = models.ForeignKey(User, default="")


class Comment(models.Model):

    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    associated_post= models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now=True)

# ------------------- END POST AND COMMENTS -----------------------
