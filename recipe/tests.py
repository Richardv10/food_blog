from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from recipe.models import Recipe, UserRecipe, RecipeComment
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError


# ============================================
# RECIPE MODEL TESTS
# ============================================

class RecipeModelTest(TestCase):
    """Test suite for Recipe model"""
    
    def setUp(self):
        """Set up test data"""
        self.recipe = Recipe.objects.create(
            recipe_id='12345',
            title='Test Recipe',
            image_url='https://example.com/image.jpg',
            summary='A delicious test recipe',
            instructions='Mix and cook',
            ingredients=[
                {'original': '2 cups flour'},
                {'original': '1 cup sugar'}
            ],
            ready_in_minutes=30,
            servings=4,
            source_url='https://example.com/recipe',
            is_cached=True
        )
    
    def test_recipe_creation(self):
        """Test that a recipe is created correctly"""
        self.assertEqual(self.recipe.recipe_id, '12345')
        self.assertEqual(self.recipe.title, 'Test Recipe')
        self.assertEqual(self.recipe.servings, 4)
        self.assertTrue(self.recipe.is_cached)
        self.assertIsNotNone(self.recipe.cached_at)
    
    def test_recipe_str_method(self):
        """Test the string representation of the recipe"""
        self.assertEqual(str(self.recipe), 'Test Recipe')
    
    def test_recipe_str_without_title(self):
        """Test string representation when title is empty"""
        recipe = Recipe.objects.create(recipe_id='67890')
        self.assertEqual(str(recipe), 'Recipe 67890')
    
    def test_recipe_unique_recipe_id(self):
        """Test that recipe_id must be unique"""
        with self.assertRaises(Exception):
            Recipe.objects.create(recipe_id='12345', title='Duplicate')
    
    def test_recipe_ingredients_json_field(self):
        """Test that ingredients are stored as JSON"""
        self.assertIsInstance(self.recipe.ingredients, list)
        self.assertEqual(len(self.recipe.ingredients), 2)
        self.assertEqual(self.recipe.ingredients[0]['original'], '2 cups flour')
    
    def test_recipe_optional_fields(self):
        """Test creating recipe with only required fields"""
        recipe = Recipe.objects.create(recipe_id='minimal')
        self.assertEqual(recipe.title, '')
        self.assertIsNone(recipe.image_url)
        self.assertIsNone(recipe.summary)
        self.assertFalse(recipe.is_cached)
    
    def test_recipe_cached_at_auto_update(self):
        """Test that cached_at updates automatically"""
        original_time = self.recipe.cached_at
        self.recipe.title = 'Updated Title'
        self.recipe.save()
        self.recipe.refresh_from_db()
        self.assertGreater(self.recipe.cached_at, original_time)


# ============================================
# USER RECIPE MODEL TESTS
# ============================================

