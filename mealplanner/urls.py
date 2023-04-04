from django.urls import re_path

from . import views, user_info_views, calendar_views

urlpatterns = [
    #re_path(r'^$', views.index, name='index'),

    # Recipe editor
    re_path(r'recipe/editor/(?P<user_id>[0-9]+)/', views.recipeEditor, name='recipeEditor'),
    re_path(r'recipe/editor/$', views.myRecipeEditor, name='myRecipeEditor'),
    re_path(r'recipe/browser/$', views.recipeBrowser, name='recipeBrowser'),
    re_path(r'recipe/view/(?P<recipe_id>[0-9]+)/$', views.viewRecipe, name='viewRecipe'),
    re_path(r'recipe/edit/(?P<recipe_id>[0-9]+)/$', views.editRecipe, name='editRecipe'),
    re_path(r'recipe/new', views.editRecipe, name='newRecipe'),
    re_path(r'recipe/save/None/$', views.saveRecipe, name='saveRecipe'),
    re_path(r'recipe/save/(?P<recipe_id>[0-9]+)/$', views.saveRecipe, name='saveRecipe'),
    re_path(r'recipe/delete/(?P<recipe_id>[0-9]+)/$', views.deleteRecipe, name='deleteRecipe'),
    re_path(r'aisle/browser/$', views.aisleBrowser, name='aisleBrowser'),
    re_path(r'ingredient/move/$', views.ingredientMove, name='ingredientMove'),
    re_path(r'aisle/move/$', views.aisleMove, name='aisleMove'),
    re_path(r'aisle/rename/$', views.aisleRename, name='aisleRename'),
    re_path(r'aisle/delete/$', views.aisleDelete, name='aisleDelete'),

    # Calendar
    re_path(r'^$', calendar_views.currentMonth, name="currentMonth"),
    re_path(r"^(\d+)/(\d+)/(prev|next)$", calendar_views.newMonth, name="newMonth"),
    re_path(r"^(\d+)/(\d+)/$", calendar_views.month, name="month"),
    re_path(r"^(\d+)/(\d+)/(\d+)/$", calendar_views.detailDay, name="detailDay"),
    re_path(r"^save/(\d+)/(\d+)/(\d+)/$", calendar_views.saveDay, name="saveDay"),
    re_path(r'generateList', calendar_views.generateList, name='generateList'),
    re_path(r'date/addRecipe', calendar_views.addToDate, name='addToDate'),

    # User settings and login
    re_path(r'signup', user_info_views.signup, name='signup'),
    re_path(r'createAccount', user_info_views.createAccount, name='createAccount'),
    re_path(r'^postLogin/', user_info_views.postLogin, name="postLogin"),
    re_path(r'^saveSettings', user_info_views.saveSettings, name="saveSettings"),
    re_path(r'^updateSettings/$', user_info_views.updateSettings, name="updateSettings"),
]