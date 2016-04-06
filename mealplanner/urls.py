from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    
    # Recipe editor
    url(r'recipe/editor', views.recipeEditor, name='recipeEditor'),
    url(r'recipe/view/(?P<recipe_id>[0-9]+)/$', views.viewRecipe, name='viewRecipe'),
    url(r'recipe/editCurrent/(?P<recipe_id>[0-9]+)/$', views.editCurrentRecipe, name='editCurrentRecipe'),
    url(r'recipe/duplicate/(?P<recipe_id>[0-9]+)/$', views.duplicateRecipe, name='duplicateRecipe'),
    url(r'recipe/save/(?P<recipe_id>[0-9]+)/$', views.saveCurrentRecipe, name='saveCurrentRecipe'),
    url(r'recipe/saveasnew/(?P<recipe_id>[0-9]+)/$', views.saveAsNewRecipe, name='saveAsNewRecipe'),
    
    # Calendar
    url(r'^$', views.currentMonth, name = "currentMonth"),
    url(r"^(\d+)/(\d+)/(prev|next)$", views.newMonth, name="newMonth"),
    url(r"^(\d+)/(\d+)/$", views.month, name="month"),
    url(r"^(\d+)/(\d+)/(\d+)/(\d+)/$", views.detailDay, name="detailDay"),
]