from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import uuid

class Profile(models.Model):
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    displayName = models.CharField(max_length=200)
    githubUsername = models.CharField(max_length=200)
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    email = models.CharField(max_length=400)
    bio = models.CharField(max_length=2000)