class UserRecipeModelTest(TestCase):
    """Test suite for UserRecipe model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.recipe = Recipe.objects.create(
            recipe_id='12345',
            title='Test Recipe',
            is_cached=True
        )
        
        self.user_recipe = UserRecipe.objects.create(
            user=self.user,
            recipe=self.recipe,
            rating=5,
            is_shared=False
        )
    
    def test_user_recipe_creation(self):
        """Test that a user recipe is created correctly"""
        self.assertEqual(self.user_recipe.user, self.user)
        self.assertEqual(self.user_recipe.recipe, self.recipe)
        self.assertEqual(self.user_recipe.rating, 5)
        self.assertFalse(self.user_recipe.is_shared)
        self.assertIsNotNone(self.user_recipe.created_at)
    
    def test_user_recipe_str_method(self):
        """Test the string representation"""
        expected = f"{self.user.username} saved {self.recipe}"
        self.assertEqual(str(self.user_recipe), expected)
    
    def test_user_recipe_str_when_shared(self):
        """Test string representation when shared"""
        self.user_recipe.is_shared = True
        self.user_recipe.save()
        expected = f"{self.user.username} shared {self.recipe}"
        self.assertEqual(str(self.user_recipe), expected)
    
    def test_user_recipe_unique_constraint(self):
        """Test that user-recipe combination must be unique"""
        with self.assertRaises(Exception):
            UserRecipe.objects.create(
                user=self.user,
                recipe=self.recipe
            )
    
    def test_user_recipe_rating_validation(self):
        """Test that rating must be between 0 and 5"""
        user_recipe = UserRecipe.objects.create(
            user=self.user,
            recipe=Recipe.objects.create(recipe_id='test123')
        )
        
        # Valid ratings
        for rating in [0, 1, 2, 3, 4, 5]:
            user_recipe.rating = rating
            user_recipe.full_clean()  # Should not raise
        
        # Invalid ratings should raise validation error
        user_recipe.rating = 6
        with self.assertRaises(ValidationError):
            user_recipe.full_clean()
        
        user_recipe.rating = -1
        with self.assertRaises(ValidationError):
            user_recipe.full_clean()
    
    def test_user_recipe_ordering(self):
        """Test that user recipes are ordered by created_at descending"""
        recipe2 = Recipe.objects.create(recipe_id='67890', title='Newer Recipe')
        user_recipe2 = UserRecipe.objects.create(
            user=self.user,
            recipe=recipe2
        )
        
        user_recipes = UserRecipe.objects.all()
        self.assertEqual(user_recipes[0], user_recipe2)
        self.assertEqual(user_recipes[1], self.user_recipe)
    
    def test_user_recipe_cascade_delete_with_user(self):
        """Test that user recipes are deleted when user is deleted"""
        user_recipe_id = self.user_recipe.id
        self.user.delete()
        
        with self.assertRaises(UserRecipe.DoesNotExist):
            UserRecipe.objects.get(id=user_recipe_id)
    
    def test_user_recipe_cascade_delete_with_recipe(self):
        """Test that user recipes are deleted when recipe is deleted"""
        user_recipe_id = self.user_recipe.id
        self.recipe.delete()
        
        with self.assertRaises(UserRecipe.DoesNotExist):
            UserRecipe.objects.get(id=user_recipe_id)
    
    def test_user_recipe_optional_fields(self):
        """Test creating user recipe without optional fields"""
        recipe = Recipe.objects.create(recipe_id='minimal123')
        user_recipe = UserRecipe.objects.create(
            user=self.user,
            recipe=recipe
        )
        
        self.assertIsNone(user_recipe.rating)
        self.assertIsNone(user_recipe.message)
        self.assertIsNone(user_recipe.shared_at)
        self.assertFalse(user_recipe.is_shared)
    
    def test_user_recipe_shared_at_timestamp(self):
        """Test that shared_at is set when sharing"""
        self.assertIsNone(self.user_recipe.shared_at)
        
        self.user_recipe.is_shared = True
        self.user_recipe.shared_at = timezone.now()
        self.user_recipe.save()
        
        self.assertIsNotNone(self.user_recipe.shared_at)


# ============================================
# SAVE RECIPE VIEW TESTS
# ============================================

class SaveRecipeViewTest(TestCase):
    """Test suite for saving recipes"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.recipe = Recipe.objects.create(
            recipe_id='12345',
            title='Test Recipe',
            is_cached=True
        )
    
    @patch('recipe.views.get_or_fetch_recipe')
    def test_save_recipe_authenticated(self, mock_get_recipe):
        """Test saving a recipe while authenticated"""
        mock_get_recipe.return_value = (self.recipe, {'id': 12345, 'title': 'Test Recipe'})
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('save_recipe', args=[12345])
        
        response = self.client.get(url)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify UserRecipe was created
        self.assertEqual(UserRecipe.objects.count(), 1)
        user_recipe = UserRecipe.objects.first()
        self.assertEqual(user_recipe.user, self.user)
        self.assertEqual(user_recipe.recipe, self.recipe)
        self.assertFalse(user_recipe.is_shared)
    
    @patch('recipe.views.get_or_fetch_recipe')
    def test_save_recipe_already_saved(self, mock_get_recipe):
        """Test saving a recipe that's already saved"""
        mock_get_recipe.return_value = (self.recipe, {'id': 12345, 'title': 'Test Recipe'})
        
        # First save
        UserRecipe.objects.create(user=self.user, recipe=self.recipe)
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('save_recipe', args=[12345])
        
        response = self.client.get(url)
        
        # Should still have only one UserRecipe
        self.assertEqual(UserRecipe.objects.count(), 1)
    
    def test_save_recipe_unauthenticated(self):
        """Test that unauthenticated users cannot save recipes"""
        url = reverse('save_recipe', args=[12345])
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


# ============================================
# DELETE RECIPE VIEW TESTS
# ============================================

