# Recipe Room Database ERD

## Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ UserRecipe : "saves"
    User ||--o{ CreatedRecipe : "creates"
    User ||--o{ RecipeComment : "writes"
    Recipe ||--o{ UserRecipe : "saved_by"
    Recipe ||--o{ RecipeComment : "has"

    User {
        int id PK "AutoField"
        string username "CharField(150)"
        string email "EmailField"
        string password "CharField(128)"
    }

    Recipe {
        int id PK "AutoField"
        string recipe_id UK "CharField(100) - API ID"
        string title "CharField(255)"
        string image_url "URLField(500)"
        text summary "TextField"
        text instructions "TextField"
        json ingredients "JSONField"
        int ready_in_minutes "IntegerField"
        int servings "IntegerField"
        string source_url "URLField(500)"
        datetime cached_at "DateTimeField(auto_now=True)"
        boolean is_cached "BooleanField"
    }

    UserRecipe {
        int id PK "AutoField"
        int user_id FK "ForeignKey(User, CASCADE)"
        int recipe_id FK "ForeignKey(Recipe, CASCADE)"
        boolean is_shared "BooleanField"
        text message "TextField"
        int rating "PositiveIntegerField(0-5)"
        datetime created_at "DateTimeField(auto_now_add=True)"
        datetime shared_at "DateTimeField"
    }

    CreatedRecipe {
        int id PK "AutoField"
        int creator_id FK "ForeignKey(User, CASCADE)"
        string title "CharField(255)"
        text description "TextField"
        text ingredients "TextField"
        text instructions "TextField"
        int ready_in_minutes "IntegerField(MinValidator=1)"
        int servings "IntegerField(MinValidator=1)"
        string featured_image "CloudinaryField"
        boolean is_shared "BooleanField"
        text shared_message "TextField"
        datetime shared_at "DateTimeField"
        datetime created_at "DateTimeField(auto_now_add=True)"
        datetime updated_at "DateTimeField(auto_now=True)"
    }

    RecipeComment {
        int id PK "AutoField"
        int recipe_id FK "ForeignKey(Recipe, CASCADE)"
        int user_id FK "ForeignKey(User, CASCADE)"
        text comment "TextField"
        int rating "PositiveIntegerField(0-5)"
        datetime created_at "DateTimeField(auto_now_add=True)"
    }
```

## Relationships

### User (Django Auth)
- **One-to-Many** with UserRecipe: A user can save multiple API recipes
- **One-to-Many** with CreatedRecipe: A user can create multiple recipes
- **One-to-Many** with RecipeComment: A user can write multiple comments

### Recipe (API Cache)
- **One-to-Many** with UserRecipe: A recipe can be saved by multiple users
- **One-to-Many** with RecipeComment: A recipe can have multiple comments
- **Unique Constraint**: `recipe_id` (Spoonacular API identifier)

### UserRecipe (Junction Table)
- **Many-to-One** with User: Links to the user who saved the recipe
- **Many-to-One** with Recipe: Links to the saved recipe
- **Unique Together**: (user, recipe) - Prevents duplicate saves
- **Cascade Delete**: Deletes when User or Recipe is deleted

### CreatedRecipe (User-Created)
- **Many-to-One** with User (creator): Links to the recipe author
- **Cascade Delete**: Deletes when creator User is deleted
- **Independent**: Not related to API Recipe model

### RecipeComment
- **Many-to-One** with User: Links to comment author
- **Many-to-One** with Recipe: Links to the commented recipe
- **Cascade Delete**: Deletes when User or Recipe is deleted

## Key Features

- **Rating System**: UserRecipe and RecipeComment support 0-5 star ratings
- **Sharing Mechanism**: Both UserRecipe and CreatedRecipe can be shared to community feed
- **API Caching**: Recipe model caches Spoonacular API data to reduce API calls
- **Image Storage**: CreatedRecipe uses Cloudinary for user-uploaded images
- **Validation**: MinValueValidator and MaxValueValidator for ratings, servings, and time
