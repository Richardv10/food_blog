from django.contrib import admin
from .models import CreatedRecipe

@admin.register(CreatedRecipe)
class CreatedRecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'servings', 'ready_in_minutes')
    list_filter = ('created_at', 'creator')
    search_fields = ('title', 'creator__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Recipe Information', {
            'fields': ('title', 'description', 'creator')
        }),
        ('Recipe Details', {
            'fields': ('ingredients', 'instructions', 'servings', 'ready_in_minutes', 'featured_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
