from django.template import loader
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from mealplanner.models import UserSettings
from mealplanner.forms import info_form_factory, signup_form

def postLogin(request):
    form = AuthenticationForm(request,data=request.POST)
    if(form.is_valid()):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        n = request.POST['next']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            _, created = UserSettings.objects.get_or_create(user=user)
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


