from django.template import loader
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from datetime import datetime,date,timedelta

from mealplanner.models import Recipe, Meal
from mealplanner.forms import recipe_name_form_factory

import calendar

def index(request):
    recipe_list = Recipe.objects.all()
    template = loader.get_template('mealplanner/index.html')
    context = {
        'recipe_list': recipe_list,
    }
    return HttpResponse(template.render(context, request))

# ----------------------------------------------------------------------------------------------------------------
# RECIPE EDITOR    
# ----------------------------------------------------------------------------------------------------------------

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

def editCurrentRecipe(request, recipe_id):
    return editRecipe(request, recipe_id, False)

def duplicateRecipe(request, recipe_id):
    return editRecipe(request, recipe_id, True)

def editRecipe(request, recipe_id, duplicate):
    recipe = Recipe.objects.get(id=recipe_id)
    recipeName = recipe.name
    if duplicate:
        recipeName = "COPY " + recipeName
    formClass = recipe_name_form_factory(initName=recipeName,initServings=recipe.servings,initInstructions=recipe.instructions)
    form = formClass()
    context = {
        'recipe': recipe,
        'form': form,
        'duplicate': duplicate
    }
    return render(request, 'mealplanner/editRecipe.html', context)

def saveCurrentRecipe(request, recipe_id):
    return saveRecipe(request, recipe_id, False)
    
def saveAsNewRecipe(request, recipe_id):
    return saveRecipe(request, recipe_id, True)

def saveRecipe(request, recipe_id, duplicate):
    # if this is a POST request we need to process the form data
    originalRecipe = Recipe.objects.get(id=recipe_id)
    if duplicate:
        newRecipe = Recipe()
    else:
        newRecipe = originalRecipe
        
    error =''
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formClass = recipe_name_form_factory()
        form = formClass(request.POST)
        
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            saveRecipeFromForm(request, form, originalRecipe, newRecipe)
        else:
            error = 'Invalid form. Your changes to recipe "' + newRecipe.name + '" were not saved.'
        
    context = {
        'recipe': newRecipe,
        'error': error
    }
    return render(request, 'mealplanner/viewRecipe.html', context)

def saveRecipeFromForm(request,form, originalRecipe, newRecipe):
    newRecipe.name =  form.cleaned_data['name']
    # TODO: change that to currently logged-in user!
    newRecipe.author = User.objects.all()[0]
    newRecipe.servings = form.cleaned_data['servings']
    newRecipe.instructions = form.cleaned_data['instructions']
    newRecipe.save()
    
    if (newRecipe.id != originalRecipe.id):
        for recipeingredient in originalRecipe.recipeingredient_set.all():
            # duplicate ingredients
            newRecipeIng = recipeingredient.duplicate()
            newRecipeIng.recipe = newRecipe
            newRecipeIng.save()
    
# ----------------------------------------------------------------------------------------------------------------
# CALENDAR    
# ----------------------------------------------------------------------------------------------------------------
mnames = "January February March April May June July August September October November December"
mnames = mnames.split()

def newMonth(request, year, month, change):
    year, month = int(year), int(month)
    if change in ("next", "prev"):
        d, mdelta = date(year, month, 15), timedelta(days=31)
        if change == "next":   
            d += mdelta
        elif change == "prev": 
            d -= mdelta
        year, month = d.timetuple()[0:2]
    return HttpResponseRedirect(reverse('month', args=(year,month)))

def currentMonth(request):
    year, month = date.today().timetuple()[0:2]
    return HttpResponseRedirect(reverse('month', args=(year,month)))
    
def month(request, year, month):
    """Listing of days in `month`."""
    year, month = int(year), int(month)


    # init variables
    cal = calendar.Calendar()
    cal.setfirstweekday(6)
    month_days = cal.itermonthdays(year, month)
    lst = [[]]
    week = 0

    # make month lists containing list of days for each week
    # each day tuple will contain list of entries and 'current' indicator
    today = datetime.now()
    for day in month_days:
        entries = current = False   # are there entries for this day; current day?
        meals = []
        if day:
            #TODO: fix this to a get and a try 
            n = date(year,month,day)
            entries = Meal.objects.filter(date=n)
            if(entries):
                for u in entries.all():
                    meals.append("(" + str(u.servings) + ") " + u.recipe.name)
            if(today.year == year and today.month == month and today.day == day):
                current = True

        lst[week].append((day, current, meals))
        if len(lst[week]) == 7:
            lst.append([])
            week += 1

    return render_to_response("mealplanner/index.html", dict(year=year, month=month, month_days=lst, mname=mnames[month-1]))
    
def detailDay(request, year, month, day, commentId = False):
    print("TODO!")