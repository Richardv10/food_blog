
# Imports (copied from recipe/views.py for convenience)
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import requests 
from recipe.models import Recipe, UserRecipe, RecipeComment
from blog.models import CreatedRecipe

# Create your views here.

@login_required
def create_recipe(request):
    """View to create a new recipe by the user."""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        servings = request.POST.get('servings')
        ready_in_minutes = request.POST.get('ready_in_minutes')
        featured_image = request.FILES.get('featured_image')
        
        # Create and save the new recipe
        new_recipe = CreatedRecipe.objects.create(
            creator=request.user,  # Fixed: was 'user', should be 'creator'
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            servings=int(servings) if servings else None,
            ready_in_minutes=int(ready_in_minutes) if ready_in_minutes else None,
            featured_image=featured_image
        )
        messages.success(request, 'Your recipe has been created successfully!')
        return redirect('my_recipes')  # Redirect to the unified my_recipes page

    return render(request, 'create_recipe.html')  # Fixed template path


@login_required 
def created_recipe_detail(request, recipe_id):
    """View to display a single created recipe"""
    try:
        recipe = CreatedRecipe.objects.get(id=recipe_id, creator=request.user)
        return render(request, 'created_recipe_detail.html', {'recipe': recipe})
    except CreatedRecipe.DoesNotExist:
        messages.error(request, 'Recipe not found.')
        return redirect('my_recipes')


@login_required
def edit_created_recipe(request, recipe_id):
    """View to edit a created recipe"""
    try:
        recipe = CreatedRecipe.objects.get(id=recipe_id, creator=request.user)
    except CreatedRecipe.DoesNotExist:
        messages.error(request, 'Recipe not found.')
        return redirect('my_recipes')
    
    if request.method == 'POST':
        recipe.title = request.POST.get('title')
        recipe.description = request.POST.get('description')
        recipe.ingredients = request.POST.get('ingredients')
        recipe.instructions = request.POST.get('instructions')
        recipe.servings = int(request.POST.get('servings')) if request.POST.get('servings') else None
        recipe.ready_in_minutes = int(request.POST.get('ready_in_minutes')) if request.POST.get('ready_in_minutes') else None
        
        # Handle image upload
        if request.FILES.get('featured_image'):
            recipe.featured_image = request.FILES.get('featured_image')
            
        recipe.save()
        messages.success(request, 'Your recipe has been updated successfully!')
        return redirect('created_recipe_detail', recipe_id=recipe.id)
    
    return render(request, 'edit_created_recipe.html', {'recipe': recipe})


@login_required
def delete_created_recipe(request, recipe_id):
    """View to delete a created recipe"""
    try:
        recipe = CreatedRecipe.objects.get(id=recipe_id, creator=request.user)
        recipe.delete()
        messages.success(request, 'Recipe deleted successfully!')
    except CreatedRecipe.DoesNotExist:
        messages.error(request, 'Recipe not found.')
    
    return redirect('my_recipes')