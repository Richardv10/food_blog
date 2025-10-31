from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField

class CreatedRecipe(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_created_recipes")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField(help_text="List each ingredient on a new line")
    instructions = models.TextField(help_text="Describe the cooking steps")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ready_in_minutes = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    servings = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    featured_image = CloudinaryField('image', default='placeholder')
    is_shared = models.BooleanField(default=False)
    shared_message = models.TextField(blank=True, null=True, help_text="Optional message when sharing")
    shared_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.creator.username}"
        
    def get_ingredients_list(self):
        #Return ingredients as a list, split by lines
        return [ingredient.strip() for ingredient in self.ingredients.split('\n') if ingredient.strip()]
        
    def get_instructions_list(self):
        #Return instructions as a list, split by lines or double newlines
        # Split by double newlines first, then single newlines
        instructions = self.instructions.replace('\r\n', '\n')
        steps = [step.strip() for step in instructions.split('\n') if step.strip()]
        return steps
    
    def get_average_rating(self):
        """Calculate the average rating for this user-created recipe from comments"""
        from recipe.models import Recipe, RecipeComment
        try:
            # Get the Recipe object that corresponds to this created recipe
            recipe_obj = Recipe.objects.get(recipe_id=f"created_{self.id}")
            # Get all comments with ratings for this recipe
            rated_comments = recipe_obj.comments.filter(rating__isnull=False)
            if rated_comments.exists():
                total_rating = sum(comment.rating for comment in rated_comments)
                return round(total_rating / rated_comments.count(), 1)
        except Recipe.DoesNotExist:
            pass
        return None
    
    def get_rating_count(self):
        """Get the total number of ratings for this user-created recipe"""
        from recipe.models import Recipe
        try:
            recipe_obj = Recipe.objects.get(recipe_id=f"created_{self.id}")
            return recipe_obj.comments.filter(rating__isnull=False).count()
        except Recipe.DoesNotExist:
            return 0