class DeleteSavedRecipeViewTest(TestCase):
    """Test suite for deleting saved recipes"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        
        self.recipe = Recipe.objects.create(
            recipe_id='12345',
            title='Test Recipe',
            is_cached=True
        )
        
        self.user_recipe = UserRecipe.objects.create(
            user=self.user,
            recipe=self.recipe
        )
    
    def test_delete_recipe_authenticated_owner(self):
        """Test that user can delete their saved recipe"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('delete_recipe', args=[12345])
        
        # Verify recipe exists
        self.assertEqual(UserRecipe.objects.count(), 1)
        
        response = self.client.get(url)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify UserRecipe was deleted
        self.assertEqual(UserRecipe.objects.count(), 0)
    
    def test_delete_recipe_non_owner(self):
        """Test that users cannot delete other users' saved recipes"""
        self.client.login(username='otheruser', password='testpass123')
        url = reverse('delete_recipe', args=[12345])
        
        response = self.client.get(url)
        
        # UserRecipe should still exist (will fail to find user's recipe)
        self.assertEqual(UserRecipe.objects.count(), 1)
    
    def test_delete_recipe_unauthenticated(self):
        """Test that unauthenticated users cannot delete recipes"""
        url = reverse('delete_recipe', args=[12345])
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


# ============================================
# SHARE RECIPE VIEW TESTS
# ============================================

