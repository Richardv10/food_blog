from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from blog.models import CreatedRecipe
from recipe.models import Recipe, UserRecipe, RecipeComment
from io import BytesIO
from PIL import Image


# ============================================
# MODEL TESTS
# ============================================

class CreatedRecipeModelTest(TestCase):
    """Test suite for CreatedRecipe model"""

    def setUp(self):
        """Set up test user and recipe"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.recipe = CreatedRecipe.objects.create(
            creator=self.user,
            title='Test Recipe',
            description='A delicious test recipe',
            ingredients='2 cups flour\n1 cup sugar\n3 eggs',
            instructions='Step 1: Mix ingredients\nStep 2: Bake at 350°F',
            servings=4,
            ready_in_minutes=30
        )

    def test_recipe_creation(self):
        """Test that a recipe is created correctly"""
        self.assertEqual(self.recipe.title, 'Test Recipe')
        self.assertEqual(self.recipe.creator, self.user)
        self.assertIsNotNone(self.recipe.created_at)
        self.assertFalse(self.recipe.is_shared)

    def test_recipe_str_method(self):
        """Test the string representation of the recipe"""
        expected_str = f"Test Recipe by {self.user.username}"
        self.assertEqual(str(self.recipe), expected_str)

    def test_get_ingredients_list(self):
        """Test that ingredients are correctly parsed into a list"""
        ingredients_list = self.recipe.get_ingredients_list()
        self.assertEqual(len(ingredients_list), 3)
        self.assertIn('2 cups flour', ingredients_list)
        self.assertIn('1 cup sugar', ingredients_list)
        self.assertIn('3 eggs', ingredients_list)

    def test_get_instructions_list(self):
        """Test that instructions are correctly parsed into a list"""
        instructions_list = self.recipe.get_instructions_list()
        self.assertEqual(len(instructions_list), 2)
        self.assertIn('Step 1: Mix ingredients', instructions_list)
        self.assertIn('Step 2: Bake at 350°F', instructions_list)

    def test_recipe_ordering(self):
        """Test that recipes are ordered by created_at in descending order"""
        recipe2 = CreatedRecipe.objects.create(
            creator=self.user,
            title='Newer Recipe',
            ingredients='test',
            instructions='test'
        )
        recipes = CreatedRecipe.objects.all()
        self.assertEqual(recipes[0], recipe2)  # Newer recipe should be first
        self.assertEqual(recipes[1], self.recipe)


# ============================================
# VIEW TESTS - CREATE
# ============================================

class CreateRecipeViewTest(TestCase):
    """Test suite for create recipe view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.create_url = reverse('create_recipe')

    def test_create_recipe_get_authenticated(self):
        """Test GET request to create recipe page while authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_recipe.html')

    def test_create_recipe_get_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn('/accounts/login/', response.url)

    def test_create_recipe_post_valid_data(self):
        """Test creating a recipe with valid POST data"""
        self.client.login(username='testuser', password='testpass123')

        recipe_data = {
            'title': 'Chocolate Cake',
            'description': 'A rich chocolate cake',
            'ingredients': '2 cups flour\n1 cup cocoa',
            'instructions': 'Mix and bake',
            'servings': '8',
            'ready_in_minutes': '45'
        }

        response = self.client.post(self.create_url, recipe_data)

        # Check redirect to my_recipes
        self.assertEqual(response.status_code, 302)
        self.assertIn('my-recipes', response.url)

        # Check recipe was created
        self.assertEqual(CreatedRecipe.objects.count(), 1)
        recipe = CreatedRecipe.objects.first()
        self.assertEqual(recipe.title, 'Chocolate Cake')
        self.assertEqual(recipe.creator, self.user)
        self.assertEqual(recipe.servings, 8)

    def test_create_recipe_post_minimal_data(self):
        """Test creating a recipe with only required fields"""
        self.client.login(username='testuser', password='testpass123')

        recipe_data = {
            'title': 'Simple Recipe',
            'ingredients': 'Ingredient 1',
            'instructions': 'Step 1'
        }

        response = self.client.post(self.create_url, recipe_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(CreatedRecipe.objects.count(), 1)
        recipe = CreatedRecipe.objects.first()
        self.assertEqual(recipe.title, 'Simple Recipe')
        self.assertIsNone(recipe.servings)
        self.assertIsNone(recipe.ready_in_minutes)


# ============================================
# VIEW TESTS - READ
# ============================================

class ReadRecipeViewTest(TestCase):
    """Test suite for reading recipe views"""

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

        self.recipe = CreatedRecipe.objects.create(
            creator=self.user,
            title='Private Recipe',
            ingredients='test',
            instructions='test',
            is_shared=False
        )

        self.shared_recipe = CreatedRecipe.objects.create(
            creator=self.user,
            title='Public Recipe',
            ingredients='test',
            instructions='test',
            is_shared=True
        )

    def test_created_recipe_detail_owner(self):
        """Test that recipe owner can view their own recipe"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('created_recipe_detail', args=[self.recipe.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'created_recipe_detail.html')
        self.assertEqual(response.context['recipe'], self.recipe)

    def test_created_recipe_detail_non_owner(self):
        """Test that non-owners cannot view private recipes"""
        self.client.login(username='otheruser', password='testpass123')
        url = reverse('created_recipe_detail', args=[self.recipe.id])
        response = self.client.get(url)

        # Should redirect to my_recipes with error
        self.assertEqual(response.status_code, 302)

    def test_public_recipe_detail_authenticated(self):
        """Test that authenticated users can view shared recipes"""
        self.client.login(username='otheruser', password='testpass123')
        url = reverse(
            'public_created_recipe_detail',
            args=[self.shared_recipe.id]
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public_created_recipe_detail.html')

    def test_public_recipe_detail_unauthenticated(self):
        """Test that unauthenticated users can view shared recipes"""
        url = reverse(
            'public_created_recipe_detail',
            args=[self.shared_recipe.id]
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_public_recipe_detail_private_recipe(self):
        """Test that private recipes cannot be viewed via public URL"""
        url = reverse('public_created_recipe_detail', args=[self.recipe.id])
        response = self.client.get(url)

        # Should redirect with error
        self.assertEqual(response.status_code, 302)


# ============================================
# VIEW TESTS - UPDATE
# ============================================

class UpdateRecipeViewTest(TestCase):
    """Test suite for update recipe view"""

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

        self.recipe = CreatedRecipe.objects.create(
            creator=self.user,
            title='Original Title',
            description='Original description',
            ingredients='Original ingredients',
            instructions='Original instructions',
            servings=4,
            ready_in_minutes=30
        )

    def test_edit_recipe_get_authenticated_owner(self):
        """Test GET request to edit page by recipe owner"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit_created_recipe', args=[self.recipe.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_created_recipe.html')
        self.assertEqual(response.context['recipe'], self.recipe)

    def test_edit_recipe_get_non_owner(self):
        """Test that non-owners cannot access edit page"""
        self.client.login(username='otheruser', password='testpass123')
        url = reverse('edit_created_recipe', args=[self.recipe.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)  # Redirect

    def test_edit_recipe_post_valid_data(self):
        """Test updating a recipe with valid data"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit_created_recipe', args=[self.recipe.id])

        updated_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'ingredients': 'Updated ingredients',
            'instructions': 'Updated instructions',
            'servings': '6',
            'ready_in_minutes': '45'
        }

        response = self.client.post(url, updated_data)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Refresh recipe from database
        self.recipe.refresh_from_db()

        # Verify updates
        self.assertEqual(self.recipe.title, 'Updated Title')
        self.assertEqual(self.recipe.description, 'Updated description')
        self.assertEqual(self.recipe.servings, 6)
        self.assertEqual(self.recipe.ready_in_minutes, 45)

    def test_edit_recipe_post_partial_update(self):
        """Test updating only some fields"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit_created_recipe', args=[self.recipe.id])

        updated_data = {
            'title': 'New Title Only',
            'description': self.recipe.description,
            'ingredients': self.recipe.ingredients,
            'instructions': self.recipe.instructions
        }

        response = self.client.post(url, updated_data)

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'New Title Only')
        # Original values should remain
        self.assertEqual(self.recipe.servings, 4)

    def test_edit_recipe_unauthenticated(self):
        """Test that unauthenticated users cannot edit"""
        url = reverse('edit_created_recipe', args=[self.recipe.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


# ============================================
# VIEW TESTS - DELETE
# ============================================

class DeleteRecipeViewTest(TestCase):
    """Test suite for delete recipe view"""

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

        self.recipe = CreatedRecipe.objects.create(
            creator=self.user,
            title='Recipe to Delete',
            ingredients='test',
            instructions='test'
        )

    def test_delete_recipe_authenticated_owner(self):
        """Test that recipe owner can delete their recipe"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('delete_created_recipe', args=[self.recipe.id])

        # Verify recipe exists
        self.assertEqual(CreatedRecipe.objects.count(), 1)

        response = self.client.get(url)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Verify recipe was deleted
        self.assertEqual(CreatedRecipe.objects.count(), 0)

    def test_delete_recipe_non_owner(self):
        """Test that non-owners cannot delete recipes"""
        self.client.login(username='otheruser', password='testpass123')
        url = reverse('delete_created_recipe', args=[self.recipe.id])

        response = self.client.get(url)

        # Recipe should still exist
        self.assertEqual(CreatedRecipe.objects.count(), 1)

    def test_delete_recipe_unauthenticated(self):
        """Test that unauthenticated users cannot delete"""
        url = reverse('delete_created_recipe', args=[self.recipe.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        # Recipe should still exist
        self.assertEqual(CreatedRecipe.objects.count(), 1)

    def test_delete_nonexistent_recipe(self):
        """Test deleting a recipe that doesn't exist"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('delete_created_recipe', args=[99999])

        response = self.client.get(url)

        # Should redirect with error message
        self.assertEqual(response.status_code, 302)


# ============================================
# VIEW TESTS - SHARE/UNSHARE
# ============================================

class ShareRecipeViewTest(TestCase):
    """Test suite for sharing/unsharing recipes"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.recipe = CreatedRecipe.objects.create(
            creator=self.user,
            title='Recipe to Share',
            ingredients='test',
            instructions='test',
            is_shared=False
        )

    def test_share_recipe_authenticated(self):
        """Test sharing a recipe to the community feed"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('share_created_recipe', args=[self.recipe.id])

        share_data = {
            'message': 'Check out my amazing recipe!'
        }

        response = self.client.post(url, share_data)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Refresh recipe
        self.recipe.refresh_from_db()

        # Verify recipe is shared
        self.assertTrue(self.recipe.is_shared)
        self.assertEqual(
            self.recipe.shared_message,
            'Check out my amazing recipe!'
        )
        self.assertIsNotNone(self.recipe.shared_at)

        # Verify Recipe and UserRecipe objects were created
        recipe_obj = Recipe.objects.get(recipe_id=f"created_{self.recipe.id}")
        self.assertIsNotNone(recipe_obj)

        user_recipe = UserRecipe.objects.get(user=self.user, recipe=recipe_obj)
        self.assertTrue(user_recipe.is_shared)

    def test_unshare_recipe_authenticated(self):
        """Test unsharing a recipe from the community feed"""
        # First share the recipe
        self.recipe.is_shared = True
        self.recipe.shared_at = timezone.now()
        self.recipe.save()

        # Create Recipe and UserRecipe objects
        recipe_obj = Recipe.objects.create(
            recipe_id=f"created_{self.recipe.id}",
            title=self.recipe.title,
            is_cached=True
        )
        user_recipe = UserRecipe.objects.create(
            user=self.user,
            recipe=recipe_obj,
            is_shared=True
        )

        # Now unshare
        self.client.login(username='testuser', password='testpass123')
        url = reverse('unshare_created_recipe', args=[self.recipe.id])

        response = self.client.get(url)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Refresh objects
        self.recipe.refresh_from_db()
        user_recipe.refresh_from_db()

        # Verify recipe is unshared
        self.assertFalse(self.recipe.is_shared)
        self.assertFalse(user_recipe.is_shared)

    def test_share_recipe_unauthenticated(self):
        """Test that unauthenticated users cannot share"""
        url = reverse('share_created_recipe', args=[self.recipe.id])
        response = self.client.post(url, {'message': 'test'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


# ============================================
# INTEGRATION TESTS
# ============================================

class RecipeCRUDIntegrationTest(TestCase):
    """Integration tests for complete CRUD workflow"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_complete_crud_workflow(self):
        """Test complete Create -> Read -> Update -> Delete workflow"""

        # CREATE
        create_data = {
            'title': 'Integration Test Recipe',
            'description': 'A complete test',
            'ingredients': '1 cup test\n2 cups integration',
            'instructions': 'Test thoroughly',
            'servings': '4',
            'ready_in_minutes': '30'
        }

        create_response = self.client.post(
            reverse('create_recipe'),
            create_data
        )
        self.assertEqual(create_response.status_code, 302)

        recipe = CreatedRecipe.objects.first()
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.title, 'Integration Test Recipe')

        # READ
        read_url = reverse('created_recipe_detail', args=[recipe.id])
        read_response = self.client.get(read_url)
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(
            read_response.context['recipe'].title,
            'Integration Test Recipe'
        )

        # UPDATE
        update_data = {
            'title': 'Updated Integration Recipe',
            'description': 'Updated description',
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'servings': '6',
            'ready_in_minutes': '45'
        }

        update_url = reverse('edit_created_recipe', args=[recipe.id])
        update_response = self.client.post(update_url, update_data)
        self.assertEqual(update_response.status_code, 302)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, 'Updated Integration Recipe')
        self.assertEqual(recipe.servings, 6)

        # DELETE
        delete_url = reverse('delete_created_recipe', args=[recipe.id])
        delete_response = self.client.get(delete_url)
        self.assertEqual(delete_response.status_code, 302)

        self.assertEqual(CreatedRecipe.objects.count(), 0)

    def test_share_unshare_workflow(self):
        """Test sharing and unsharing workflow"""

        # Create a recipe
        recipe = CreatedRecipe.objects.create(
            creator=self.user,
            title='Share Test Recipe',
            ingredients='test',
            instructions='test'
        )

        self.assertFalse(recipe.is_shared)

        # Share the recipe
        share_url = reverse('share_created_recipe', args=[recipe.id])
        share_response = self.client.post(
            share_url,
            {'message': 'Great recipe!'}
        )

        recipe.refresh_from_db()
        self.assertTrue(recipe.is_shared)
        self.assertEqual(recipe.shared_message, 'Great recipe!')

        # Unshare the recipe
        unshare_url = reverse('unshare_created_recipe', args=[recipe.id])
        unshare_response = self.client.get(unshare_url)

        recipe.refresh_from_db()
        self.assertFalse(recipe.is_shared)


