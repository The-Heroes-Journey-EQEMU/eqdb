#!/usr/bin/env python3

import local

# Create a simple user object
class User:
    def __init__(self):
        self.id = 1

user = User()

# Test the add_weights_set function
try:
    print("Testing add_weights_set...")
    filters = {'hp': 1.5, 'mana': 2.0}
    result = local.add_weights_set(user, "Test Weight Set", filters)
    print(f"Result: {result}")
    print(f"Type: {type(result)}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 