from django.template import loader
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max, F

from datetime import datetime,date,timedelta

from mealplanner.models import Recipe, RecipeIngredient, Ingredient, Meal, UserSettings, Aisle, DayIngredient
from mealplanner.forms import recipe_name_form_factory, info_form_factory, signup_form, generate_list_form_factory

import calendar
import collections

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
    context = {
        'recipe': recipe,
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
        
    return HttpResponseRedirect(reverse('mealplanner.views.viewRecipe', args=(recipe.id,)))

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
    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# CALENDAR    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
mnames = "January February March April May June July August September October November December"
mnames = mnames.split()

@login_required
def generateList(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formClass = generate_list_form_factory()
        form = formClass(request.POST)
        
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            return generateListFromForm(request, form)
        else:
            return HttpResponse('Invalid form.')
        
    return HttpResponseRedirect(reverse('currentMonth'))

def generateListFromForm(request,form):
    start = form.cleaned_data['start_date']
    end = form.cleaned_data['end_date']
    
    # get all meals, build map from aisle to ingredient, to unit, to quantity...
    meals = Meal.objects.filter(user=request.user, date__range=[ start, end])
    sortedAisles = Aisle.objects.filter(user=request.user).order_by('order')

    # initialize map in specific order
    aisleToIngredientToUnitToQuantity = collections.OrderedDict()
    for aisle in sortedAisles:
        aisleToIngredientToUnitToQuantity[aisle.name] = {}

    # add ingredients from meals
    for meal in meals:
        for recipeingredient in meal.recipe.recipeingredient_set.all(): 
            # scale the ingredients of this recipe for this meal's servings
            if (not recipeingredient.ingredient.aisle):
                aisle = "Not categorized"
            else:
                aisle = recipeingredient.ingredient.aisle.name
            name,unit,quantity = recipeingredient.ingredient.name,recipeingredient.unit,recipeingredient.quantity
            scalar = meal.servings / meal.recipe.servings
            quantity = quantity * scalar

            if aisle not in aisleToIngredientToUnitToQuantity:
                aisleToIngredientToUnitToQuantity[aisle] = {}
            if name not in aisleToIngredientToUnitToQuantity[aisle]:
                aisleToIngredientToUnitToQuantity[aisle][name] = {}
                
            if unit not in aisleToIngredientToUnitToQuantity[aisle][name]:
                aisleToIngredientToUnitToQuantity[aisle][name][unit] = quantity
            else:
                aisleToIngredientToUnitToQuantity[aisle][name][unit] = aisleToIngredientToUnitToQuantity[aisle][name][unit] + quantity

    # add ingredients directly
    dayIngredients = DayIngredient.objects.filter(user=request.user, date__range=[ start, end])
    for dayIngredient in dayIngredients:
        if (not dayIngredient.ingredient.aisle):
            aisle = "Not categorized"
        else:
            aisle = dayIngredient.ingredient.aisle.name
        name,unit,quantity = dayIngredient.ingredient.name,dayIngredient.unit,dayIngredient.quantity

        if aisle not in aisleToIngredientToUnitToQuantity:
            aisleToIngredientToUnitToQuantity[aisle] = {}
        if name not in aisleToIngredientToUnitToQuantity[aisle]:
            aisleToIngredientToUnitToQuantity[aisle][name] = {}
            
        if unit not in aisleToIngredientToUnitToQuantity[aisle][name]:
            aisleToIngredientToUnitToQuantity[aisle][name][unit] = quantity
        else:
            aisleToIngredientToUnitToQuantity[aisle][name][unit] = aisleToIngredientToUnitToQuantity[aisle][name][unit] + quantity
    
    
    context = {
        'user': request.user,
        'startDate': start,
        'endDate': end,
        'aisleToIngredientToUnitToQuantity': aisleToIngredientToUnitToQuantity
    }
    return render(request, 'mealplanner/shoppingList.html', context)

@login_required
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

@login_required
def currentMonth(request):
    year, month = date.today().timetuple()[0:2]
    return HttpResponseRedirect(reverse('month', args=(year,month)))

@login_required    
def month(request, year, month):
    """Listing of days in `month`."""
    year, month = int(year), int(month)


    # init variables
    firstDay = request.user.usersettings.firstDayOfWeek;
    cal = calendar.Calendar(firstDay)
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
            entries = Meal.objects.filter(date=n, user=request.user)
            if(entries):
                for u in entries.all():
                    meals.append("(" + str(u.servings) + ") " + u.recipe.name)
            entries = DayIngredient.objects.filter(date=n, user=request.user)
            if(entries):
                ingredientDesc = ""
                for u in entries.all():
                    ingredientDesc += '{0:.2g}'.format(u.quantity) + " " + u.unit + " of " + u.ingredient.name + ", "
                meals.append(ingredientDesc[:len(ingredientDesc)-2])
            if(today.year == year and today.month == month and today.day == day):
                current = True

        lst[week].append((day, current, meals))
        if len(lst[week]) == 7:
            lst.append([])
            week += 1
    wd = calendar.weekheader(3).split()
    week_days = [wd[x] for x in cal.iterweekdays()]
    context = {
        'user': request.user,
        'year': year, 
        'month': month, 
        'month_days': lst, 
        'mname': mnames[month-1],
        'week_days': week_days
    }
    return render(request, "mealplanner/index.html", context)
    
@login_required
def detailDay(request, year, month, day):
    year, month, day = int(year), int(month), int(day)
    editDay = date(year,month,day)
    
    meals = Meal.objects.filter(date=editDay, user=request.user)
    dayIngredients = DayIngredient.objects.filter(date=editDay, user=request.user)
    userSettings = UserSettings.objects.get(user=request.user)
    recipes = Recipe.objects.filter(author=request.user)
    context = {
        'user': request.user,
        'meals': meals,
        'dayIngredients': dayIngredients,
        'recipes': recipes,
        'editDay': editDay,
        'defaultServings': userSettings.defaultServings
    }
    return render(request, 'mealplanner/editDay.html', context)

@login_required
def saveDay(request, year, month, day):
    if request.method == 'POST':
        saveDayMeals(request, year, month, day)
        
    return HttpResponseRedirect(reverse('month', args=(year,month)))

def saveDayMeals(request, year, month, day):
    year, month, day = int(year), int(month), int(day)
    editDay = date(year,month,day)
    
    # save the meals
    num_meals = int(request.POST['num_meals'])
    mealsToSave = []
    for i in range(num_meals):
        # get the Recipe
        recipeName = request.POST['meal_recipe-' + str(i)]
        servings = int(request.POST['meal_servings-' + str(i)])
        recipes = Recipe.objects.filter(name=recipeName,author=request.user)
        if (not recipes):
            # TODO: this should be handled better, it shouldn't happen ever
            return HttpResponse('Could not find a recipe called "' + recipeName + '". Your changes were not saved.')
        if (len(recipes) > 1):
            # TODO: this should be handled better, it shouldn't happen ever
            return HttpResponse('Found more than one recipe called "' + recipeName + '". Your changes were not saved.')
        
        recipe = recipes[0]
        
        # get or update meal
        meal = Meal()
        meal.user = request.user
        meal.date = editDay
        meal.recipe = recipe
        meal.servings = servings
        mealsToSave.append(meal)
            
    # delete all current meals - we'll just resave everything
    # only save after all meals are correctly created 
    Meal.objects.filter(user=request.user, date=editDay).all().delete()       
    for meal in mealsToSave:
        meal.save()
        
    # save the day's ingredients
    num_ingredients = int(request.POST['num_ingredients'])
    dayIngredientsToSave = []
    for i in range(num_ingredients):
        name = request.POST['ingredient_name-' + str(i)]
        dayIngredient = DayIngredient()
        dayIngredient.user = request.user
        dayIngredient.date = editDay
        [ingredient,_] = Ingredient.objects.get_or_create(user=request.user,name=name)
        dayIngredient.ingredient = ingredient
        dayIngredient.quantity = float(request.POST['ingredient_quantity-' + str(i)])
        dayIngredient.unit = request.POST['ingredient_unit-' + str(i)]
        dayIngredientsToSave.append(dayIngredient)
        
    # delete all current day ingredients - we'll just resave everything
    DayIngredient.objects.filter(user=request.user, date=editDay).all().delete()       
    for dayIngredient in dayIngredientsToSave:
        dayIngredient.save()

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# USER    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
    
def postLogin(request):
    form = AuthenticationForm(request,data=request.POST)
    if(form.is_valid()):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        n = request.POST['next']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            userSettings,created = UserSettings.objects.get_or_create(user=user)
            if(created):
                return HttpResponseRedirect(reverse('updateInfo'))
            else:
                if(n):
                    return HttpResponseRedirect(n)
                else:
                    return HttpResponseRedirect(reverse('currentMonth'))
        HttpResponse("Form was valid")
    return HttpResponse("Form was invalid")

@login_required
def updateSettings(request, form = None):
    if(not form):
        formClass = info_form_factory(request.user)
        form = formClass()
    return render(request, 'mealplanner/userSettings.html', {'form':form})

@login_required
def saveSettings(request):
    user = request.user
    formClass = info_form_factory(user)
    form = formClass(request.POST)
    if(form.is_valid()):
        user.username = form.cleaned_data['username']
        p = form.cleaned_data['password']
        if(p):
            user.set_password(p)
        user.save()

        defaultServings = form.cleaned_data['defaultServings']
        userSettings,_ = UserSettings.objects.get_or_create(user=user)
        userSettings.defaultServings = defaultServings
        userSettings.firstDayOfWeek = form.cleaned_data['firstDayOfWeek']
        userSettings.save()
        
        return HttpResponseRedirect(reverse('currentMonth'))
    else:
        return updateSettings(request, form)

def signup(request):
    form = signup_form()
    template = loader.get_template('mealplanner/signup.html')
    context = {
        'form': form(),
    }
    return HttpResponse(template.render(context, request))

def createAccount(request):
    form = signup_form();
    form_data = form(request.POST);
    if form_data.is_valid():
        username = form_data.cleaned_data['username']
        email = form_data.cleaned_data['email']
        password = form_data.cleaned_data['password']
        user = User.objects.create_user(username, email, password)
        user.save()
        user = authenticate(username=username, password=password)
        login(request, user)
        return HttpResponseRedirect(reverse('mealplanner.views.updateSettings'))
    else:
        return HttpResponseRedirect(reverse('mealplanner.views.signup'))
    

