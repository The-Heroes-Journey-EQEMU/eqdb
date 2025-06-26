## API Testing Plan

### Overview
Our API testing plan involves ensuring that our local API endpoints return data in a format that matches the production API. This includes returning all fields, handling null values, and formatting datetimes correctly.

### Outstanding Tasks
- **Spell Endpoint**: Currently using `get_spell_json()` which returns limited fields. Will be addressed with new model implementation.
- **Other Endpoints**: Review and update other endpoints (e.g., NPCs, quests) to ensure they return raw data and match production format.

### How Testing Works
- We compare the response from our local API with the response from the production API.
- We ensure that all fields are present, null values are converted to empty strings, and datetimes are formatted as ISO strings.

### What is Broken
- The spell endpoint currently returns a limited set of fields, missing many attributes present in the production API.
- This is a known issue that will be addressed with the new model implementation, rather than modifying the current `spell.py`.

### Assumptions Made
- The production API returns all raw database fields.
- Local API should mirror the production API in terms of field presence and formatting.
- We will implement a new model for data fetching that will handle raw data consistently across all endpoints.

### Additional Context
- We have successfully updated the item endpoint to return raw data and match the production format.
- We need to apply similar changes to other endpoints to ensure consistency across the API.
- We are deferring changes to `spell.py` until the new model implementation is ready.

### Item Testing
- **What was Tested**: The item endpoint was tested to ensure it returns raw item data, matching the production API format.
- **What was Fixed**: The item endpoint was updated to return all fields, handle null values, and format datetimes correctly.
- **Remaining Issues**: None identified for the item endpoint. 