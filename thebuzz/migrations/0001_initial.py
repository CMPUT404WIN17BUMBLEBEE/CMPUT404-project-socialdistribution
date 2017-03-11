# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('date_created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('posted_text', models.CharField(max_length=2000)),
                ('date_created', models.DateTimeField(verbose_name=b'DateTime created')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('displayName', models.CharField(max_length=200, blank=True)),
                ('githubUsername', models.CharField(max_length=200, blank=True)),
                ('firstName', models.CharField(max_length=200, blank=True)),
                ('lastName', models.CharField(max_length=200, blank=True)),
                ('email', models.CharField(max_length=400, blank=True)),
                ('bio', models.CharField(max_length=2000, blank=True)),
                ('friends', models.ManyToManyField(to='thebuzz.Profile', through='thebuzz.Friends', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='friends',
            name='sourceFriend',
            field=models.ForeignKey(related_name='source', default=b'', to='thebuzz.Profile'),
        ),
        migrations.AddField(
            model_name='friends',
            name='targetFriend',
            field=models.ForeignKey(related_name='target', default=b'', to='thebuzz.Profile'),
        ),
        migrations.AddField(
            model_name='comment',
            name='associated_post',
            field=models.ForeignKey(to='thebuzz.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(to='thebuzz.Profile'),
        ),
    ]
