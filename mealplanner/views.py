from django.http import HttpResponse
from django.template import loader

from mealplanner.models import Recipe


def index(request):
    recipe_list = Recipe.objects.all()
    template = loader.get_template('mealplanner/index.html')
    context = {
        'recipe_list': recipe_list,
    }
    return HttpResponse(template.render(context, request))

def recipeDetail(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    template = loader.get_template('mealplanner/recipe.html')
    context = {
        'recipe': recipe,
    }
    return HttpResponse(template.render(context, request))
    

