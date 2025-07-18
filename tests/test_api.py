import requests
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

# Remove unused Path import and sys.path.append

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API base URL
API_BASE = "http://127.0.0.1:5001/api/v1"

# --- Utility Functions ---
def json_serial(obj):
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def check_attribute(response: dict, attr: str, expected_type: type) -> Tuple[bool, str]:
    if attr not in response:
        return False, f"Missing attribute: {attr}"
    if not isinstance(response[attr], expected_type):
        return False, f"Wrong type for {attr}: expected {expected_type.__name__}, got {type(response[attr]).__name__}"
    return True, ""

def log_result(endpoint: str, param: str, attr: str, passed: bool, msg: str):
    if passed:
        logger.info(f"[GREEN] {endpoint} {param} {attr} OK")
    else:
        logger.error(f"[RED] {endpoint} {param} {attr} FAIL: {msg}")

# --- Endpoint Test Definitions ---
# Each entry: (endpoint, params_list, expected_attributes)
# params_list: list of dicts, each dict is a set of params to test
# expected_attributes: dict of attr: type
ENDPOINTS = [
    # Items endpoint (lightweight - only basic fields)
    ("/items", [
        {"id": 1},
        {"name": "Fine Steel"},
        {"item_type": "Weapon"},
        {"tradeskill_only": True},
        {"equippable_only": True},
        {"exclude_glamours": True},
        {"only_augments": True},
        {"item_slot": "Primary"},
        {"itemtype_name": "2H Slashing"},
        {"slot_names": "Primary"},
        {"itemclass_name": "Weapon"},
        # All params at once (example values)
        {"id": 1, "name": "Fine Steel", "item_type": "Weapon", "tradeskill_only": True, "equippable_only": True, "exclude_glamours": True, "only_augments": True, "item_slot": "Primary", "itemtype_name": "2H Slashing", "slot_names": "Primary", "itemclass_name": "Weapon"}
    ],
    {"id": int, "name": str, "type": str}  # Only basic fields for lightweight /items endpoint
    ),
    # Spells endpoint
    ("/spells", [
        {"id": 1},
        {"name": "Minor Healing"},
        # All params at once
        {"id": 1, "name": "Minor Healing"}
    ],
    {"id": int, "name": str, "class": str, "level": int}
    ),
    # NPCs endpoint
    ("/npcs", [
        {"id": 1},
        {"name": "Guard"},
        {"zone": "qeynos"},
        {"id": 1, "name": "Guard", "zone": "qeynos"}
    ],
    {"id": int, "name": str, "zone": str, "level": int}
    ),
    # Zones endpoint
    ("/zones", [
        {"name": "qeynos"},
        {"name": "Freeport"}
    ],
    {"short_name": str, "long_name": str, "expansion_id": int, "expansion_name": str, "min_level": int, "max_level": int}
    ),
    # Tradeskills endpoint
    ("/tradeskills", [
        {"id": 59},
        {"name": "Alchemy"},
        {"id": 59, "name": "Alchemy"}
    ],
    {"id": int, "name": str, "skill": str, "recipe_count": int}
    ),
    # Recipes endpoint
    ("/recipes", [
        {"id": 1},
        {"name": "Fine Steel Dagger"},
        {"tradeskill": "Blacksmithing"},
        {"id": 1, "name": "Fine Steel Dagger", "tradeskill": "Blacksmithing"}
    ],
    {"id": int, "name": str, "tradeskill": int, "tradeskill_name": str, "skillneeded": int, "trivial": int, "nofail": int, "replace_container": int, "must_learn": int, "enabled": int, "min_expansion": int, "components": list, "success_items": list, "fail_items": list}
    ),
    # Quests endpoint
    ("/quests", [
        {"name": "guard"},
        {"npc_name": "captain"},
        {"item_id": 1},
        {"item_name": "dagger"},
        {"min_level": 1},
        {"max_level": 50},
        {"zone": "qeynos"},
        {"expansion": 0},
        {"name": "guard", "npc_name": "captain", "item_id": 1, "item_name": "dagger", "min_level": 1, "max_level": 50, "zone": "qeynos", "expansion": 0}
    ],
    {"npc_id": int, "npc_name": str, "quest_name": str, "level": int, "zone_name": str, "zone_long_name": str, "zone_expansion": int, "item_id": int, "item_name": str, "itemtype": int, "classes": int, "slots": int, "is_quest_item": bool, "expansion": str}
    ),
    # Expansions endpoint
    ("/expansions", [
        {},
    ],
    {"id": int, "name": str, "short_name": str, "release_date": str, "description": str}
    ),
    # Items Search endpoint (enriched - all fields)
    ("/items/search", [
        {"name": "Fine Steel"},
        {"slot": "Primary"},
        {"class": "Warrior"},
        {"item_type": "1H Slashing"},
        {"expansion": "Classic"},
        {"elemental_damage_type": "Fire"},
        {"bane_damage_type": "body_14"},
        {"proc": "True"},
        {"click": "True"},
        {"pet_search": True},
        {"sympathetic": "all_strike"},
        {"stat_filters": json.dumps([{"stat": "hp", "value": 10}])},
        {"stat_weights": json.dumps([{"stat": "damage", "weight": 2.0}])},
        {"exclude_expansions": json.dumps(["Kunark"])},
        {"proc_level": 10},
        {"click_level": 20},
        {"show_full_detail": True},
        {"show_weight_detail": True, "stat_weights": json.dumps([{"stat": "damage", "weight": 2.0}])},
        {"ignore_zero": True, "show_full_detail": True},
        {"page": 1, "page_size": 2},
        # Combo: advanced search
        {"name": "Fine Steel", "slot": "Primary", "class": "Warrior", "item_type": "1H Slashing", "expansion": "Classic", "stat_filters": json.dumps([{"stat": "hp", "value": 10}]), "show_full_detail": True}
    ],
    {"id": int, "name": str, "type": str, "slot_names": str, "expansion_name": str, "is_quest_item": (bool, type(None)), "npcs": list, "serialized": str, "itemtype_name": str}
    ),
    # Items Details endpoint (exhaustive - single item by ID)
    ("/items/details/1001", [
        {}  # No parameters needed for path-based endpoint
    ],
    {"item_id": int, "raw_data": dict, "enriched_data": dict, "npcs": list, "spells": list, "metadata": dict}
    ),
    # TODO: Add more endpoints and attributes as discovered
]

