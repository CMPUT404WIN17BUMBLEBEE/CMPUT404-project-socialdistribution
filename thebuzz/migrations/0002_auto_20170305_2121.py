# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('thebuzz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('date_created', models.DateTimeField(verbose_name=b'DateTime created')),
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
        migrations.AddField(
            model_name='comment',
            name='associated_post',
            field=models.ForeignKey(to='thebuzz.Post'),
        ),
    ]
