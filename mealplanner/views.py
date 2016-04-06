from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

from mealplanner.models import Recipe
from mealplanner.forms import recipe_name_form_factory

def index(request):
    recipe_list = Recipe.objects.all()
    template = loader.get_template('mealplanner/index.html')
    context = {
        'recipe_list': recipe_list,
    }
    return HttpResponse(template.render(context, request))

def recipeEditor(request):
    recipe_list = Recipe.objects.all()
    template = loader.get_template('mealplanner/recipeEditor.html')
    context = {
        'recipe_list': recipe_list,
    }
    return HttpResponse(template.render(context, request))

def viewRecipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    template = loader.get_template('mealplanner/viewRecipe.html')
    context = {
        'recipe': recipe,
    }
    
    return HttpResponse(template.render(context, request))

def editRecipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    formClass = recipe_name_form_factory(initName=recipe.name,initServings=recipe.servings,initInstructions=recipe.instructions)
    form = formClass()
    context = {
        'recipe': recipe,
        'form': form
    }
    return render(request, 'mealplanner/editRecipe.html', context)

def saveRecipe(request, recipe_id):
    # if this is a POST request we need to process the form data
    recipe = Recipe.objects.get(id=recipe_id)
    error =''
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formClass = recipe_name_form_factory()
        form = formClass(request.POST)
        
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            saveRecipeFromForm(request, form, recipe)
        else:
            error = 'Invalid form. Your changes to recipe "' + recipe.name + '" were not saved.'
            #error = 'Invalid form.'
        
    context = {
        'recipe': recipe,
        'error': error
    }
    return render(request, 'mealplanner/viewRecipe.html', context)



def saveRecipeFromForm(request,form, recipe):
    recipe.name =  form.cleaned_data['name']
    recipe.servings = form.cleaned_data['servings']
    recipe.instructions = form.cleaned_data['instructions']
    recipe.save()
    
    