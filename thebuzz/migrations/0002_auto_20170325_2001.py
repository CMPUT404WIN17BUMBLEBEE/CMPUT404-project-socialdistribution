# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('thebuzz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentAuthor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('url', models.URLField()),
                ('host', models.URLField()),
                ('displayName', models.CharField(max_length=200)),
                ('github', models.CharField(max_length=200, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Site_API_User',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('username', models.CharField(max_length=150)),
                ('password', models.CharField(max_length=72)),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(to='thebuzz.CommentAuthor'),
        ),
    ]
