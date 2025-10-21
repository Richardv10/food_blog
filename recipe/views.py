from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import requests  # Fixed import

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
    # Spoonacular images: https://spoonacular.com/recipeImages/{id}-{size}.{format}
    if 'image' in recipe and recipe['image']:
        # Replace the image URL to ensure consistent thumbnail size
        recipe['image'] = f"https://spoonacular.com/recipeImages/{recipe_id}-312x231.jpg"
    
    return render(request, 'search/detail.html', {'recipe': recipe})

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
