from django.template import loader
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from datetime import datetime,date,timedelta

from mealplanner.models import Recipe, RecipeIngredient, Ingredient, Meal, UserSettings
from mealplanner.forms import recipe_name_form_factory, info_form_factory, signup_form, generate_list_form_factory

import calendar

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
    print(user_id)
    recipe_list = Recipe.objects.filter(author = author)
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
    # TODO: change that to currently logged-in user!
    recipe.author = request.user
    recipe.servings = form.cleaned_data['servings']
    recipe.instructions = form.cleaned_data['instructions']
    num_ingredients = int(request.POST['num_ingredients'])
    recipe.recipeingredient_set.all().delete()
    recipe.save()
    for i in range(num_ingredients):
        recipe_ingredient = RecipeIngredient()
        recipe_ingredient.recipe = recipe
        name = request.POST['ingredient_name-' + str(i)]
        [ingredient,_] = Ingredient.objects.get_or_create(user=request.user,name=name)
        recipe_ingredient.ingredient = ingredient
        recipe_ingredient.quantity = float(request.POST['ingredient_quantity-' + str(i)])
        recipe_ingredient.unit = request.POST['ingredient_unit-' + str(i)]
        recipe_ingredient.save()
        
def deleteRecipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    if(recipe.author == request.user):
        recipe.delete()
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
            generateListFromForm(request, form)
        else:
            return HttpResponse('Invalid form.')
        
    return HttpResponseRedirect(reverse('currentMonth'))

def generateListFromForm(request,form):
    start = form.cleaned_data['start_date']
    end = form.cleaned_data['end_date']
    print("Generating a shopping list from " + str(start) + " to " + str(end))
    # TODO: make it go to a shopping list page

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
    userSettings = UserSettings.objects.get(user=request.user)
    recipes = Recipe.objects.filter(author=request.user)
    context = {
        'user': request.user,
        'meals': meals,
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
        print("----------> default servings: " + str(defaultServings))
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
    

