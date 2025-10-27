
# Imports
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
import requests 
from .models import Recipe, UserRecipe, RecipeComment

# Helper function to fetch and cache recipe data
def get_or_fetch_recipe(recipe_id):
    """
    Get recipe from database cache or fetch from API if not cached.
    Returns a tuple: (recipe_obj, recipe_data_dict)
    """
    recipe_id_str = str(recipe_id)
    
    # Try to get from database
    try:
        recipe_obj = Recipe.objects.get(recipe_id=recipe_id_str)
        
        # If cached, return cached data
        if recipe_obj.is_cached:
            recipe_data = {
                'id': int(recipe_id),
                'title': recipe_obj.title,
                'image': recipe_obj.image_url,
                'summary': recipe_obj.summary,
                'instructions': recipe_obj.instructions,
                'extendedIngredients': recipe_obj.ingredients or [],
                'readyInMinutes': recipe_obj.ready_in_minutes,
                'servings': recipe_obj.servings,
                'sourceUrl': recipe_obj.source_url,
            }
            return recipe_obj, recipe_data
    except Recipe.DoesNotExist:
        pass
    
    # Fetch from API (if not cached)
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {'apiKey': settings.SPOONACULAR_API_KEY}
    response = requests.get(url, params=params)
    recipe_data = response.json()
    
    # Fix image URL
    recipe_data['image'] = f"https://spoonacular.com/recipeImages/{recipe_id}-312x231.jpg"
    
    # Create recipe in database with full cached data
    recipe_obj, created = Recipe.objects.get_or_create(
        recipe_id=recipe_id_str,
        defaults={
            'title': recipe_data.get('title', f'Recipe {recipe_id}'),
            'image_url': recipe_data.get('image'),
            'summary': recipe_data.get('summary', ''),
            'instructions': recipe_data.get('instructions', ''),
            'ingredients': recipe_data.get('extendedIngredients', []),
            'ready_in_minutes': recipe_data.get('readyInMinutes'),
            'servings': recipe_data.get('servings'),
            'source_url': recipe_data.get('sourceUrl'),
            'is_cached': True
        }
    )
    
    return recipe_obj, recipe_data


def home_view(request):
    # Get all shared recipes for the feed, ordered by most recent
    shared_recipes = UserRecipe.objects.filter(
        is_shared=True
    ).select_related('user', 'recipe').order_by('-shared_at')
    
    # Get comments for each shared recipe (limit to 3 most recent for feed display)
    recipes_with_comments = []
    for shared_recipe in shared_recipes:
        comments = RecipeComment.objects.filter(
            recipe=shared_recipe.recipe
        ).select_related('user').order_by('-created_at')[:3]
        
        comment_count = RecipeComment.objects.filter(
            recipe=shared_recipe.recipe
        ).count()
        
        recipes_with_comments.append({
            'shared_recipe': shared_recipe,
            'recent_comments': comments,
            'comment_count': comment_count
        })
    
    return render(request, "home.html", {'recipes_with_comments': recipes_with_comments})

# Share recipe to Feed
def share_recipe(request, recipe_id):
    """Share a recipe to the homepage feed and cache full recipe data"""
    if request.method == 'POST':
        message = request.POST.get('message', '')
        rating = request.POST.get('rating', None)
        
        # Use helper to fetch and cache recipe data
        recipe_obj, recipe_data = get_or_fetch_recipe(recipe_id)
        
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
    # Use cached data if available
    recipe_obj, recipe = get_or_fetch_recipe(recipe_id)
    
    # Check if recipe is already saved by the user
    is_saved = UserRecipe.objects.filter(
        user=request.user,
        recipe__recipe_id=str(recipe_id)
    ).exists() if request.user.is_authenticated else False
    
     # Get all comments for this recipe
    comments = RecipeComment.objects.filter(
        recipe=recipe_obj
    ).select_related('user').order_by('-created_at')
    
    return render(request, 'search/detail.html', {
        'recipe': recipe,
        'is_saved': is_saved,
        'comments': comments
    })

def random_recipe(request):
    """Get a random recipe from Spoonacular API and cache it"""
    url = "https://api.spoonacular.com/recipes/random"
    params = {
        'apiKey': settings.SPOONACULAR_API_KEY,
        'number': 1  # Get one random recipe
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    recipe_data = data['recipes'][0]
    recipe_id = recipe_data['id']
    
    # Cache this recipe for future use
    recipe_obj, recipe = get_or_fetch_recipe(recipe_id)
    
    return render(request, 'search/detail.html', {'recipe': recipe})

# Save Recipe to User's Favorites

def save_recipe(request, recipe_id):
    """Save a recipe to the user's collection and cache full recipe data"""
    # Use helper to fetch and cache recipe data
    recipe_obj, recipe_data = get_or_fetch_recipe(recipe_id)
    
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
    
    # Import here to avoid circular imports
    from blog.models import CreatedRecipe
    created_recipes = CreatedRecipe.objects.filter(creator=request.user).order_by('-created_at')
    
    return render(request, 'recipe/my_recipes.html', {
        'saved_recipes': saved_recipes,
        'created_recipes': created_recipes
    })

# Delete Recipe from User's Favorites
#  
def delete_recipe(request, recipe_id):
        user_recipe = UserRecipe.objects.get(user=request.user, recipe__recipe_id=str(recipe_id))
        user_recipe.delete()
        messages.success(request, "Recipe deleted from your favorites.")
        return redirect('my_recipes')

def make_comment(request, recipe_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        rating = request.POST.get('rating', None)
        recipe_obj, _ = get_or_fetch_recipe(recipe_id)
# Create the comment
        RecipeComment.objects.create(
            recipe=recipe_obj,
            user=request.user,
            comment=comment_text,
            rating=rating if rating else None
        )
        messages.success(request, "Your comment has been added.")
        return redirect('recipe_detail', recipe_id=recipe_id)
    
    return redirect('recipe_detail', recipe_id=recipe_id)


def make_feed_comment(request, recipe_id):
    """Handle comments submitted from the home feed"""
    if request.method == 'POST' and request.user.is_authenticated:
        comment_text = request.POST.get('comment')
        
        if comment_text:
            recipe_obj, _ = get_or_fetch_recipe(recipe_id)
            
            # Create the comment
            RecipeComment.objects.create(
                recipe=recipe_obj,
                user=request.user,
                comment=comment_text,
            )
            
            messages.success(request, "Your comment has been added.")
    
    return redirect('home')
