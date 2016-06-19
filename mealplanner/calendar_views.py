from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


from datetime import datetime,date,timedelta

from mealplanner.models import Recipe, Ingredient, Meal, UserSettings, Aisle, DayIngredient
from mealplanner.forms import generate_list_form_factory

import calendar
import collections


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



