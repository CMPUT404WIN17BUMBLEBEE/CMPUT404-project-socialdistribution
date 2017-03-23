# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import thebuzz.models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('content', models.TextField(max_length=2000)),
                ('contentType', models.CharField(default=b'text/plain', max_length=2000, choices=[(b'text/markdown', b'text/markdown'), (b'text/plain', b'text/plain'), (b'application/base64', b'application/base65'), (b'image/png;base64', b'image/png;base64'), (b'image/jpeg;base64', b'image/jpeg;base64')])),
                ('date_created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Img',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('myImg', models.ImageField(upload_to=b'')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True)),
                ('title', models.CharField(default=b'No Title', max_length=100)),
                ('source', models.CharField(max_length=2000)),
                ('origin', models.CharField(max_length=2000)),
                ('description', models.CharField(max_length=100)),
                ('content', models.TextField(max_length=2000)),
                ('contentType', models.CharField(default=b'text/plain', max_length=2000, choices=[(b'text/markdown', b'text/markdown'), (b'text/plain', b'text/plain'), (b'application/base64', b'application/base65'), (b'image/png;base64', b'image/png;base64'), (b'image/jpeg;base64', b'image/jpeg;base64')])),
                ('image', models.ImageField(null=True, upload_to=b'', blank=True)),
                ('published', models.DateTimeField(auto_now=True)),
                ('categories', thebuzz.models.ListField(blank=True)),
                ('visibility', models.CharField(default=b'PUBLIC', max_length=20, choices=[(b'PUBLIC', b'PUBLIC'), (b'FOAF', b'FOAF'), (b'FRIENDS', b'FRIENDS'), (b'PRIVATE', b'PRIVATE'), (b'SERVERONLY', b'SERVERONLY')])),
                ('visibleTo', thebuzz.models.ListField(blank=True)),
                ('unlisted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('displayName', models.CharField(max_length=200, blank=True)),
                ('github', models.CharField(max_length=200, blank=True)),
                ('firstName', models.CharField(max_length=200, blank=True)),
                ('lastName', models.CharField(max_length=200, blank=True)),
                ('email', models.CharField(max_length=400, blank=True)),
                ('bio', models.CharField(max_length=2000, blank=True)),
                ('host', models.URLField()),
                ('url', models.URLField()),
                ('followers', models.ManyToManyField(related_name='my_followers', to='thebuzz.Profile', blank=True)),
                ('following', models.ManyToManyField(related_name='who_im_following', to='thebuzz.Profile', blank=True)),
                ('friends', models.ManyToManyField(related_name='friends_rel_+', to='thebuzz.Profile', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='associated_author',
            field=models.ForeignKey(to='thebuzz.Profile'),
        ),
        migrations.AddField(
            model_name='img',
            name='associated_post',
            field=models.ForeignKey(to='thebuzz.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='associated_post',
            field=models.ForeignKey(related_name='comments', to='thebuzz.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(to='thebuzz.Profile'),
        ),
    ]
