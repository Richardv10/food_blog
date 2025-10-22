
# Imports
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
import requests 
from .models import Recipe, UserRecipeLibrary



def home_view(request):
    return render(request, "home.html") 





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
    return render(request, 'search/search.html')  # Fixed indentation

def recipe_detail(request, recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {'apiKey': settings.SPOONACULAR_API_KEY}
    response = requests.get(url, params=params)
    recipe = response.json()
    
    # Fix image URL to use the correct size format
    recipe['image'] = f"https://spoonacular.com/recipeImages/{recipe_id}-312x231.jpg"
    
    # Check if recipe is already saved by the user
    is_saved = UserRecipeLibrary.objects.filter(
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

def save_recipe(request, recipe_id):
    """Save a recipe to the user's collection"""
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
    library_entry, created = UserRecipeLibrary.objects.get_or_create(
        user=request.user,
        recipe=recipe_obj
    )
    
    if created:
        messages.success(request, "Recipe added to your favorites!")
    else:
        messages.info(request, "This recipe is already in your favorites.")
    
    return redirect('recipe_detail', recipe_id=recipe_id)

def my_recipes(request):
    """Display user's saved recipes"""
    saved_recipes = UserRecipeLibrary.objects.filter(user=request.user).order_by('-added_at')
    
    return render(request, 'recipe/my_recipes.html', {'saved_recipes': saved_recipes})
