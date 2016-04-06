from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    
    # Recipe editor
    url(r'recipe/editor', views.recipeEditor, name='recipeEditor'),
    url(r'recipe/view/(?P<recipe_id>[0-9]+)/$', views.viewRecipe, name='viewRecipe'),
    url(r'recipe/edit/(?P<recipe_id>[0-9]+)/$', views.editRecipe, name='editRecipe'),
    url(r'recipe/save/(?P<recipe_id>[0-9]+)/$', views.saveRecipe, name='saveRecipe'),
    
    # Calendar
    url(r'^$', views.currentMonth, name="currentMonth"),
    url(r"^(\d+)/(\d+)/(prev|next)$", views.newMonth, name="newMonth"),
    url(r"^(\d+)/(\d+)/$", views.month, name="month"),
    url(r"^(\d+)/(\d+)/(\d+)/(\d+)/$", views.detailDay, name="detailDay"),
    
    # Login
    #url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'mealplanner/login.html'}),
    #url(r'^logout/$', 'django.contrib.auth.views.logout',{'next_page': '/'}),
    
    url(r'^login/$', login, {'template_name': 'mealplanner/login.html'}),
    url(r'^logout/$', logout,{'next_page': '/'}),
    
    url(r'^postLogin/', views.postLogin, name="postLogin"),
    url(r'^saveSettings', views.saveSettings, name="saveSettings"),
    url(r'^updateSettings/$', views.updateSettings, name="updateSettings"),
]