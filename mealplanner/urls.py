from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    
    # Recipe editor
    url(r'recipe/editor/(?P<user_id>[0-9]+)/', views.recipeEditor, name='recipeEditor'),
    url(r'recipe/editor/$', views.myRecipeEditor, name='myRecipeEditor'),
    url(r'recipe/browser/$', views.recipeBrowser, name='recipeBrowser'),
    url(r'recipe/view/(?P<recipe_id>[0-9]+)/$', views.viewRecipe, name='viewRecipe'),
    url(r'recipe/edit/(?P<recipe_id>[0-9]+)/$', views.editRecipe, name='editRecipe'),
    url(r'recipe/new', views.editRecipe, name='newRecipe'),
    url(r'recipe/save/None/$', views.saveRecipe, name='saveRecipe'),
    url(r'recipe/save/(?P<recipe_id>[0-9]+)/$', views.saveRecipe, name='saveRecipe'),
    url(r'recipe/delete/(?P<recipe_id>[0-9]+)/$', views.deleteRecipe, name='deleteRecipe'),
    url(r'aisle/browser/$', views.aisleBrowser, name='aisleBrowser'),
    url(r'ingredient/move/$', views.ingredientMove, name='ingredientMove'),
    url(r'aisle/move/$', views.aisleMove, name='aisleMove'),
    url(r'aisle/rename/$', views.aisleRename, name='aisleRename'),
    url(r'aisle/delete/$', views.aisleDelete, name='aisleDelete'),

    # Calendar
    url(r'^$', views.currentMonth, name="currentMonth"),
    url(r"^(\d+)/(\d+)/(prev|next)$", views.newMonth, name="newMonth"),
    url(r"^(\d+)/(\d+)/$", views.month, name="month"),
    url(r"^(\d+)/(\d+)/(\d+)/$", views.detailDay, name="detailDay"),
    url(r"^save/(\d+)/(\d+)/(\d+)/$", views.saveDay, name="saveDay"),
    url(r'generateList', views.generateList, name='generateList'),
    
    # User settings and login
    url(r'signup', views.signup, name='signup'),
    url(r'createAccount', views.createAccount, name='createAccount'),
    url(r'^postLogin/', views.postLogin, name="postLogin"),
    url(r'^saveSettings', views.saveSettings, name="saveSettings"),
    url(r'^updateSettings/$', views.updateSettings, name="updateSettings"),
]