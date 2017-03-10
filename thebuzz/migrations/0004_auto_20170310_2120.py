# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('thebuzz', '0003_auto_20170308_2154'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='githubUsername',
            new_name='github',
        ),
    ]
