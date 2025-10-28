#!/usr/bin/env python3
"""
Quick Database Clear Script
Simple script to clear all data with minimal prompts
"""

from sqlalchemy import text
from app.database.database import engine

def quick_clear():
    """Quickly clear all data from database"""
    
    print("🗑️  Quick Database Clear")
    print("=" * 30)
    
    # Tables in dependency order
    tables = [
        'discussion_messages', 'discussion_topics', 'vote_allocations', 'voting_sessions',
        'theme_groups', 'retrospective_responses', 'chat_messages', 'chat_sessions',
        'retrospective_participants', 'retrospectives', 'action_items',
        'workspace_invitations', 'workspace_members', 'workspaces',
        'email_verification_tokens', 'user_onboarding', 'users'
    ]
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                total_cleared = 0
                
                for table in tables:
                    try:
                        result = conn.execute(text(f"DELETE FROM {table};"))
                        print(f"✅ Cleared {table}")
                        total_cleared += result.rowcount
                    except Exception as e:
                        print(f"⚠️  {table}: {e}")
                
                # Reset sequences
                sequences = [
                    'users_id_seq', 'workspaces_id_seq', 'retrospectives_id_seq',
                    'action_items_id_seq', 'chat_sessions_id_seq', 'chat_messages_id_seq'
                ]
                
                for seq in sequences:
                    try:
                        conn.execute(text(f"SELECT setval('{seq}', 1, false);"))
                    except:
                        pass  # Ignore if sequence doesn't exist
                
                trans.commit()
                print(f"\n🎉 Cleared {total_cleared} total records")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    quick_clear()
