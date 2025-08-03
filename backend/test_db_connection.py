#!/usr/bin/env python3
"""
Database connection test script for TAIFA-FIALA
Tests Supabase connection and database tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_supabase
from config.settings import settings

def test_supabase_connection():
    """Test Supabase client connection"""
    print("\n🔍 Testing Supabase connection...")
    try:
        supabase = get_supabase()
        # Test with a simple query to a system table
        response = supabase.table('innovations').select('id').limit(1).execute()
        print("✅ Supabase connection successful!")
        print(f"   Response status: {len(response.data) if response.data else 0} records found")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_database_tables():
    """Test if main tables exist using Supabase"""
    print("\n🔍 Testing database tables...")
    try:
        supabase = get_supabase()
        # Check if main tables exist
        tables_to_check = ['innovations', 'organizations', 'individuals', 'fundings']
        for table in tables_to_check:
            try:
                response = supabase.table(table).select('id').limit(1).execute()
                count = len(response.data) if response.data else 0
                print(f"   ✅ Table '{table}': accessible (sample: {count} record)")
            except Exception as e:
                print(f"   ❌ Table '{table}': {e}")
        return True
    except Exception as e:
        print(f"❌ Database tables test failed: {e}")
        return False

def main():
    """Run all database tests"""
    print("🚀 TAIFA-FIALA Supabase Connection Test")
    print("=" * 50)
    
    print(f"Supabase URL: {settings.NEXT_PUBLIC_SUPABASE_URL}")
    print()
    
    # Run tests
    supabase_ok = test_supabase_connection()
    tables_ok = test_database_tables() if supabase_ok else False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Supabase:   {'✅ PASS' if supabase_ok else '❌ FAIL'}")
    print(f"   Tables:     {'✅ PASS' if tables_ok else '❌ FAIL'}")
    
    if supabase_ok and tables_ok:
        print("\n🎉 Supabase connection is working!")
        return 0
    else:
        print("\n⚠️  Supabase connection has issues.")
        return 1

if __name__ == "__main__":
    exit(main())
