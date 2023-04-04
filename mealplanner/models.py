from django.db import models
from django.contrib.auth.models import User

import calendar


# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    instructions = models.TextField()
    servings = models.IntegerField()

    def __str__(self):
        return str(self.name)

    def duplicate(self):
        newRecipe = Recipe()
        newRecipe.name = self.name
        newRecipe.author = self.author
        newRecipe.servings = self.servings
        newRecipe.instructions = self.instructions

        for recipeingredient in self.recipeingredient_set.all():
            newRecipeIng = recipeingredient.duplicate()
            newRecipeIng.recipe = newRecipe

        return newRecipe


class Aisle(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    order = models.IntegerField()

    def __str__(self):
        return str(self.name)


class Ingredient(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    aisle = models.ForeignKey(Aisle, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, null=True, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return str(self.ingredient.name) + "-" + str(self.recipe.name)

    def duplicate(self):
        newRecipeIng = RecipeIngredient()
        newRecipeIng.ingredient = self.ingredient
        newRecipeIng.recipe = self.recipe
        newRecipeIng.quantity = self.quantity
        newRecipeIng.unit = self.unit
        return newRecipeIng


class DayIngredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return str(self.ingredient.name)


class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    servings = models.IntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return str(str(self.servings) + "-" + self.recipe.name + "-" + str(self.date))


day_dictionary = list(zip(range(0, 7), calendar.day_name))


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    defaultServings = models.IntegerField(null=True, default=4)
    firstDayOfWeek = models.IntegerField(choices=day_dictionary, default=6)

    def __str__(self):
        return str(self.user.username)
