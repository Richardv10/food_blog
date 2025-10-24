
# Imports
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
import requests 
from .models import Recipe, UserRecipe



def home_view(request):
    # Get all shared recipes for the feed, ordered by most recent
    shared_recipes = UserRecipe.objects.filter(
        is_shared=True
    ).select_related('user', 'recipe').order_by('-shared_at')
    
    return render(request, "home.html", {'shared_recipes': shared_recipes})

def share_recipe(request, recipe_id):
    """Share a recipe to the homepage feed"""
    if request.method == 'POST':
        message = request.POST.get('message', '')
        rating = request.POST.get('rating', None)
        
        # Fetch recipe data from API to get the title
        url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
        params = {'apiKey': settings.SPOONACULAR_API_KEY}
        response = requests.get(url, params=params)
        recipe_data = response.json()
        
        # Get or create the Recipe object
        recipe_obj, created = Recipe.objects.get_or_create(
            recipe_id=str(recipe_id),
            defaults={'title': recipe_data.get('title', f'Recipe {recipe_id}')}
        )
        
        # Get or create UserRecipe entry and mark as shared
        user_recipe, created = UserRecipe.objects.get_or_create(
            user=request.user,
            recipe=recipe_obj,
            defaults={
                'is_shared': True,
                'message': message,
                'rating': rating if rating else None,
                'shared_at': timezone.now()
            }
        )
        
        # If it already exists but wasn't shared, update it
        if not created:
            user_recipe.is_shared = True
            user_recipe.message = message
            user_recipe.shared_at = timezone.now()
            if rating:
                user_recipe.rating = rating
            user_recipe.save()
            messages.success(request, "Recipe shared to the feed!")
        else:
            messages.success(request, "Recipe added to your favorites and shared!")
        
        return redirect('home')
    
    # GET request - show share form (optional)
    return render(request, 'recipe/share_recipe.html', {'recipe_id': recipe_id})
    



def search_recipes(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            'apiKey': settings.SPOONACULAR_API_KEY,
            'query': query,
            'number': 10
        }
        response = requests.get(url, params=params)
        data = response.json()
        recipes = data.get('results', [])
        return render(request, 'search/results.html', {'recipes': recipes})
    return render(request, 'search/search.html') 

def recipe_detail(request, recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {'apiKey': settings.SPOONACULAR_API_KEY}
    response = requests.get(url, params=params)
    recipe = response.json()
    
    # Fix image URL to use the working size format
    recipe['image'] = f"https://spoonacular.com/recipeImages/{recipe_id}-312x231.jpg"
    
    # Check if recipe is already saved by the user
    is_saved = UserRecipe.objects.filter(
        user=request.user,
        recipe__recipe_id=str(recipe_id)
    ).exists() if request.user.is_authenticated else False
    
    return render(request, 'search/detail.html', {
        'recipe': recipe,
        'is_saved': is_saved
    })

def random_recipe(request):
    """Get a random recipe from Spoonacular API"""
    url = "https://api.spoonacular.com/recipes/random"
    params = {
        'apiKey': settings.SPOONACULAR_API_KEY,
        'number': 1  # Get one random recipe
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    recipe = data['recipes'][0]
    recipe_id = recipe['id']
    
    # Fix image URL
    if 'image' in recipe and recipe['image']:
        recipe['image'] = f"https://spoonacular.com/recipeImages/{recipe_id}-312x231.jpg"
    
    return render(request, 'search/detail.html', {'recipe': recipe})

# Save Recipe to User's Favorites

def save_recipe(request, recipe_id):
    # Fetch recipe data from API to get the title
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {'apiKey': settings.SPOONACULAR_API_KEY}
    response = requests.get(url, params=params)
    recipe_data = response.json()
    
    # Get or create the Recipe object with the title
    recipe_obj, created = Recipe.objects.get_or_create(
        recipe_id=str(recipe_id),
        defaults={'title': recipe_data.get('title', f'Recipe {recipe_id}')}
    )
    
    # Add to user's library (or get if already exists)
    user_recipe, created = UserRecipe.objects.get_or_create(
        user=request.user,
        recipe=recipe_obj
    )
    
    if created:
        messages.success(request, "Recipe added to your favorites!")
    else:
        messages.info(request, "This recipe is already in your favorites.")
    
    return redirect('recipe_detail', recipe_id=recipe_id)

# Display User Recipes

def my_recipes(request):
    saved_recipes = UserRecipe.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'recipe/my_recipes.html', {'saved_recipes': saved_recipes})

# Delete Recipe from User's Favorites
#  
def delete_recipe(request, recipe_id):
        user_recipe = UserRecipe.objects.get(user=request.user, recipe__recipe_id=str(recipe_id))
        user_recipe.delete()
        messages.success(request, "Recipe deleted from your favorites.")
        return redirect('my_recipes')
