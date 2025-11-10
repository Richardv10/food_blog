
# Recipe Room

<img src="static/images/README/hero.png" alt="Three weeks of my life" width="600">

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Agile Development](#agile-development)
- [Github Projects Board](#github-projects-board)
- [Core Functionality](#core-functionality)
- [UX Design](#ux-design)
- [Wireframes](#wireframes)
- [Database ERD](#database-erd)
- [Technologies and Packages Used](#technologies-and-packages-used)
- [Screenshots](#screenshots)
- [Testing, Performance and Validation](#testing-performance-and-validation)
- [HTML Validation Testing](#html-validation-testing)
- [Python Validation](#python-validation)
- [Lighthouse Testing](#lighthouse-testing)
- [Browser Compatibility](#browser-compatibility)
- [AI Tools](#ai-tools)
- [Cloud Deployment](#cloud-deployment)
- [Limitations and Further Development](#limitations-and-further-development)
- [Credits](#credits)

## Deployed site [here] (https://recipe-room-b877ae9a2298.herokuapp.com/)


## Description 

A food blogging site where users can create, search, and share recipes.

## Features

1. Secure user accounts with individual CRUD functionality.
2. Spoonacular API integration for searching recipes, including a random search tool, and
  options to refine or exclude results.
3. Logged-in users have a persistent saved "My Recipes" section (with recipe caching to
  reduce API calls).
4. Users can create and share recipes (users' images are stored separately with
  Cloudinary).
5. Featured Recipes section that changes on every visit.
6. Responsive mobile first design.


# Agile Development



## User stories and Acceptance criteria 



## (Feature 1) 
### As a regular user I would like to be able to create recipes and store them on my
user profile (Could have)
- Use cloud storage, key/value pairs, or an API ID to record favorites


## (Features 2 & 5)
### As a casual visitor, I want to browse a variety of recipes so that I can discover
new dishes easily. (Must have)
- API returns a list of recipes with title, image, description, and tags, and is
  searchable
- Recipes are displayed in a grid or list format
- If the API fails, exception handling and caching still provide usable
  functionality


## (Feature 3)
### As a user, I want to like recipes, so that I can save my favorites and influence future recommendations.(Should have)
-Each recipe has a visible "like" button.
-Liked recipes are stored in the user’s profile.
-Users can unlike recipes to remove them from favorites.


## (Feature 4)
### As a regular user I want to connect with others and share my love of food (Must have)
-Social feed where users can comment and share recipes
-User can modify, delete or post their own comments
-Users can't delete each others comments

## (Feature 6)
### As a mobile user without access to a PC, I would like the site to be fully usable
on mobiles and tablets (Must have)
- Full site functionality preserved through use of media queries and Bootstrap


## (Feature 2)
### As a vegetarian user, I want to filter out meat-based recipes, so that I only see dishes I can eat. (Could have)
-Filter options include dietary tags (e.g., vegetarian, vegan, gluten-free).
~~Recipes with excluded ingredients are hidden from personalized feed~~
-Settings persist across sessions.



# Github projects board


<img src="static/images/README/github.png" alt="Github user stories" width="600">


The GitHub Projects board was used for scoping and planning using MoSCoW labels for
feature prioritization. As sections evolved, I reviewed them weekly and adjusted when
necessary.







# Core functionality

The Recipe Room is a food blogging site linked to the Spoonacular API for integrated
search/share functionality. Users can create an account, search for recipes, or create
their own. Both are stored in a user's library. When recipes are viewed, they are
cached in the database for local retrieval. Users can comment on recipes, delete,
and update their own comments. Because comments are stored locally they link to
recipes in the database via a foreign key and are visible to all users.

### Spoonacular API Integration

The concept of the site is to provide a resource to search curated recipes, share,
and comment. For this purpose I utilized an API that has over 50,000 recipes. The
API exposes several endpoints, which I use through Spoonaculars "recipe_id",
"recipe_detail", and "random" URLs to fulfill different functions of the site. Near
submission I took advantage of a student offer through RapidAPI to provide higher
usage limits to mirror real-world functionality for a recipe blog.


### Cloudinary API Integration

Due to the use of eco dynos on Heroku, persistent data storage requires the use
of a cloud image host; I utilized Cloudinary for this purpose. As API recipes include
an image URL, this can be saved in the database when a recipe is viewed and then
reused, avoiding the need to store API recipe images locally. For user-created
recipes, users can upload images which are stored via Cloudinary fields in the
database.



# UX Design

As the project scope is to deliver a shared community resource, I chose a social
feed format with infinite scroll. The landing zone of the site changes for
returning users, replacing the welcome banner with the user's recipe library. This
was intended to provide users with an easy-to-navigate experience. Because the site
may be used by people actively cooking, the functions are designed to be as
accessible as possible with as few clicks or touches as necessary. To this end I
separated the search function into another app and paginated results to create a
distinction between recipe creation/discovery and the social feed/library used for
reference. Navigation is achieved via simple links on the navbar and jump buttons
nested in content.


### Color Scheme and design language

After conducting research on various food blogs, the design consensus seemed to be
light and airy with lots of pastels. I opted for a green theme and included
translucent elements to frame recipes for readability. I chose a simple image
background that would not interfere with the displayed content and that gives a
clean look.


### Primary Colors

| Color Name | Hex Code | RGB | Preview | Usage |
|------------|----------|-----|---------|-------|
| **Primary Color** | `#7bb560` | `rgb(123, 181, 96)` | <div style="background-color: #7bb560; width: 60px; height: 25px; border: 1px solid #ccc; border-radius: 4px;"></div> | Main brand color, buttons, links |
| **Secondary Color** | `#9fc93b` | `rgb(159, 201, 59)` | <div style="background-color: #9fc93b; width: 60px; height: 25px; border: 1px solid #ccc; border-radius: 4px;"></div> | Secondary buttons, accents |
| **Accent Color** | `#f2e8cf` | `rgb(242, 232, 207)` | <div style="background-color: #f2e8cf; width: 60px; height: 25px; border: 1px solid #ccc; border-radius: 4px;"></div> | Highlights, decorative elements |
| **Success Color** | `#479124` | `rgb(71, 145, 36)` | <div style="background-color: #479124; width: 60px; height: 25px; border: 1px solid #ccc; border-radius: 4px;"></div> | Success messages, positive actions |
| **Danger Color** | `#e76f51` | `rgb(231, 111, 81)` | <div style="background-color: #e76f51; width: 60px; height: 25px; border: 1px solid #ccc; border-radius: 4px;"></div> | Error messages, delete buttons |
| **Warning Color** | `#9ab58e` | `rgb(154, 181, 142)` | <div style="background-color: #9ab58e; width: 60px; height: 25px; border: 1px solid #ccc; border-radius: 4px;"></div> | Navigation bar, footer background |
| **Info Color** | `#264653` | `rgb(38, 70, 83)` | <div style="background-color: #264653; width: 60px; height: 25px; border: 1px solid #ccc; border-radius: 4px;"></div> | Headings, informational text |
| **Card Background** | `#fef9f0` | `rgb(254, 249, 240)` | <div style="background-color: #fef9f0; width: 60px; height: 25px; border: 1px solid #ccc; border-radius: 4px;"></div> | Recipe cards, content blocks |




# Wireframes

### Wireframe 1 - Home Page / Landing
<img src="static/images/README/1.png" alt="Wireframe 1 - Home Page" width="600">

*Initial homepage design showing the main landing zone and navigation structure*

### Wireframe 2 - Logged In User
<img src="static/images/README/2.png" alt="Wireframe 2 - Logged in" width="600">

*Logged in landing page*

### Wireframe 3 - Recipe Search
<img src="static/images/README/3.png" alt="Wireframe 3 - Recipe Search" width="600">

*Recipe Search Function*

### Wireframe 4 - Recipe detail
<img src="static/images/README/4.png" alt="Wireframe 4 - User Dashboard" width="600">

*User's recipe (unified display)*

### Wireframe 5 - Recipe Creation Form
<img src="static/images/README/5.png" alt="Wireframe 5 - Create Recipe" width="600">

*Form interface for users to create and submit their own recipes*

### Wireframe 6 - Mobile Design
<img src="static/images/README/6.png" alt="Wireframe 6 - Community Feed" width="400" height="700">

*As the site is "feed based" mobile friendly design requires minimal rearrangement*

-----------

# Database ERD

<img src="static/images/README/ERD.png" alt="ERD" width="1000">

## Extension during development

The CreatedRecipe model was added after achieving MVP, (to extend the functionality of the project). It solely interacts with the User model, and didn't alter any existing Model recipe relationships. I chose not to add rating functionality to the created recipes, as this would have significantly increased the complexity of the schema. 


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





# Technologies and Packages Used

## Backend
- **Django 4.2.25** - Python web framework
- **PostgreSQL** (psycopg2 2.9.11) - Database
- **Gunicorn 23.0.0** - Production WSGI server

## Authentication & Security
- **Django Allauth 0.57.2** - User authentication and account management
- **Bleach 6.2.0** - HTML sanitization for XSS protection

## Cloud Services & APIs
- **Cloudinary 1.36.0** - Image storage and management
- **Spoonacular API** - Recipe data integration
- **Heroku** - Cloud Hosting provider

## Static Files & Deployment
- **WhiteNoise 6.11.0** - Static file serving
- **dj-database-url 3.0.1** - Database configuration

## Frontend
- **HTML/CSS** - Structure and styling
- **JavaScript** - Interactive features
- **Bootstrap 5** - Responsive design framework

# Screenshots

## Landing Page

<img src="static/images/README/welcome.png" alt="Welcome Section" width="600">

*Landing page for Recipe Room.* Rather than clutter the space with food pictures,
simple headings and a short paragraph describe the site's features. Two buttons
prompt users to join and to go to the search function, which is available to all
users.

<img src="static/images/README/landingzone.png" alt="Landing Zone" width="600">

*Logged-in user landing page.* When a user is logged in, the generic welcome
screen is replaced with a personalized greeting and a tabbed menu showing all of
the user's saved recipes. These have buttons and indicators for sharing and
updating shared recipes.


## User Authentication
<img src="static/images/README/notloggedin.png" alt="Not Logged In View" width="400">

*Default view for visitors who are not logged in*

<img src="static/images/README/login.png" alt="Login Page" width="400">

*Secure login interface for registered users*

<img src="static/images/README/signup.png" alt="Sign Up Page" width="400">

*Registration page for new users to create an account*

<img src="static/images/README/loggedin.png" alt="Logged In View" width="400">

*Authenticated user view with full access to features*

## User Dashboard
<img src="static/images/README/userlandingzone.png" alt="User Landing Zone" width="600">

*Personalized dashboard for logged-in users with saved recipes*

## Recipe Search
<img src="static/images/README/search.png" alt="Search Functionality" width="600">

*Advanced search interface with suggestions and dietary preferences*

## Recipe Display
<img src="static/images/README/APIrecipe.png" alt="API Recipe" width="600">

*Recipe detail page showing API-fetched recipe with full information*

<img src="static/images/README/userrecipe.png" alt="User Created Recipe" width="600">

*User-created recipe detail view with custom content*

## Recipe Creation
<img src="static/images/README/createrecipe.png" alt="Create Recipe" width="600">

*Intuitive recipe creation form for users to share their own recipes*

## Community Features
<img src="static/images/README/feed.png" alt="Community Feed" width="600">

*Social feed where users share and discover recipes from the community*

<img src="static/images/README/comment.png" alt="Comments Section" width="600">

*Comment functionality for community engagement*

<img src="static/images/README/commentloggedin.png" alt="Logged In Comments" width="600">

*Enhanced comment features for authenticated users (edit/delete)*

## Responsive Design
<img src="static/images/README/mobile.png" alt="Mobile View" width="400">

*Fully responsive mobile interface*

<img src="static/images/README/tablet.png" alt="Tablet View" width="400">

*Optimized tablet display ensuring great UX across all devices*



# Testing, Performance and Validation

## Test Summary

**Date**: November 6, 2025  
**Total Tests Run**: 85  
**Passed**: 85 ✅  
**Failed**: 0 ❌  
**Success Rate**: 100%  
**Execution Time**: ~160 seconds

---

## Test Coverage Overview

Comprehensive CRUD (Create, Read, Update, Delete) testing across all four models: API Recipe caching, User-Recipe relationships (save/share), User-Created Recipes, and Comments. Tests schema saved in "tests.py"

### Blog App Tests (52 tests)
- **Model Tests** (11 tests) - CreatedRecipe and RecipeComment models ✅
- **Create Views** (12 tests) - Recipe and comment creation ✅
- **Read Views** (5 tests) - Recipe viewing permissions ✅
- **Update Views** (10 tests) - Recipe and comment editing ✅
- **Delete Views** (9 tests) - Recipe and comment deletion ✅
- **Share/Unshare** (3 tests) - Community feed functionality ✅
- **Integration Tests** (4 tests) - Complete CRUD workflows ✅

### Recipe App Tests (33 tests)
- **Model Tests** (17 tests) - Recipe and UserRecipe models ✅
- **Save/Delete Views** (6 tests) - Library management ✅
- **Share/Unshare Views** (6 tests) - Feed management ✅
- **My Recipes View** (2 tests) - Dashboard functionality ✅
- **Integration Tests** (2 tests) - Complete workflows ✅

---

## Key Features Tested

### ✅ API Recipe Features (Recipe Model)
- Recipe caching from Spoonacular API
- JSON field storage for ingredients
- Unique recipe ID enforcement
- Auto-updating timestamps

### ✅ User Recipe Library (UserRecipe Model)
- Saving/deleting API recipes
- Sharing/unsharing to community feed
- Rating recipes (0-5 validation)
- Adding messages to shared recipes
- Authentication and permissions
- Multi-user interactions

### ✅ User-Created Recipes (CreatedRecipe Model)
- Recipe creation with full and minimal data
- Recipe updates (complete and partial)
- Recipe deletion
- Owner permissions enforcement
- Public vs. private recipe access
- Sharing to community feed

### ✅ Comment System (RecipeComment Model)
- Comment creation and editing
- Comment deletion
- Permission enforcement (owners only)
- Cascade deletion with recipes/users
- Multi-user interactions
- Authentication requirements

---

## Test Environment

- **Framework**: Django TestCase
- **Database**: PostgreSQL (Neon serverless test instance)
- **Python**: 3.x
- **Django**: 4.x

---

## Test Conclusion

All 85 tests passed successfully, validating complete CRUD functionality across all models with proper authentication, permissions, and error handling.

---
# HTML Validation Testing


<table>
  <thead>
    <tr>
      <th>Page</th>
      <th>Screenshot</th>
      <th>Result</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Home Page</td>
      <td><img src="static/images/README/validation_images/homepage.png" alt="Home Page Validation" width="400"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Login Page</td>
      <td><img src="static/images/README/validation_images/loginpage.png" alt="Login Page Validation" width="400"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Logout Page</td>
      <td><img src="static/images/README/validation_images/logout.png" alt="Logout Page Validation" width="400"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Sign Up Page</td>
      <td><img src="static/images/README/validation_images/signuppage.png" alt="Sign Up Page Validation" width="400"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Search Page</td>
      <td><img src="static/images/README/validation_images/searchpage.png" alt="Search Page Validation" width="400"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Recipe Page</td>
      <td><img src="static/images/README/validation_images/recipepage.png" alt="Recipe Page Validation" width="400"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Created Recipe Page</td>
      <td><img src="static/images/README/validation_images/createdpage.png" alt="Created Recipe Page Validation" width="400"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Random Recipe</td>
      <td><img src="static/images/README/validation_images/random.png" alt="Random Recipe Validation" width="400"></td>
      <td>✅ Pass</td>
    </tr>
  </tbody>
</table>

# Python Validation

<table>
  <thead>
    <tr>
      <th>File</th>
      <th>Screenshot</th>
      <th>Result</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>blog/admin.py</td>
      <td><img src="static/images/README/pylint/blog_admin.png" alt="blog admin validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>blog/models.py</td>
      <td><img src="static/images/README/pylint/blog_models.png" alt="blog models validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>blog/urls.py</td>
      <td><img src="static/images/README/pylint/blog_urls.png" alt="blog urls validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>blog/views.py</td>
      <td><img src="static/images/README/pylint/blog_views.png" alt="blog views validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>recipe/admin.py</td>
      <td><img src="static/images/README/pylint/recipe_admin.png" alt="recipe admin validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>recipe/models.py</td>
      <td><img src="static/images/README/pylint/recipe_models.png" alt="recipe models validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>recipe/urls.py</td>
      <td><img src="static/images/README/pylint/recipe_urls.png" alt="recipe urls validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>recipe/views.py</td>
      <td><img src="static/images/README/pylint/recipe_views.png" alt="recipe views validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>food_blog/urls.py</td>
      <td><img src="static/images/README/pylint/foodblog_urls.png" alt="food_blog urls validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>food_blog/settings.py</td>
      <td><img src="static/images/README/pylint/settings.png" alt="settings validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>admin.py</td>
      <td><img src="static/images/README/pylint/admin_py.png" alt="admin.py validation"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>blog/tests.py</td>
      <td><img src="static/images/README/pylint/test.png" alt="tests validation"></td>
      <td>✅ Pass</td>
    </tr>
  </tbody>
</table>

# Lighthouse testing

<table>
  <thead>
    <tr>
      <th>Page</th>
      <th>Screenshot</th>
      <th>Result</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Home Page</td>
      <td><img src="static/images/README/lighthouse/homepage.png" alt="Home Page Lighthouse"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Login Page</td>
      <td><img src="static/images/README/lighthouse/login.png" alt="Login Page Lighthouse"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Sign Up Page</td>
      <td><img src="static/images/README/lighthouse/signup.png" alt="Sign Up Page Lighthouse"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Search Page</td>
      <td><img src="static/images/README/lighthouse/search.png" alt="Search Page Lighthouse"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Recipe Detail Page</td>
      <td><img src="static/images/README/lighthouse/recipedetail.png" alt="Recipe Detail Page Lighthouse"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Mobile View</td>
      <td><img src="static/images/README/lighthouse/mobile.png" alt="Mobile View Lighthouse"></td>
      <td>✅ Pass</td>
    </tr>
  </tbody>
</table>

# Browser compatibility

<table>
  <thead>
    <tr>
      <th>Browser</th>
      <th>Screenshot</th>
      <th>Result</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Chrome 131</td>
      <td><img src="static/images/README/browser/chrome.png" alt="Chrome Browser Compatibility"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Edge 131</td>
      <td><img src="static/images/README/browser/edge.png" alt="Edge Browser Compatibility"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Firefox 132</td>
      <td><img src="static/images/README/browser/firefox.png" alt="Firefox Browser Compatibility"></td>
      <td>✅ Pass</td>
    </tr>
    <tr>
      <td>Safari 18.1</td>
      <td><img src="static/images/README/browser/Safari.png" alt="Safari Browser Compatibility"></td>
      <td>✅ Pass</td>
    </tr>
  </tbody>
</table>


# Ai Tools

## Code Creation
I utilized Claude Sonnet 4.5 to assist in code production through VS Code Co-pilot. Early
in development, frequent API calls made me aware of the need for a caching system.
I used Co-pilot to help implement caching in my existing schema and to assist in the
creation of large sections of Django template code on the site's frontend, which
would otherwise have taken much longer.

## Debugging
Co-pilot helped specifically through logical problem solving and by explaining how to
achieve given objectives. I frequently asked Co-pilot to identify errors regarding
Django-specific functions and behaviours I wasn't familiar with. File structure
issues and Cloudinary-specific parameters were common questions, and Co-pilot has
been invaluable while learning a large framework.

## Optimization 
I've used Co-pilot to refactor sections of code I thought could be improved or to ask
for alternative ways to achieve objectives. Co-pilot was used extensively to adjust
Bootstrap classes and tweak things in bulk or to reorganize the CSS file as it grew.
Early in development I tried several different approaches to implementing models,
data retrieval methods, and schema. Co-pilot allowed rapid prototyping and resulted
in a more refined product through iterative development.

## Co-pilot unit tests
I used Co-pilot to construct a test suite covering all CRUD operations across all
models using a test database. These are detailed separately.


# Cloud Deployment

The project is deployed to Heroku and can be found [here](https://recipe-room-b877ae9a2298.herokuapp.com/).

## Set-up Heroku

- After setting up an account

- Create new app from the dropdown menu.
- In deployment -> Connect Github Repository to heroku
- In settings -> Reveal Config Vars, and set environment variables.

- CLOUDINARY_URL: Obtained from Cloudinary
- DATABASE_URL: Obtained from Code Institute	
- DISABLE_COLLECTSTATIC: (this is temporary, and can be removed for the final deployment)
- SECRET_KEY:	Obtained from Django
- SPOONACULAR_URL: Obtained from Spoonacular (I have switched to "RapidAPI_URL" for deployment to use their student offer)

 Debug value must be set to "False" in settings.py for deployment to Heroku

### Heroku needs two additional deployment files

- requirements.txt (list of installed packages)
- Procfile

### Install this project's requirements

pip3 install -r requirements.txt

- If requirements file needs updated using:

pip3 freeze --local > requirements.txt

- Procfile can be created with the following:

echo web: gunicorn FOOD_BLOG.wsgi > Procfile


### Set-up Cloudinary

- Set up free account with Cloudinary 
- Copy the cloudinary URL to Heroku CONFIG VARS
- Set cloudinary to use HTTPS through settings.py 

### Set-up Spoonacular

- Create a free account with Spoonacular
- Copy the API key from the user area to Heroku CONFIG VARS (For this project I have used Rapid API's student offer)

### Initialization

- Under the deploy tab, find "deploy from main branch"

### Verification of deployment

- To compare functionality, run a development server from "localhost" in the VS code terminal. The result should be the same. If not enable Debug in settings.py for the local deployment.





# Limitations and Further Development

- Search function requires user to modify search parameters using language like "exclude" and "include". I would add a complex search section using filters. This relates to the "As a vegetarian" user story (that has a strike-through), I wanted to add the related functionality via a filter, but this was a "could have", and did not have time.

- Rating system does not aggregate, no system to search recipes "rated by others". This would require significant changes to the models, and was beyond project scope.

- The user section is just a recipe library, further development I would flesh this out to be a full user profile, that tracks recent comments, interactions, and posts. 

- When a user views a recipe, this is cached in the database. This data would be useful for metrics. As given enough usage, users preferences and likes could be recorded, this would allow the "featured recipes" section to be user specific. 



# Credits 

- Background image: "http://www.unsplash.com"
- Django for everybody course - Free code camp: https://www.youtube.com/watch?v=o0XbHvKxw7Y&t=32320s
- CodeAcademy (various resources)
- Thanks to Crystal at Spoonacular for providing me student access.
- Thanks to Mark, Lewis and Tom and everyone at Code Institute for their help and support.


