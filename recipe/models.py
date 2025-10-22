from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Recipe(models.Model):
    recipe_id = models.CharField(max_length=100, unique=True)  # ID from the external API
    title = models.CharField(max_length=255, blank=True)    # optional metadata
    

    def __str__(self):
        return self.title or f"Recipe {self.recipe_id}"


class UserRecipeLibrary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipe_library")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rate this recipe from 0 to 5 stars"
    )
    
    class Meta:
        unique_together = ("user", "recipe")  # prevent duplicates

    def __str__(self):
        return f"{self.user.username} → {self.recipe}"
    
class SharedRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_recipes")
    shared_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rate this recipe from 0 to 5 stars"
    )
    
    def __str__(self):
        return f"{self.shared_by.username} shared {self.recipe}"
    
class RecipeComment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment_rating = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rate this recipe from 0 to 5 stars"
    )

    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe}"
    

