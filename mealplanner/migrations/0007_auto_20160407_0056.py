# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-07 00:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mealplanner', '0006_auto_20160406_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='firstDayOfWeek',
            field=models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday')], default=6),
        ),
        migrations.AlterField(
            model_name='author',
            name='defaultServings',
            field=models.IntegerField(default=4, null=True),
        ),
    ]
