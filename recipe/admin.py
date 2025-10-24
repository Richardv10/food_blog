from django.contrib import admin
from .models import Recipe, UserRecipe, RecipeComment

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe_id', 'title')
    search_fields = ('recipe_id', 'title')

@admin.register(UserRecipe)
class UserRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'is_shared', 'rating', 'created_at')
    list_filter = ('is_shared', 'created_at')
    search_fields = ('user__username', 'recipe__title')

@admin.register(RecipeComment)
class RecipeCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('user__username', 'recipe__title', 'comment')
