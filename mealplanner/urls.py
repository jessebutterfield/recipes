from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'recipe/(?P<recipe_id>[0-9]+)/$', views.recipeDetail, name='recipeDetail'),
]