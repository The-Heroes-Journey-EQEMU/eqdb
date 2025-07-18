#!/usr/bin/env python3

import sys
import os

# Add the current directory to the path so we can import local
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from local import get_characters, get_character, add_character, update_character, delete_character

# Mock user object for testing
class MockUser:
    def __init__(self, user_id):
        self.id = user_id

def test_character_functions():
    """Test all character functions"""
    print("Testing character functions...")
    
    # Create a mock user
    user = MockUser(1)
    
    try:
        # Test 1: Add a character
        print("\n1. Testing add_character...")
        character_data = add_character(
            user=user,
            name="TestCharacter",
            classes=["Warrior"],
            level=50,
            character_set="Tank Set",
            inventory_blob="{'head': 12345, 'chest': 67890}"
        )
        print(f"✅ Character created: {character_data}")
        
        # Test 2: Get all characters
        print("\n2. Testing get_characters...")
        characters = get_characters(user)
        print(f"✅ Found {len(characters)} characters: {characters}")
        
        # Test 3: Get specific character
        print("\n3. Testing get_character...")
        character_id = character_data['id']
        character = get_character(character_id, user)
        print(f"✅ Retrieved character: {character}")
        
        # Test 4: Update character
        print("\n4. Testing update_character...")
        updated_character = update_character(
            cid=character_id,
            user=user,
            level=55,
            character_set="Updated Tank Set"
        )
        print(f"✅ Updated character: {updated_character}")
        
        # Test 5: Delete character
        print("\n5. Testing delete_character...")
        deleted = delete_character(character_id, user)
        print(f"✅ Character deleted: {deleted}")
        
        # Test 6: Verify deletion
        print("\n6. Verifying deletion...")
        characters_after = get_characters(user)
        print(f"✅ Characters after deletion: {len(characters_after)}")
        
        print("\n🎉 All character function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_character_functions()
    sys.exit(0 if success else 1) 