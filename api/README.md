## Models

### ZoneDB (db/zone.py)

- The `ZoneDB` class provides access to zone data from the remote gamedb (MySQL).
- Use `get_zone_long_name(shortname)` to retrieve a tuple of (zoneidnumber, long_name) for a given zone shortname.
- **Caching:**
  - Zone long name lookups are cached in memory after the first database query.
  - On the first call to `get_zone_long_name`, all zone shortname mappings are loaded into a class-level cache.
  - Subsequent lookups are served from the cache, reducing database load and improving performance.
  - The cache is only refreshed if the process restarts.
  - This strategy is safe because the zone table is static and rarely changes.
- **Testing:**
  - Tests in `tests/test_zone_cache.py` verify that the cache is populated and used, and that no additional database queries are made after the initial load.
- Example usage:

```python
from db.zone import ZoneDB
zone_db = ZoneDB()
zone_id, zone_name = zone_db.get_zone_long_name('freportw')
```

- This model should be used for all zone lookups instead of static mappings or utility functions. 