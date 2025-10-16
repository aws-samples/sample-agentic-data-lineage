#!/usr/bin/env python3
"""
Test Redshift Direct Connection
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_redshift_direct_connection():
    """Test direct connection to Redshift"""
    print("🔗 Testing Redshift direct connection...")

    try:
        from utils.redshift_connector import RedshiftConnector

        connector = RedshiftConnector()

        # Test connection
        print("Establishing direct connection...")
        result = connector.test_connection()

        print(f"Connection status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Connection type: {result['connection_type']}")

        if result["status"] == "success":
            print("\n✅ Direct connection successful!")

            # Test query
            print("Testing database query...")
            schemas = connector.get_schemas()
            print(f"Retrieved {len(schemas)} schemas")

            for schema in schemas:
                print(f"  - {schema['schemaname']}: {schema['table_count']} tables")

            return True

        elif result["status"] == "warning":
            print("\n⚠️ Using mock data (incomplete configuration)")
            return False

        else:
            print(f"\n❌ Connection failed: {result['message']}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("🚀 Redshift Direct Connection Test")
    print("=" * 50)

    success = test_redshift_direct_connection()

    print("\n" + "=" * 50)
    if success:
        print("✅ Direct connection test successful!")
        print("💡 Redshift can be accessed directly")
    else:
        print("❌ Direct connection test failed!")
        print("💡 Please check configuration or network connection")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
