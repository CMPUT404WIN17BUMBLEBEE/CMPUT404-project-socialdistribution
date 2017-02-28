from django.db import models
from django.contrib.auth.models import AbstractUser
#used this to help set up some customizations on the default user:
#https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractuser


class User(AbstractUser):

    following = models.ManyToManyField("self",related_name='follows',symmetrical=False) #unaccepted friend request from you



 
    #followers? #unaccepted friend request to you
    #friend? #in both following and followers

