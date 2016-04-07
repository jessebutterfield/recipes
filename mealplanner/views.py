from django.template import loader, RequestContext
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from datetime import datetime,date,timedelta

from mealplanner.models import Recipe, RecipeIngredient, Meal, Author
from mealplanner.forms import recipe_name_form_factory, info_form_factory, signup_form

import calendar

@login_required
def index(request):
    recipe_list = Recipe.objects.all()
    template = loader.get_template('mealplanner/index.html')
    context = {
        'recipe_list': recipe_list,
    }
    return HttpResponse(template.render(context, request))

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

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# RECIPE EDITOR    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------

@login_required
def recipeEditor(request):
    recipe_list = Recipe.objects.filter(author = request.user)
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
    # if this is a POST request we need to process the form data
    duplicate = ('saveasnew' in request.POST)

    if duplicate:
        recipe = Recipe()
    else:
        recipe = Recipe.objects.get(id=recipe_id)
        if(recipe.author != request.user):
            return HttpResponse("Don't try and hack other peoples recipes")
        
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
        ingredient = RecipeIngredient()
        ingredient.recipe = recipe
        ingredient.name = request.POST['ingredient_name-' + str(i)]
        ingredient.quantity = float(request.POST['ingredient_quantity-' + str(i)])
        ingredient.unit = request.POST['ingredient_unit-' + str(i)]
        ingredient.save()
    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# CALENDAR    
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
mnames = "January February March April May June July August September October November December"
mnames = mnames.split()

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
    firstDay = request.user.author.firstDayOfWeek;
    print(firstDay)
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
    print(list(cal.iterweekdays()))
    week_days = [wd[x] for x in cal.iterweekdays()]
    context = {
        'user': request.user,
        'year': year, 
        'month': month, 
        'month_days': lst, 
        'mname': mnames[month-1],
        'week_days': week_days
    }
    return render_to_response("mealplanner/index.html", context )
    
def detailDay(request, year, month, day, commentId = False):
    print("TODO!")
    
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
            ua,created = Author.objects.get_or_create(user=user)
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
    return render_to_response('mealplanner/userSettings.html', {'form':form},context_instance=RequestContext(request))

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
        author,_ = Author.objects.get_or_create(user=user)
        author.defaultServings = defaultServings
        author.firstDayOfWeek = form.cleaned_data['firstDayOfWeek']
        author.save()
        
        return HttpResponseRedirect(reverse('currentMonth'))
    else:
        return updateSettings(request, form)
    


