import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_blog.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname='public' AND tablename LIKE 'recipe_%'
        ORDER BY tablename
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
print("Existing recipe tables:")
for table in tables:
    print(f"  - {table}")

print("\nExpected tables:")
print("  - recipe_recipe")
print("  - recipe_userrecipe")
print("  - recipe_recipecomment")
