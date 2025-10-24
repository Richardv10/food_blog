import os
import django
import json
from datetime import datetime, date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_blog.settings')
django.setup()

from django.apps import apps
from django.db import models

def serialize_value(value):
    """Convert non-serializable values to JSON-compatible format"""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        return list(value)
    return value

def export_database():
    """Export all models from all apps to JSON"""
    data = {
        "export_date": datetime.now().isoformat(),
        "database": {}
    }
    
    total_records = 0
    
    # Get all installed apps
    for app_config in apps.get_app_configs():
        app_label = app_config.label
        
        # Skip Django's built-in apps if you want
        # if app_label in ['admin', 'auth', 'contenttypes', 'sessions']:
        #     continue
        
        app_data = {}
        
        # Get all models in this app
        for model in app_config.get_models():
            model_name = model.__name__
            print(f"Exporting {app_label}.{model_name}...")
            
            model_records = []
            
            # Get all instances of this model
            for instance in model.objects.all():
                record = {}
                
                # Get all fields
                for field in instance._meta.get_fields():
                    field_name = field.name
                    
                    try:
                        # Skip reverse relations
                        if isinstance(field, models.ManyToOneRel):
                            continue
                        if isinstance(field, models.ManyToManyRel):
                            continue
                        
                        # Get field value
                        value = getattr(instance, field_name, None)
                        
                        # Handle ForeignKey - get the ID and string representation
                        if isinstance(field, models.ForeignKey):
                            if value:
                                record[field_name + "_id"] = value.pk
                                record[field_name + "_str"] = str(value)
                            else:
                                record[field_name + "_id"] = None
                                record[field_name + "_str"] = None
                        
                        # Handle ManyToMany
                        elif isinstance(field, models.ManyToManyField):
                            if value:
                                record[field_name + "_ids"] = [obj.pk for obj in value.all()]
                                record[field_name + "_strs"] = [str(obj) for obj in value.all()]
                            else:
                                record[field_name + "_ids"] = []
                                record[field_name + "_strs"] = []
                        
                        # Regular fields
                        else:
                            record[field_name] = serialize_value(value)
                    
                    except Exception as e:
                        record[field_name] = f"<Error: {str(e)}>"
                
                model_records.append(record)
                total_records += 1
            
            if model_records:  # Only add if there's data
                app_data[model_name] = model_records
        
        if app_data:  # Only add app if it has data
            data["database"][app_label] = app_data
    
    # Write to JSON file
    output_file = f"database_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Database exported successfully!")
    print(f"📁 File: {output_file}")
    print(f"\nSummary:")
    print(f"  - Total apps exported: {len(data['database'])}")
    print(f"  - Total records: {total_records}")
    print(f"\nApps:")
    for app_name, models_data in data['database'].items():
        print(f"  - {app_name}: {sum(len(records) for records in models_data.values())} records")
        for model_name, records in models_data.items():
            print(f"    • {model_name}: {len(records)}")

if __name__ == "__main__":
    export_database()
