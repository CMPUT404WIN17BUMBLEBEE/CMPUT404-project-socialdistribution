# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('thebuzz', '0002_auto_20170305_2121'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comment',
            new_name='content',
        ),
        migrations.AlterField(
            model_name='comment',
            name='date_created',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.CharField(max_length=2000, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='displayName',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.CharField(max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='firstName',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='githubUsername',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='lastName',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
