"""
Fix action_items table - add created_by and handle assigned_by
"""
from app.database.database import engine
from sqlalchemy import text

def fix_action_items_schema():
    """Fix action_items table schema"""
    with engine.connect() as conn:
        # Check for assigned_by (old column)
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='action_items' AND column_name='assigned_by';
        """))
        
        if result.fetchone():
            print("⚠️ Found old 'assigned_by' column. Renaming to 'created_by'...")
            
            # Check if created_by already exists
            result2 = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='action_items' AND column_name='created_by';
            """))
            
            if result2.fetchone():
                print("   created_by already exists. Dropping assigned_by...")
                conn.execute(text("ALTER TABLE action_items DROP COLUMN assigned_by;"))
            else:
                print("   Renaming assigned_by to created_by...")
                conn.execute(text("ALTER TABLE action_items RENAME COLUMN assigned_by TO created_by;"))
            
            conn.commit()
            print("✅ Schema updated")
        else:
            print("✅ No assigned_by column found")
        
        # Check for created_by
        result3 = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='action_items' AND column_name='created_by';
        """))
        
        if result3.fetchone():
            print("✅ created_by column exists")
        else:
            print("⚠️ Adding created_by column...")
            conn.execute(text("""
                ALTER TABLE action_items 
                ADD COLUMN created_by INTEGER REFERENCES users(id);
            """))
            conn.commit()
            print("✅ Added created_by column")
        
        # Show all columns
        result4 = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='action_items'
            ORDER BY ordinal_position;
        """))
        
        print("\nCurrent action_items columns:")
        for row in result4:
            print(f"  - {row[0]}")

if __name__ == "__main__":
    fix_action_items_schema()
