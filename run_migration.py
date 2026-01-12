#!/usr/bin/env python3
"""
Run database migration using Supabase REST API
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client

def run_migration():
    """Execute the migration SQL via Supabase"""
    
    # Load environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = (os.getenv("SUPABASE_KEY") or 
                    os.getenv("SUPABASE_SERVICE_KEY") or 
                    os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)
    
    print(f"🔗 Connecting to Supabase project...")
    print(f"   URL: {supabase_url}")
    
    # Read migration SQL
    migration_file = Path(__file__).parent / "migrations" / "001_create_tables.sql"
    if not migration_file.exists():
        print(f"❌ Error: Migration file not found: {migration_file}")
        sys.exit(1)
    
    sql = migration_file.read_text()
    print(f"📄 Loaded migration: {migration_file.name}")
    
    # Create Supabase client
    client = create_client(supabase_url, supabase_key)
    
    # Execute SQL using Supabase's RPC
    # Note: We need to use the PostgREST API directly
    print("\n🚀 Executing migration SQL...")
    print("=" * 60)
    
    try:
        # Use the underlying postgrest client to execute raw SQL
        # This requires the query parameter to be sent to the /rpc/query endpoint
        response = client.postgrest.rpc("query", {"query": sql}).execute()
        
        print("\n✅ Migration completed successfully!")
        print(response.data)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print("\nℹ️  This is expected - Supabase REST API doesn't support direct SQL execution.")
        print("    Please run the migration manually in the Supabase Dashboard:")
        print(f"    https://supabase.com/dashboard/project/burikoetldvkvporqnno/sql/new")
        print(f"\n    Copy the contents of: {migration_file}")
        sys.exit(1)

if __name__ == "__main__":
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    run_migration()
