from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_recipe, name='create_recipe'),
    path('recipe/<int:recipe_id>/', views.created_recipe_detail, name='created_recipe_detail'),
    path('recipe/<int:recipe_id>/public/', views.public_created_recipe_detail, name='public_created_recipe_detail'),
    path('recipe/<int:recipe_id>/edit/', views.edit_created_recipe, name='edit_created_recipe'),
    path('recipe/<int:recipe_id>/delete/', views.delete_created_recipe, name='delete_created_recipe'),
    path('recipe/<int:recipe_id>/share/', views.share_created_recipe, name='share_created_recipe'),
    path('recipe/<int:recipe_id>/unshare/', views.unshare_created_recipe, name='unshare_created_recipe'),
]