class ShareSavedRecipeViewTest(TestCase):
    """Test suite for sharing saved recipes"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.recipe = Recipe.objects.create(
            recipe_id='12345',
            title='Test Recipe',
            is_cached=True
        )
    
    @patch('recipe.views.get_or_fetch_recipe')
    def test_share_recipe_new(self, mock_get_recipe):
        """Test sharing a recipe that isn't saved yet"""
        mock_get_recipe.return_value = (self.recipe, {'id': 12345, 'title': 'Test Recipe'})
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('share_recipe', args=[12345])
        
        share_data = {
            'message': 'Check out this recipe!',
            'rating': '5'
        }
        
        response = self.client.post(url, share_data)
        
        # Check redirect to home
        self.assertEqual(response.status_code, 302)
        
        # Verify UserRecipe was created and shared
        self.assertEqual(UserRecipe.objects.count(), 1)
        user_recipe = UserRecipe.objects.first()
        self.assertTrue(user_recipe.is_shared)
        self.assertEqual(user_recipe.message, 'Check out this recipe!')
        self.assertEqual(user_recipe.rating, 5)
        self.assertIsNotNone(user_recipe.shared_at)
    
    @patch('recipe.views.get_or_fetch_recipe')
    def test_share_recipe_already_saved(self, mock_get_recipe):
        """Test sharing a recipe that's already saved"""
        mock_get_recipe.return_value = (self.recipe, {'id': 12345, 'title': 'Test Recipe'})
        
        # Pre-save the recipe
        UserRecipe.objects.create(
            user=self.user,
            recipe=self.recipe,
            is_shared=False
        )
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('share_recipe', args=[12345])
        
        share_data = {
            'message': 'Now sharing!',
            'rating': '4'
        }
        
        response = self.client.post(url, share_data)
        
        # Should still have only one UserRecipe, but now shared
        self.assertEqual(UserRecipe.objects.count(), 1)
        user_recipe = UserRecipe.objects.first()
        self.assertTrue(user_recipe.is_shared)
        self.assertEqual(user_recipe.message, 'Now sharing!')
    
    def test_share_recipe_get_request(self):
        """Test GET request to share recipe redirects to recipe detail"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('share_recipe', args=[12345])
        
        response = self.client.get(url)
        
        # Should redirect to recipe detail (sharing is done via modal)
        self.assertEqual(response.status_code, 302)
        self.assertIn('recipe/12345', response.url)
    
    def test_share_recipe_unauthenticated(self):
        """Test that unauthenticated users cannot share"""
        url = reverse('share_recipe', args=[12345])
        response = self.client.post(url, {'message': 'test'})
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


# ============================================
# UNSHARE RECIPE VIEW TESTS
# ============================================

class UnshareSavedRecipeViewTest(TestCase):
    """Test suite for unsharing saved recipes"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.recipe = Recipe.objects.create(
            recipe_id='12345',
            title='Test Recipe',
            is_cached=True
        )
        
        self.user_recipe = UserRecipe.objects.create(
            user=self.user,
            recipe=self.recipe,
            is_shared=True,
            shared_at=timezone.now(),
            message='Shared recipe'
        )
    
    def test_unshare_recipe_authenticated_owner(self):
        """Test that user can unshare their recipe"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('unshare_saved_recipe', args=[12345])
        
        response = self.client.get(url)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify recipe is unshared
        self.user_recipe.refresh_from_db()
        self.assertFalse(self.user_recipe.is_shared)
    
    def test_unshare_recipe_unauthenticated(self):
        """Test that unauthenticated users cannot unshare"""
        url = reverse('unshare_saved_recipe', args=[12345])
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        
        # Recipe should still be shared
        self.user_recipe.refresh_from_db()
        self.assertTrue(self.user_recipe.is_shared)


# ============================================
# MY RECIPES VIEW TEST
# ============================================

class MyRecipesViewTest(TestCase):
    """Test suite for my recipes view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create some saved recipes
        self.recipe1 = Recipe.objects.create(recipe_id='111', title='Recipe 1')
        self.recipe2 = Recipe.objects.create(recipe_id='222', title='Recipe 2')
        
        UserRecipe.objects.create(user=self.user, recipe=self.recipe1)
        UserRecipe.objects.create(user=self.user, recipe=self.recipe2, is_shared=True)
    
    def test_my_recipes_authenticated(self):
        """Test viewing my recipes page while authenticated"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('my_recipes')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe/my_recipes.html')
        
        # Check that saved recipes are in context
        self.assertIn('saved_recipes', response.context)
        saved_recipes = response.context['saved_recipes']
        self.assertEqual(saved_recipes.count(), 2)
    
    def test_my_recipes_unauthenticated(self):
        """Test that unauthenticated users are redirected"""
        url = reverse('my_recipes')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


# ============================================
# INTEGRATION TESTS
# ============================================

class RecipeUserRecipeIntegrationTest(TestCase):
    """Integration tests for Recipe and UserRecipe workflows"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.recipe = Recipe.objects.create(
            recipe_id='12345',
            title='Integration Test Recipe',
            is_cached=True
        )
    
    @patch('recipe.views.get_or_fetch_recipe')
    def test_complete_save_share_unshare_delete_workflow(self, mock_get_recipe):
        """Test complete workflow: Save → Share → Unshare → Delete"""
        mock_get_recipe.return_value = (self.recipe, {'id': 12345, 'title': 'Test Recipe'})
        
        # SAVE
        save_url = reverse('save_recipe', args=[12345])
        save_response = self.client.get(save_url)
        self.assertEqual(save_response.status_code, 302)
        
        user_recipe = UserRecipe.objects.first()
        self.assertIsNotNone(user_recipe)
        self.assertFalse(user_recipe.is_shared)
        
        # SHARE
        share_url = reverse('share_recipe', args=[12345])
        share_data = {
            'message': 'Great recipe!',
            'rating': '5'
        }
        share_response = self.client.post(share_url, share_data)
        self.assertEqual(share_response.status_code, 302)
        
        user_recipe.refresh_from_db()
        self.assertTrue(user_recipe.is_shared)
        self.assertEqual(user_recipe.message, 'Great recipe!')
        self.assertEqual(user_recipe.rating, 5)
        
        # UNSHARE
        unshare_url = reverse('unshare_saved_recipe', args=[12345])
        unshare_response = self.client.get(unshare_url)
        self.assertEqual(unshare_response.status_code, 302)
        
        user_recipe.refresh_from_db()
        self.assertFalse(user_recipe.is_shared)
        
        # DELETE
        delete_url = reverse('delete_recipe', args=[12345])
        delete_response = self.client.get(delete_url)
        self.assertEqual(delete_response.status_code, 302)
        
        self.assertEqual(UserRecipe.objects.count(), 0)
    
    @patch('recipe.views.get_or_fetch_recipe')
    def test_multiple_users_saving_same_recipe(self, mock_get_recipe):
        """Test multiple users saving and sharing the same recipe"""
        mock_get_recipe.return_value = (self.recipe, {'id': 12345, 'title': 'Test Recipe'})
        
        # First user saves
        save_url = reverse('save_recipe', args=[12345])
        self.client.get(save_url)
        
        # Second user saves
        user2 = User.objects.create_user(username='user2', password='pass123')
        self.client.login(username='user2', password='pass123')
        self.client.get(save_url)
        
        # Both should have saved the recipe
        self.assertEqual(UserRecipe.objects.count(), 2)
        
        # Verify different users
        user_recipes = UserRecipe.objects.all()
        users = [ur.user for ur in user_recipes]
        self.assertIn(self.user, users)
        self.assertIn(user2, users)
        
        # Both point to same Recipe
        for ur in user_recipes:
            self.assertEqual(ur.recipe, self.recipe)
