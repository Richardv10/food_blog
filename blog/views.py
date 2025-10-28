
# Imports (copied from recipe/views.py for convenience)
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
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


def public_created_recipe_detail(request, recipe_id):
    """Public view to display a shared created recipe"""
    try:
        recipe = CreatedRecipe.objects.get(id=recipe_id, is_shared=True)
        return render(request, 'public_created_recipe_detail.html', {'recipe': recipe})
    except CreatedRecipe.DoesNotExist:
        messages.error(request, 'Recipe not found or not shared.')
        return redirect('home')


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


@login_required
def share_created_recipe(request, recipe_id):
    """Share a created recipe to the community feed"""
    try:
        recipe = CreatedRecipe.objects.get(id=recipe_id, creator=request.user)
    except CreatedRecipe.DoesNotExist:
        messages.error(request, 'Recipe not found.')
        return redirect('my_recipes')
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        # Create a Recipe object for this created recipe if it doesn't exist
        recipe_obj, created = Recipe.objects.get_or_create(
            recipe_id=f"created_{recipe.id}",  # Unique identifier for created recipes
            defaults={
                'title': recipe.title,
                'image_url': recipe.featured_image.url if recipe.featured_image else None,
                'summary': recipe.description or '',
                'instructions': recipe.instructions,
                'ingredients': [{'original': ingredient} for ingredient in recipe.get_ingredients_list()],
                'ready_in_minutes': recipe.ready_in_minutes,
                'servings': recipe.servings,
                'is_cached': True
            }
        )
        
        # Create or update UserRecipe for sharing
        user_recipe, user_recipe_created = UserRecipe.objects.get_or_create(
            user=request.user,
            recipe=recipe_obj,
            defaults={
                'is_shared': True,
                'message': message,
                'shared_at': timezone.now()
            }
        )
        
        # If it already exists but wasn't shared, update it
        if not user_recipe_created:
            user_recipe.is_shared = True
            user_recipe.message = message
            user_recipe.shared_at = timezone.now()
            user_recipe.save()
        
        # Update the original created recipe sharing status
        recipe.is_shared = True
        recipe.shared_message = message
        
        # Set shared_at timestamp if not already shared
        if not recipe.shared_at:
            recipe.shared_at = timezone.now()
            
        recipe.save()
        
        messages.success(request, f'"{recipe.title}" has been shared to the community feed!')
        
        return redirect('my_recipes')
    
    return redirect('my_recipes')


@login_required 
def unshare_created_recipe(request, recipe_id):
    """Remove a created recipe from the community feed"""
    try:
        recipe = CreatedRecipe.objects.get(id=recipe_id, creator=request.user)
        
        # Find and unshare the corresponding Recipe/UserRecipe
        try:
            recipe_obj = Recipe.objects.get(recipe_id=f"created_{recipe.id}")
            user_recipe = UserRecipe.objects.get(user=request.user, recipe=recipe_obj)
            user_recipe.is_shared = False
            user_recipe.save()
        except (Recipe.DoesNotExist, UserRecipe.DoesNotExist):
            pass  # Handle case where Recipe/UserRecipe doesn't exist
        
        # Update the original created recipe
        recipe.is_shared = False
        recipe.save()
        
        messages.success(request, f'"{recipe.title}" has been removed from the community feed.')
    except CreatedRecipe.DoesNotExist:
        messages.error(request, 'Recipe not found.')
    
    return redirect('my_recipes')