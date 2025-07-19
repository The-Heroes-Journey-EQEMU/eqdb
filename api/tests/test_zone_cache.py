import unittest
from unittest.mock import patch, MagicMock
from db.zone import ZoneDB

class TestZoneDBCache(unittest.TestCase):
    def setUp(self):
        # Patch the engine.connect method for all tests
        self.patcher = patch('db.zone.create_engine')
        self.mock_create_engine = self.patcher.start()
        self.mock_engine = MagicMock()
        self.mock_create_engine.return_value = self.mock_engine
        self.mock_conn = MagicMock()
        self.mock_engine.connect.return_value.__enter__.return_value = self.mock_conn
        # Reset cache before each test
        ZoneDB._zone_cache = None
        ZoneDB._zone_cache_populated = False

    def tearDown(self):
        self.patcher.stop()
        ZoneDB._zone_cache = None
        ZoneDB._zone_cache_populated = False

    def test_zone_cache_populates_and_uses_cache(self):
        # Simulate DB returning two zones
        self.mock_conn.execute.return_value.fetchall.return_value = [
            {'short_name': 'qeynos', 'zoneidnumber': 1, 'long_name': 'Qeynos'},
            {'short_name': 'freeport', 'zoneidnumber': 2, 'long_name': 'Freeport'}
        ]
        zdb = ZoneDB()
        # First call should populate cache and return correct value
        zoneid, longname = zdb.get_zone_long_name('qeynos')
        self.assertEqual(zoneid, 1)
        self.assertEqual(longname, 'Qeynos')
        # Second call should use cache, not DB
        self.mock_conn.execute.reset_mock()
        zoneid2, longname2 = zdb.get_zone_long_name('freeport')
        self.assertEqual(zoneid2, 2)
        self.assertEqual(longname2, 'Freeport')
        self.mock_conn.execute.assert_not_called()

    def test_zone_cache_miss(self):
        # Simulate DB returning one zone
        self.mock_conn.execute.return_value.fetchall.return_value = [
            {'short_name': 'qeynos', 'zoneidnumber': 1, 'long_name': 'Qeynos'}
        ]
        zdb = ZoneDB()
        zoneid, longname = zdb.get_zone_long_name('notfound')
        self.assertIsNone(zoneid)
        self.assertEqual(longname, 'Unknown Zone')

if __name__ == '__main__':
    unittest.main() 