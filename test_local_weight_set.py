#!/usr/bin/env python3

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_local_weight_set():
    print("Testing local.add_weights_set function...")
    
    try:
        # Import the local module
        import local
        print("✓ Local module imported successfully")
        
        # Create a simple user object
        class UserObject:
            def __init__(self, user_id):
                self.id = user_id
        
        user = UserObject(1)  # Use user ID 1 (the admin user)
        print(f"✓ Created user object with ID: {user.id}")
        
        # Test data
        name = "Test Weight Set Direct"
        filters = {
            'hp': 1.5,
            'mana': 2.0
        }
        
        print(f"✓ Test data prepared - name: {name}, filters: {filters}")
        
        # Call the local function
        print("Calling local.add_weights_set...")
        weight_set_id = local.add_weights_set(user, name, filters)
        print(f"✓ Weight set created with ID: {weight_set_id}")
        
        # Try to get the weight set back
        print("Calling local.get_weight_set...")
        weight_set_data = local.get_weight_set(weight_set_id, user)
        print(f"✓ Retrieved weight set data: {weight_set_data}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_local_weight_set()
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Tests failed!")
        sys.exit(1) 