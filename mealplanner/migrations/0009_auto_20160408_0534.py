# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-08 05:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealplanner', '0008_auto_20160407_0111'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='author',
            new_name='user',
        ),
    ]
