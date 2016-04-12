from django.contrib import admin

# Register your models here.

from .models import Recipe, RecipeIngredient, Ingredient, Meal, UserSettings, Aisle, DayIngredient

admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(Ingredient)
admin.site.register(Meal)
admin.site.register(UserSettings)
admin.site.register(Aisle)
admin.site.register(DayIngredient)
