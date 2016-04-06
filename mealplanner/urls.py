from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    
    # Recipe editor
    url(r'recipe/editor', views.recipeEditor, name='recipeEditor'),
    url(r'recipe/view/(?P<recipe_id>[0-9]+)/$', views.viewRecipe, name='viewRecipe'),
    url(r'recipe/edit/(?P<recipe_id>[0-9]+)/$', views.editRecipe, name='editRecipe'),
    url(r'recipe/save/(?P<recipe_id>[0-9]+)/$', views.saveRecipe, name='saveRecipe'),
    
    # Calendar
    url(r'^$', views.currentMonth, name = "currentMonth"),
    url(r"^(\d+)/(\d+)/(prev|next)$", views.newMonth, name="newMonth"),
    url(r"^(\d+)/(\d+)/$", views.month, name="month"),
    url(r"^(\d+)/(\d+)/(\d+)/(\d+)/$", views.detailDay, name="detailDay"),
]