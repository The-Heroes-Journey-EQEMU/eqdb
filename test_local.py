#!/usr/bin/env python3

import local

print("Testing local functions...")

# Create a simple user object
class User:
    def __init__(self):
        self.id = 1

user = User()

try:
    print("Testing get_weights_sets...")
    result = local.get_weights_sets(user)
    print("Result:", result)
except Exception as e:
    print("Error in get_weights_sets:", e)
    import traceback
    traceback.print_exc()

try:
    print("Testing add_weights_set...")
    filters = {'hp': 1.5, 'mana': 2.0}
    result = local.add_weights_set(user, "Test Weight Set", filters)
    print("Result:", result)
except Exception as e:
    print("Error in add_weights_set:", e)
    import traceback
    traceback.print_exc() 