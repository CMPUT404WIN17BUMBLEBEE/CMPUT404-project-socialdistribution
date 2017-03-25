# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('thebuzz', '0002_auto_20170325_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentauthor',
            name='displayName',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
