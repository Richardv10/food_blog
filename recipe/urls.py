from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_recipes, name='search_recipes'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('random/', views.random_recipe, name='random_recipe'),
    path('recipe/<int:recipe_id>/save/', views.save_recipe, name='save_recipe'),
    path('my-recipes/', views.my_recipes, name='my_recipes'),
]