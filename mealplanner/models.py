from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(User)
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
    
class RecipeIngredient(models.Model):
    name = models.CharField(max_length=200)
    recipe = models.ForeignKey(Recipe)
    quantity = models.FloatField()    
    unit = models.CharField(max_length=50)
    
    def __str__(self):
        return str(self.name)
    
    def duplicate(self):
        newRecipeIng = RecipeIngredient()
        newRecipeIng.name = self.name
        newRecipeIng.recipe = self.recipe
        newRecipeIng.quantity = self.quantity
        newRecipeIng.unit = self.unit
        return newRecipeIng
    
class Meal(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    servings = models.IntegerField()
    recipe = models.ForeignKey(Recipe)
