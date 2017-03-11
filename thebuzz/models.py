from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


import uuid

#---------------------------------------------------------------------------------------------
# PROFILE AND USER STUFF
@python_2_unicode_compatible
class Profile(models.Model):

    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    displayName = models.CharField(max_length=200,blank=True)
    githubUsername = models.CharField(max_length=200,blank=True)
    firstName = models.CharField(max_length=200,blank=True)
    lastName = models.CharField(max_length=200,blank=True)
    email = models.CharField(max_length=400,blank=True)
    bio = models.CharField(max_length=2000,blank=True)
    
    following = models.ManyToManyField('self', symmetrical = False, blank=True, related_name='who_im_following')

    friends = models.ManyToManyField('self', symmetrical = False, blank=True, related_name='friends')

    friend_requests = models.ManyToManyField('self', symmetrical = False, blank=True, related_name='friend_requests')

    #friends = models.ManyToManyField('self', through = 'Friends', through_fields=("sourceFriend","targetFriend"), symmetrical = False, blank = True)

#the following lines onward are from here:
#https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

    def follow(self, user_to_follow):
        self.following.add(user_to_follow)
        self.save()

    def friend(self, user_to_befriend):
        self.friends.add(user_to_befriend)
        self.save()

    def get_all_following(self):
        return self.following.all()

    def get_all_friends(self):
        return self.friends.all() 

    def get_all_friend_requests(self):
        return self.friend_requests.all()


class Friends(models.Model):
   sourceFriend = models.ForeignKey(Profile, related_name = 'source',default="")
   targetFriend = models.ForeignKey(Profile, related_name = 'target',default="")

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
    posted_text = models.CharField(max_length =2000)
    date_created = models.DateTimeField('DateTime created')
    post_privacy = 1


class Comment(models.Model):

    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    associated_post= models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now=True)

# ------------------- END POST AND COMMENTS -----------------------
