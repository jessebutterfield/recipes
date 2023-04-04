from django.template import loader
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max, F

from mealplanner.models import Recipe, RecipeIngredient, Ingredient, Aisle
from mealplanner.forms import recipe_name_form_factory


@login_required
def index(request):
    recipe_list = Recipe.objects.all()
    context = {
        'recipe_list': recipe_list,
    }
    return render(request, 'mealplanner/index.html', context)

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# RECIPE EDITOR
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------

@login_required
def myRecipeEditor(request):
    return recipeEditor(request, request.user.id)

def recipeEditor(request, user_id):
    author = User.objects.get(id=user_id)
    recipe_list = Recipe.objects.filter(author = author).order_by('name')
    template = loader.get_template('mealplanner/recipeEditor.html')
    context = {
        'author': author,
        'recipe_list': recipe_list,
    }
    return HttpResponse(template.render(context, request))

def recipeBrowser(request):
    author_list = User.objects.all()
    template = loader.get_template('mealplanner/recipeBrowser.html')
    context = {
        'author_list': author_list,
    }
    return HttpResponse(template.render(context, request))

def viewRecipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    template = loader.get_template('mealplanner/viewRecipe.html')
    if request.user.usersettings:
        first_day = request.user.usersettings.firstDayOfWeek + 1 % 7
    else:
        first_day = 0
    context = {
        'recipe': recipe,
        'first_day': first_day,
    }

    return HttpResponse(template.render(context, request))

@login_required
def editRecipe(request, recipe_id=None):
    if recipe_id:
        recipe = Recipe.objects.get(id=recipe_id)
        if (recipe.author != request.user):
            recipe.name = recipe.author.username + "'s " + recipe.name
    else:
        recipe = Recipe()
    formClass = recipe_name_form_factory(initName=recipe.name,initServings=recipe.servings,initInstructions=recipe.instructions)
    form = formClass()
    context = {
        'recipe': recipe,
        'form': form,
    }
    return render(request, 'mealplanner/editRecipe.html', context)

@login_required
def saveRecipe(request, recipe_id=None):
    # check whether this recipe needs to be saved with a new id (and author maybe)
    duplicate = ('saveasnew' in request.POST)

    if duplicate:
        recipe = Recipe()
    else:
        recipe = Recipe.objects.get(id=recipe_id)
        if(recipe.author != request.user):
            return HttpResponse("Don't try and hack other people's recipes")

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formClass = recipe_name_form_factory()
        form = formClass(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            saveRecipeFromForm(request, form, recipe)
        else:
            return HttpResponse('Invalid form. Your changes to recipe "' + recipe.name + '" were not saved.')

    return HttpResponseRedirect(reverse_lazy('mealplanner.views.viewRecipe', args=(recipe.id,)))

def saveRecipeFromForm(request,form, recipe):
    recipe.name =  form.cleaned_data['name']
    recipe.author = request.user
    recipe.servings = form.cleaned_data['servings']
    recipe.instructions = form.cleaned_data['instructions']
    num_ingredients = int(request.POST['num_ingredients'])

    ingredientsToSave = []
    for i in range(num_ingredients):
        recipe_ingredient = RecipeIngredient()
        name = request.POST['ingredient_name-' + str(i)]
        # get all inputs
        [ingredient,_] = Ingredient.objects.get_or_create(user=request.user,name=name)
        quantityStr = request.POST['ingredient_quantity-' + str(i)]
        unit = request.POST['ingredient_unit-' + str(i)]
        # validate before saving
        if isfloat(quantityStr) and ingredient:
            recipe_ingredient.quantity = float(quantityStr)
            recipe_ingredient.ingredient = ingredient
            recipe_ingredient.unit = unit
            ingredientsToSave.append(recipe_ingredient)
        else:
            print("Could not save invalid quantity-unit-ingredient " + quantityStr + "-" + unit + "-" + name)

    # only delete once you've built a list of valid ingredients to save
    recipe.save()
    recipe.recipeingredient_set.all().delete()
    for ingredientToSave in ingredientsToSave:
        ingredientToSave.recipe = recipe
        ingredientToSave.save()

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def deleteRecipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    if(recipe.author == request.user):
        recipe.delete()
    return HttpResponse()

@login_required
def aisleBrowser(request):
    aisle_list = Aisle.objects.filter(user = request.user).order_by('order')
    unassigned = Ingredient.objects.filter(user = request.user, aisle=None)
    template = loader.get_template('mealplanner/aisleBrowser.html')
    context = {
        'unassigned_set': unassigned,
        'aisle_list': aisle_list,
    }
    return HttpResponse(template.render(context, request))

@login_required
def aisleRename(request):
    old_name = request.POST['old_name']
    new_name = request.POST['new_name']
    if(old_name):
        aisle = Aisle.objects.get(name=old_name, user=request.user)
    else:
        aisle = Aisle(user=request.user)
        max_order = Aisle.objects.filter(user=request.user).aggregate(Max('order'))['order__max']
        if max_order is None:
            max_order = -1
        aisle.order = max_order + 1
    aisle.name = new_name
    aisle.save()

    return HttpResponse()

@login_required
def aisleMove(request):
    print(request.POST)
    aisle_name = request.POST['aisle_name']
    move_before = request.POST['move_before']
    if(aisle_name == move_before):
        return HttpResponse()
    aisle = Aisle.objects.get(name=aisle_name, user=request.user)
    if(move_before=='Unassigned'):
        b = Aisle.objects.filter(user=request.user).aggregate(Max('order'))['order__max'] + 1
    else:
        b = Aisle.objects.get(name=move_before, user=request.user).order
    if(aisle.order < b):
        Aisle.objects.filter(user=request.user, order__gt=aisle.order, order__lt=b).update(order=F('order') - 1)
        aisle.order = b - 1
    else:
        Aisle.objects.filter(user=request.user, order__gte=b, order__lt=aisle.order).update(order=F('order') + 1)
        aisle.order = b
    aisle.save()
    return HttpResponse()

@login_required
def aisleDelete(request):
    aisle_name = request.POST['aisle_name']
    aisle = Aisle.objects.get(name=aisle_name, user=request.user)
    Ingredient.objects.filter(aisle=aisle).update(aisle=None)
    aisle.delete()
    return HttpResponse()

@login_required
def ingredientMove(request):
    ingredient_id = request.POST['ingredient_id']
    ingredient = Ingredient.objects.get(id=ingredient_id)
    aisle_name = request.POST['aisle_name']
    if(aisle_name == "Unassigned"):
        aisle = None
    else:
        aisle = Aisle.objects.get(name=aisle_name, user=request.user)

    if(ingredient.user == request.user):
        ingredient.aisle = aisle
        ingredient.save()
    return HttpResponse()
