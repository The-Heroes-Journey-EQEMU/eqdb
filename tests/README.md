# API Tests

This directory contains tests for the EQDB API. The tests compare responses from the local development server against the production server to ensure compatibility.

## Setup

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the local development server is running:
```bash
FLASK_DEBUG=1 python3 eqdb.py
```

## Running Tests

To run all tests:
```bash
python3 test_api.py
```

## Test Cases

The test suite includes the following test cases:

### Items
- Item by ID
- Item by Name
- Item by Type

### Spells
- Spell by ID
- Spell by Name
- Spell by Class

### NPCs
- NPC by ID
- NPC by Name

### Zones
- Zone by ID
- Zone by Name

## Adding New Tests

To add a new test case:

1. Add a new test case to the `test_cases` list in `test_api.py`
2. Each test case should include:
   - `name`: A descriptive name for the test
   - `endpoint`: The API endpoint to test
   - `params`: A dictionary of query parameters

Example:
```python
{
    "name": "New Test Case",
    "endpoint": "/endpoint",
    "params": {"param1": "value1", "param2": "value2"}
}
``` 