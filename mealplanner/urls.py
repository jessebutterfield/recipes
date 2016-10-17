from django.conf.urls import url

from . import views, user_info_views, calendar_views

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
    url(r'^$', calendar_views.currentMonth, name="currentMonth"),
    url(r"^(\d+)/(\d+)/(prev|next)$", calendar_views.newMonth, name="newMonth"),
    url(r"^(\d+)/(\d+)/$", calendar_views.month, name="month"),
    url(r"^(\d+)/(\d+)/(\d+)/$", calendar_views.detailDay, name="detailDay"),
    url(r"^save/(\d+)/(\d+)/(\d+)/$", calendar_views.saveDay, name="saveDay"),
    url(r'generateList', calendar_views.generateList, name='generateList'),
    url(r'date/addRecipe', calendar_views.addToDate, name='addToDate'),

    # User settings and login
    url(r'signup', user_info_views.signup, name='signup'),
    url(r'createAccount', user_info_views.createAccount, name='createAccount'),
    url(r'^postLogin/', user_info_views.postLogin, name="postLogin"),
    url(r'^saveSettings', user_info_views.saveSettings, name="saveSettings"),
    url(r'^updateSettings/$', user_info_views.updateSettings, name="updateSettings"),
]