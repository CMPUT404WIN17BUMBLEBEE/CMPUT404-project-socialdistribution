# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import api.models
import django.utils.timezone
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('host', models.URLField()),
                ('url', models.URLField()),
                ('displayName', models.CharField(max_length=200, blank=True)),
                ('github', models.URLField(blank=True)),
                ('firstName', models.CharField(max_length=200, blank=True)),
                ('lastName', models.CharField(max_length=200, blank=True)),
                ('email', models.CharField(max_length=400, blank=True)),
                ('bio', models.CharField(max_length=2000, blank=True)),
                ('followers', models.ManyToManyField(related_name='followers_rel_+', to='api.Author', blank=True)),
                ('following', models.ManyToManyField(related_name='following_rel_+', to='api.Author', blank=True)),
                ('friends', models.ManyToManyField(related_name='friends_rel_+', to='api.Author', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('comment', models.CharField(max_length=2000)),
                ('contentType', models.CharField(default=b'text/plain', max_length=2000, choices=[(b'text/markdown', b'text/markdown'), (b'text/plain', b'text/plain'), (b'application/base64', b'application/base65'), (b'image/png;base64', b'image/png;base64'), (b'image/jpeg;base64', b'image/jpeg;base64')])),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(to='api.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('title', models.CharField(default=b'Title', max_length=100)),
                ('source', models.URLField(max_length=2000, blank=True)),
                ('origin', models.URLField(max_length=2000, blank=True)),
                ('description', models.CharField(max_length=100, blank=True)),
                ('content', models.TextField(max_length=2000)),
                ('contentType', models.CharField(default=b'text/plain', max_length=2000, choices=[(b'text/markdown', b'text/markdown'), (b'text/plain', b'text/plain'), (b'application/base64', b'application/base65'), (b'image/png;base64', b'image/png;base64'), (b'image/jpeg;base64', b'image/jpeg;base64')])),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('categories', api.models.ListField(blank=True)),
                ('visibility', models.CharField(default=b'PUBLIC', max_length=20, choices=[(b'PUBLIC', b'PUBLIC'), (b'FOAF', b'FOAF'), (b'FRIENDS', b'FRIENDS'), (b'PRIVATE', b'PRIVATE'), (b'SERVERONLY', b'SERVERONLY')])),
                ('visibileTo', api.models.ListField(blank=True)),
                ('unlisted', models.BooleanField(default=False)),
                ('author', models.ForeignKey(to='api.Author')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(related_name='comments', to='api.Post'),
        ),
    ]
