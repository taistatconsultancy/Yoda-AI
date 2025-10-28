"""Check database schema"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database.database import engine
from sqlalchemy import inspect, text

print("=" * 80)
print("Checking Neon Database Schema")
print("=" * 80)

inspector = inspect(engine)

# Check users table
print("\n📋 Users Table Columns:")
try:
    columns = inspector.get_columns('users')
    for col in columns:
        print(f"  ✓ {col['name']}: {col['type']}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Check what columns exist in the database
print("\n📋 All Tables:")
for table_name in inspector.get_table_names():
    print(f"\nTable: {table_name}")
    columns = inspector.get_columns(table_name)
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")

# Check the database_schema_complete.sql for expected columns
print("\n" + "=" * 80)
print("Checking if database schema matches model expectations...")

# Read the User model expected columns
from app.models.user import User
print("\nExpected columns from User model:")
for attr_name in dir(User):
    if not attr_name.startswith('_'):
        attr = getattr(User, attr_name)
        if hasattr(attr, 'property') and hasattr(attr.property, 'columns'):
            for col in attr.property.columns:
                print(f"  ✓ {col.name}: {col.type}")

print("\n" + "=" * 80)
