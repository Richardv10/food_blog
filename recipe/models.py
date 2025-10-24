from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Recipe(models.Model):
    recipe_id = models.CharField(max_length=100, unique=True)  # ID from the external API
    title = models.CharField(max_length=255, blank=True)    
    

    def __str__(self):
        return self.title or f"Recipe {self.recipe_id}"


class UserRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="user_recipes")
    is_shared = models.BooleanField(default=False)  # Whether recipe is shared publicly
    message = models.TextField(blank=True, null=True)  # Optional message when sharing
    rating = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rate this recipe from 0 to 5 stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # When added to library
    shared_at = models.DateTimeField(blank=True, null=True)  # When shared (if shared)
    
    class Meta:
        unique_together = ("user", "recipe")  # Prevent duplicate user-recipe entries
        ordering = ['-created_at']

    def __str__(self):
        status = "shared" if self.is_shared else "saved"
        return f"{self.user.username} {status} {self.recipe}"

# User comments on recipes
class RecipeComment(models.Model):
   
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    rating = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rate this recipe from 0 to 5 stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe}"
    