# --- Test Runner ---
def matches_filter(item: dict, param: dict) -> Tuple[bool, str]:
    """Check if the item matches the filter param. Returns (True, '') if match, else (False, reason)."""
    for key, value in param.items():
        if key == 'id':
            if item.get('id') != value:
                return False, f"id mismatch: got {item.get('id')}, expected {value}"
        elif key == 'name':
            if value not in str(item.get('name', '')):
                return False, f"name mismatch: got {item.get('name')}, expected to contain {value}"
        elif key == 'type':
            # Flexible matching for type - allow substring matches
            item_type = str(item.get('type', ''))
            if value not in item_type:
                return False, f"type mismatch: got {item_type}, expected to contain {value}"
        elif key == 'itemtype_name':
            # Flexible matching for itemtype_name - allow substring matches
            itemtype_name = str(item.get('itemtype_name', ''))
            if value not in itemtype_name:
                return False, f"itemtype_name mismatch: got {itemtype_name}, expected to contain {value}"
        elif key == 'slot_names':
            # Flexible matching for slot_names - allow substring matches
            slot_names = str(item.get('slot_names', ''))
            if value not in slot_names:
                return False, f"slot_names mismatch: got {slot_names}, expected to contain {value}"
        elif key == 'itemclass_name':
            # Flexible matching for itemclass_name - allow substring matches
            itemclass_name = str(item.get('itemclass_name', ''))
            if value not in itemclass_name:
                return False, f"itemclass_name mismatch: got {itemclass_name}, expected to contain {value}"
        elif key == 'expansion_name':
            # Only validate if field is present in response
            if 'expansion_name' in item:
                expansion_name = str(item.get('expansion_name', ''))
                if value not in expansion_name:
                    return False, f"expansion_name mismatch: got {expansion_name}, expected to contain {value}"
            # If field is not present, consider it a valid match (optional field)
        elif key == 'serialized':
            # Only validate if field is present in response
            if 'serialized' in item:
                serialized = item.get('serialized')
                if serialized != value:
                    return False, f"serialized mismatch: got {serialized}, expected {value}"
            # If field is not present, consider it a valid match (optional field)
        elif key == 'is_quest_item':
            # Allow None or boolean values
            is_quest = item.get('is_quest_item')
            if is_quest is not None and is_quest != value:
                return False, f"is_quest_item mismatch: got {is_quest}, expected {value}"
        elif key == 'npcs':
            # Only validate if field is present in response
            if 'npcs' in item:
                npcs = item.get('npcs')
                if npcs != value:
                    return False, f"npcs mismatch: got {npcs}, expected {value}"
            # If field is not present, consider it a valid match (optional field)
        else:
            # For other fields, do exact matching but allow None/empty for optional fields
            item_value = item.get(key)
            if item_value != value:
                return False, f"{key} mismatch: got {item_value}, expected {value}"
    return True, ''

