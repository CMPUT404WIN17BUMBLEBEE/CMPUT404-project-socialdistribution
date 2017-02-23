from django.db import models

from django.utils.encoding import python_2_unicode_compatible
# Create your models here.

#taking influence from http://pythoncentral.io/writing-models-for-your-first-python-django-application/
#because I have no idea what im doing

class Post(models.Model):
	#assuming links would go in as text? may have to change later
	posted_text = models.CharField(max_length =2000) 
	date_created = models.DateTimeField('DateTime created')
	post_privacy = 1


class Comment(models.Model):
	associated_post= models.ForeignKey(Post)
	comment = models.TextField()
	date_created = models.DateTimeField('DateTime created')