# ============================================
# COMMENT MODEL TESTS
# ============================================

class RecipeCommentModelTest(TestCase):
    """Test suite for RecipeComment model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.recipe = Recipe.objects.create(
            recipe_id='12345',
            title='Test Recipe',
            is_cached=True
        )

        self.comment = RecipeComment.objects.create(
            recipe=self.recipe,
            user=self.user,
            comment='This is a great recipe!',
            rating=5
        )

    def test_comment_creation(self):
        """Test that a comment is created correctly"""
        self.assertEqual(self.comment.comment, 'This is a great recipe!')
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.recipe, self.recipe)
        self.assertEqual(self.comment.rating, 5)
        self.assertIsNotNone(self.comment.created_at)

    def test_comment_str_method(self):
        """Test the string representation of the comment"""
        expected_str = f"Comment by {self.user.username} on {self.recipe}"
        self.assertEqual(str(self.comment), expected_str)

    def test_comment_without_rating(self):
        """Test creating a comment without a rating"""
        comment = RecipeComment.objects.create(
            recipe=self.recipe,
            user=self.user,
            comment='Good recipe but no rating'
        )
        self.assertIsNone(comment.rating)
        self.assertEqual(comment.comment, 'Good recipe but no rating')

    def test_comment_ordering(self):
        """Test that comments are ordered by created_at descending"""
        comment2 = RecipeComment.objects.create(
            recipe=self.recipe,
            user=self.user,
            comment='Newer comment'
        )
        comments = RecipeComment.objects.all()
        self.assertEqual(comments[0], comment2)  # Newer comment first
        self.assertEqual(comments[1], self.comment)

    def test_comment_cascade_delete_with_recipe(self):
        """Test that comments are deleted when recipe is deleted"""
        comment_id = self.comment.id
        self.recipe.delete()

        with self.assertRaises(RecipeComment.DoesNotExist):
            RecipeComment.objects.get(id=comment_id)

    def test_comment_cascade_delete_with_user(self):
        """Test that comments are deleted when user is deleted"""
        comment_id = self.comment.id
        self.user.delete()

        with self.assertRaises(RecipeComment.DoesNotExist):
            RecipeComment.objects.get(id=comment_id)


# ============================================
# COMMENT VIEW TESTS - CREATE
# ============================================

class CreateCommentViewTest(TestCase):
    """Test suite for creating comments"""

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

    def test_make_comment_authenticated(self):
        """Test creating a comment while authenticated"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('make_comment', args=[12345])

        comment_data = {
            'comment': 'This recipe is amazing!',
            'rating': '5'
        }

        response = self.client.post(url, comment_data)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Verify comment was created
        self.assertEqual(RecipeComment.objects.count(), 1)
        comment = RecipeComment.objects.first()
        self.assertEqual(comment.comment, 'This recipe is amazing!')
        self.assertEqual(comment.rating, 5)
        self.assertEqual(comment.user, self.user)

    def test_make_comment_without_rating(self):
        """Test creating a comment without a rating"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('make_comment', args=[12345])

        comment_data = {
            'comment': 'Good recipe'
        }

        response = self.client.post(url, comment_data)

        self.assertEqual(response.status_code, 302)
        comment = RecipeComment.objects.first()
        self.assertIsNone(comment.rating)

    def test_make_feed_comment_authenticated(self):
        """Test creating a comment from home feed"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('make_feed_comment', args=['12345'])

        comment_data = {
            'comment': 'Great recipe from feed!'
        }

        response = self.client.post(url, comment_data)

        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.url)

        # Verify comment was created
        self.assertEqual(RecipeComment.objects.count(), 1)
        comment = RecipeComment.objects.first()
        self.assertEqual(comment.comment, 'Great recipe from feed!')

    def test_make_feed_comment_unauthenticated(self):
        """Test that unauthenticated users cannot comment"""
        url = reverse('make_feed_comment', args=['12345'])

        comment_data = {
            'comment': 'Should not work'
        }

        response = self.client.post(url, comment_data)

        # Should still redirect but no comment created
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RecipeComment.objects.count(), 0)

    def test_make_feed_comment_empty_text(self):
        """Test that empty comments are not created"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('make_feed_comment', args=['12345'])

        comment_data = {
            'comment': ''
        }

        response = self.client.post(url, comment_data)

        # No comment should be created
        self.assertEqual(RecipeComment.objects.count(), 0)

    def test_make_feed_comment_nonexistent_recipe(self):
        """Test commenting on a recipe that doesn't exist"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('make_feed_comment', args=['99999'])

        comment_data = {
            'comment': 'Comment on missing recipe'
        }

        response = self.client.post(url, comment_data)

        # Should handle gracefully
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RecipeComment.objects.count(), 0)