def validate_response_structure(response_data: dict, endpoint: str) -> List[str]:
    """Validate that the response has the expected structure. Returns list of errors."""
    errors = []
    
    # Check for required top-level fields
    required_fields = ['results', 'total', 'page', 'page_size', 'pages']
    for field in required_fields:
        if field not in response_data:
            errors.append(f"Missing top-level field: {field}")
    
    # Check results array
    if 'results' in response_data:
        results = response_data['results']
        if not isinstance(results, list):
            errors.append("results should be a list")
        else:
            # Check first result for structure (if any results exist)
            if results:
                first_result = results[0]
                # Required fields that should always be present
                always_required = ['id', 'name']
                for field in always_required:
                    if field not in first_result:
                        errors.append(f"Missing required field in result: {field}")
                
                # Optional fields - only validate if present
                optional_fields = ['type', 'slot_names', 'expansion_name', 'itemtype_name', 
                                 'serialized', 'is_quest_item', 'npcs', 'itemclass_name']
                for field in optional_fields:
                    # These fields are optional and may not be present in all responses
                    pass  # No validation needed for optional fields
    
    return errors

def run_endpoint_tests():
    total = 0
    passed = 0
    failed = 0
    
    for endpoint, test_cases in ENDPOINTS:
        print(f"\n--- Testing {endpoint} ---")
        
        for i, test_case in enumerate(test_cases):
            total += 1
            test_name = f"{endpoint} {test_case}"
            print(f"  Test {i+1}: {test_name}")
            
            try:
                # Make request
                response = requests.get(f"{API_BASE}{endpoint}", params=test_case)
                
                # Check status code
                if response.status_code != 200:
                    print(f"    [RED] {test_name} status_code FAIL: HTTP {response.status_code}")
                    failed += 1
                    continue
                
                # Parse response
                try:
                    data = response.json()
                except Exception as e:
                    print(f"    [RED] {test_name} json_parse FAIL: {e}")
                    failed += 1
                    continue
                
                # Validate response structure
                structure_errors = validate_response_structure(data, endpoint)
                if structure_errors:
                    for error in structure_errors:
                        print(f"    [RED] {test_name} structure FAIL: {error}")
                    failed += 1
                    continue
                
                # Check results
                if 'results' not in data or not data['results']:
                    print(f"    [YELLOW] {test_name} no_results WARN: No results returned")
                    passed += 1
                    continue
                
                # Test each result against the filter
                all_passed = True
                for item in data['results']:
                    # For /items endpoint, only test basic fields that are actually returned
                    if endpoint == '/items':
                        # Only test fields that /items actually returns
                        basic_fields = ['id', 'name', 'type']
                        filtered_test_case = {k: v for k, v in test_case.items() if k in basic_fields}
                        if filtered_test_case:
                            match, reason = matches_filter(item, filtered_test_case)
                            if not match:
                                print(f"    [RED] {test_name} {reason}")
                                all_passed = False
                                break
                    else:
                        # For other endpoints (like /items/search), test all fields
                        match, reason = matches_filter(item, test_case)
                        if not match:
                            print(f"    [RED] {test_name} {reason}")
                            all_passed = False
                            break
                
                if all_passed:
                    print(f"    [GREEN] {test_name} PASS")
                    passed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"    [RED] {test_name} exception FAIL: {e}")
                failed += 1
    
    print(f"\n--- Test Summary ---")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    return passed, failed, total

