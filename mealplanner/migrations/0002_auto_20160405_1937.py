# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-05 19:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealplanner', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Ingredient',
            new_name='RecipeIngredient',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='instruction',
            new_name='instructions',
        ),
        migrations.RenameField(
            model_name='recipeingredient',
            old_name='units',
            new_name='unit',
        ),
    ]