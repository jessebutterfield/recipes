from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=200)
    instructions = models.TextField()
    servings = models.IntegerField()
    
    def __str__(self):
        return str(self.name)
    
class RecipeIngredient(models.Model):
    name = models.CharField(max_length=200)
    recipe = models.ForeignKey(Recipe)
    quantity = models.FloatField()    
    unit = models.CharField(max_length=50)
    
    def __str__(self):
        return str(self.name)
    
class Meal(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    servings = models.IntegerField()
    recipe = models.ForeignKey(Recipe)