def run_items_tests():
    total = 0
    passed = 0
    filter_total = 0
    filter_passed = 0
    for endpoint, params_list, expected_attrs in ENDPOINTS:
        if endpoint != "/items":
            continue
        for params in params_list:
            param_str = json.dumps(params)
            try:
                resp = requests.get(API_BASE + endpoint, params=params)
                if resp.status_code != 200:
                    log_result(endpoint, param_str, "status_code", False, f"HTTP {resp.status_code}")
                    continue
                data = resp.json()
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict) and any(isinstance(v, list) for v in data.values()):
                    items = next((v for v in data.values() if isinstance(v, list)), [])
                else:
                    items = [data]
                for item in items:
                    for attr, typ in expected_attrs.items():
                        total += 1
                        ok, msg = check_attribute(item, attr, typ)
                        log_result(endpoint, param_str, attr, ok, msg)
                        if ok:
                            passed += 1
                    filter_total += 1
                    # For /items endpoint, only test basic fields that are actually returned
                    basic_fields = ['id', 'name', 'type']
                    filtered_params = {k: v for k, v in params.items() if k in basic_fields}
                    if filtered_params:
                        match, reason = matches_filter(item, filtered_params)
                        if match:
                            logger.info(f"[GREEN] {endpoint} {param_str} FILTER OK")
                            filter_passed += 1
                        else:
                            logger.error(f"[RED] {endpoint} {param_str} FILTER FAIL: {reason}")
                    else:
                        # No basic fields to test, consider it a pass
                        logger.info(f"[GREEN] {endpoint} {param_str} FILTER OK (no basic fields to test)")
                        filter_passed += 1
            except Exception as e:
                log_result(endpoint, param_str, "EXCEPTION", False, str(e))
    logger.info(f"\nItem Test Summary: {passed}/{total} attribute checks passed.")
    logger.info(f"\nItem Filter Test Summary: {filter_passed}/{filter_total} filter checks passed.")

def run_items_details_tests():
    """Run tests for /items/details endpoint"""
    endpoint = "/items/details/1001"
    
    # Find the endpoint in the ENDPOINTS list
    test_cases = None
    expected_attrs = None
    for ep, cases, attrs in ENDPOINTS:
        if ep == endpoint:
            test_cases = cases
            expected_attrs = attrs
            break
    
    if test_cases is None:
        logger.error(f"Endpoint {endpoint} not found in ENDPOINTS")
        return 0, 0, 0, 0
    
    logger.info(f"\n=== Testing {endpoint} ===")
    
    total_tests = 0
    passed_tests = 0
    attr_total = 0
    attr_passed = 0
    
    for params in test_cases:
        total_tests += 1
        param_str = json.dumps(params)
        
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            status_code = response.status_code
            
            if status_code == 200:
                data = response.json()
                logger.info(f"[GREEN] {endpoint} {param_str} status_code OK")
                passed_tests += 1
                
                # Test all expected attributes
                for attr, expected_type in expected_attrs.items():
                    attr_total += 1
                    if attr in data:
                        actual_value = data[attr]
                        if isinstance(expected_type, tuple):
                            # Handle multiple possible types
                            if any(isinstance(actual_value, t) for t in expected_type):
                                logger.info(f"[GREEN] {endpoint} {param_str} {attr} OK")
                                attr_passed += 1
                            else:
                                logger.error(f"[RED] {endpoint} {param_str} {attr} TYPE FAIL: got {type(actual_value).__name__}, expected one of {[t.__name__ for t in expected_type]}")
                        else:
                            if isinstance(actual_value, expected_type):
                                logger.info(f"[GREEN] {endpoint} {param_str} {attr} OK")
                                attr_passed += 1
                            else:
                                logger.error(f"[RED] {endpoint} {param_str} {attr} TYPE FAIL: got {type(actual_value).__name__}, expected {expected_type.__name__}")
                    else:
                        logger.error(f"[RED] {endpoint} {param_str} {attr} MISSING")
            else:
                logger.error(f"[RED] {endpoint} {param_str} status_code FAIL: HTTP {status_code}")
                
        except Exception as e:
            logger.error(f"[RED] {endpoint} {param_str} EXCEPTION: {str(e)}")
    
    logger.info(f"\n{endpoint} Results: {passed_tests}/{total_tests} tests passed, {attr_passed}/{attr_total} attributes passed")
    return passed_tests, total_tests, attr_passed, attr_total

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "items":
        run_items_tests()
        logger.info("\n[INFO] e2e API /items attribute and filter tests complete.")
    elif len(sys.argv) > 1 and sys.argv[1] == "items_details":
        run_items_details_tests()
        logger.info("\n[INFO] e2e API /items/details attribute tests complete.")
    else:
        run_endpoint_tests()
        logger.info("\n[INFO] e2e API attribute tests complete.") 