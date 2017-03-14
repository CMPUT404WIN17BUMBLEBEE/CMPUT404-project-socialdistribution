import ast

from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

import uuid


# From jathanism http://stackoverflow.com/a/7394475
class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


@python_2_unicode_compatible
class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.URLField()
    url = models.URLField()

    displayName = models.CharField(max_length=200, blank=True)
    github = models.URLField(blank=True)
    firstName = models.CharField(max_length=200, blank=True)
    lastName = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=400, blank=True)
    bio = models.CharField(max_length=2000, blank=True)

    friends = models.ManyToManyField('self', blank=True)
    followers = models.ManyToManyField('self', blank=True)
    following = models.ManyToManyField('self', blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.username


# these two functions act as signals so a profile is created/updated and saved when a new user is created/updated.
@receiver(post_save, sender=User)
def create_user_author(sender, instance, created, **kwargs):
    if created:
        # Based on  Southpaw Hare & Carl Meyer
        # http://stackoverflow.com/a/1454986
        # Todo: Does not work
        host = Site.objects.get_current().domain
        id = uuid.uuid4()
        url = host + '/author/' + str(id)
        Author.objects.create(user=instance, id=id, host=host, url=url, displayName=instance.username)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.author.save()


@python_2_unicode_compatible
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=100, default='Title')
    source = models.URLField(max_length=2000, blank=True)
    origin = models.URLField(max_length=2000, blank=True)
    description = models.CharField(max_length=100, blank=True)

    content = models.TextField(max_length=2000)
    contentType_choice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base65'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )
    contentType = models.CharField(max_length=2000, default='text/plain', choices=contentType_choice)

    published = models.DateTimeField(default=timezone.now)
    categories = ListField(blank=True)

    visibility_choice = (
        ('PUBLIC', 'PUBLIC'),
        ('FOAF', 'FOAF'),
        ('FRIENDS', 'FRIENDS'),
        ('PRIVATE', 'PRIVATE'),
        ('SERVERONLY', 'SERVERONLY'),
    )
    visibility = models.CharField(default="PUBLIC", max_length=20, choices=visibility_choice)
    visibileTo = ListField(blank=True)
    unlisted = models.BooleanField(default=False)  # image is true

    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):  # __unicode__ for Python 2
        return self.title


@python_2_unicode_compatible
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment = models.CharField(max_length=2000)
    contentType_choice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base65'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )
    contentType = models.CharField(max_length=2000, default='text/plain', choices=contentType_choice)
    published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.comment + '    ----' + self.author.displayName