# ============================================
# COMMENT VIEW TESTS - UPDATE
# ============================================

class UpdateCommentViewTest(TestCase):
    """Test suite for updating comments"""

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

        self.comment = RecipeComment.objects.create(
            recipe=self.recipe,
            user=self.user,
            comment='Original comment text'
        )

    def test_edit_comment_authenticated_owner(self):
        """Test that comment owner can edit their comment"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit_comment', args=[self.comment.id])

        updated_data = {
            'comment': 'Updated comment text'
        }

        response = self.client.post(url, updated_data)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Verify comment was updated
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, 'Updated comment text')

    def test_edit_comment_non_owner(self):
        """Test that non-owners cannot edit comments"""
        self.client.login(username='otheruser', password='testpass123')
        url = reverse('edit_comment', args=[self.comment.id])

        updated_data = {
            'comment': 'Trying to edit someone elses comment'
        }

        response = self.client.post(url, updated_data)

        # Comment should not be updated
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, 'Original comment text')

    def test_edit_comment_unauthenticated(self):
        """Test that unauthenticated users cannot edit"""
        url = reverse('edit_comment', args=[self.comment.id])

        updated_data = {
            'comment': 'Should not work'
        }

        response = self.client.post(url, updated_data)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

        # Comment should not be updated
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, 'Original comment text')

    def test_edit_comment_empty_text(self):
        """Test that comments cannot be updated with empty text"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit_comment', args=[self.comment.id])

        updated_data = {
            'comment': ''
        }

        response = self.client.post(url, updated_data)

        # Comment should not be updated
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, 'Original comment text')

    def test_edit_nonexistent_comment(self):
        """Test editing a comment that doesn't exist"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit_comment', args=[99999])

        updated_data = {
            'comment': 'Updated text'
        }

        response = self.client.post(url, updated_data)

        # Should handle gracefully
        self.assertEqual(response.status_code, 302)


# ============================================
# COMMENT VIEW TESTS - DELETE
# ============================================

class DeleteCommentViewTest(TestCase):
    """Test suite for deleting comments"""

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

        self.comment = RecipeComment.objects.create(
            recipe=self.recipe,
            user=self.user,
            comment='Comment to delete'
        )

    def test_delete_comment_authenticated_owner(self):
        """Test that comment owner can delete their comment"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('delete_comment', args=[self.comment.id])

        # Verify comment exists
        self.assertEqual(RecipeComment.objects.count(), 1)

        response = self.client.post(url)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Verify comment was deleted
        self.assertEqual(RecipeComment.objects.count(), 0)

    def test_delete_comment_non_owner(self):
        """Test that non-owners cannot delete comments"""
        self.client.login(username='otheruser', password='testpass123')
        url = reverse('delete_comment', args=[self.comment.id])

        response = self.client.post(url)

        # Comment should still exist
        self.assertEqual(RecipeComment.objects.count(), 1)

    def test_delete_comment_unauthenticated(self):
        """Test that unauthenticated users cannot delete"""
        url = reverse('delete_comment', args=[self.comment.id])

        response = self.client.post(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

        # Comment should still exist
        self.assertEqual(RecipeComment.objects.count(), 1)

    def test_delete_comment_get_request(self):
        """Test that GET requests do not delete comments"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('delete_comment', args=[self.comment.id])

        response = self.client.get(url)

        # Comment should still exist (only POST deletes)
        self.assertEqual(RecipeComment.objects.count(), 1)

    def test_delete_nonexistent_comment(self):
        """Test deleting a comment that doesn't exist"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('delete_comment', args=[99999])

        response = self.client.post(url)

        # Should handle gracefully
        self.assertEqual(response.status_code, 302)


# ============================================
# COMMENT INTEGRATION TESTS
# ============================================

class CommentIntegrationTest(TestCase):
    """Integration tests for complete comment workflow"""

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

    def test_complete_comment_crud_workflow(self):
        """Test complete Create -> Read -> Update -> Delete comment workflow"""

        # CREATE
        create_url = reverse('make_feed_comment', args=['12345'])
        create_data = {
            'comment': 'Initial comment text'
        }

        create_response = self.client.post(create_url, create_data)
        self.assertEqual(create_response.status_code, 302)

        comment = RecipeComment.objects.first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.comment, 'Initial comment text')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.recipe, self.recipe)

        # UPDATE
        update_url = reverse('edit_comment', args=[comment.id])
        update_data = {
            'comment': 'Updated comment text'
        }

        update_response = self.client.post(update_url, update_data)
        self.assertEqual(update_response.status_code, 302)

        comment.refresh_from_db()
        self.assertEqual(comment.comment, 'Updated comment text')

        # DELETE
        delete_url = reverse('delete_comment', args=[comment.id])
        delete_response = self.client.post(delete_url)
        self.assertEqual(delete_response.status_code, 302)

        self.assertEqual(RecipeComment.objects.count(), 0)

    def test_multiple_users_commenting(self):
        """Test multiple users commenting on the same recipe"""

        # First user comments
        comment1_data = {
            'comment': 'Comment from user 1'
        }
        self.client.post(
            reverse('make_feed_comment', args=['12345']),
            comment1_data
        )

        # Second user comments
        user2 = User.objects.create_user(username='user2', password='pass123')
        self.client.login(username='user2', password='pass123')

        comment2_data = {
            'comment': 'Comment from user 2'
        }
        self.client.post(
            reverse('make_feed_comment', args=['12345']),
            comment2_data
        )

        # Verify both comments exist
        self.assertEqual(RecipeComment.objects.count(), 2)

        comments = RecipeComment.objects.all()
        comment_texts = [c.comment for c in comments]
        self.assertIn('Comment from user 1', comment_texts)
        self.assertIn('Comment from user 2', comment_texts)

        # Verify user2 cannot delete user1's comment
        user1_comment = RecipeComment.objects.get(
            comment='Comment from user 1'
        )
        delete_url = reverse('delete_comment', args=[user1_comment.id])
        self.client.post(delete_url)

        # Both comments should still exist
        self.assertEqual(RecipeComment.objects.count(), 2)
