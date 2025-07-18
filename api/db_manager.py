import configparser
from sqlalchemy import create_engine, inspect
import logging
from api.cache import cache_results

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    # Tables that should always use the old engine
    ALWAYS_OLD_ENGINE_TABLES = ['db_str']
    def __init__(self):
        self._engines = {}
        self._initialize_engines()

    def _get_config(self):
        config = configparser.ConfigParser()
        config.read('configuration.ini')
        return config

    def _initialize_engines(self):
        config = self._get_config()
        
        # New Database
        db_new_config = config['database_new']
        url_new = f"{db_new_config['driver']}{db_new_config['user']}:{db_new_config['password']}@{db_new_config['host']}:{db_new_config['port']}/{db_new_config['database']}"
        self._engines['new'] = create_engine(url_new)

        # Old Database
        db_old_config = config['database_old']
        url_old = f"{db_old_config['driver']}{db_old_config['user']}:{db_old_config['password']}@{db_old_config['host']}:{db_old_config['port']}/{db_old_config['database']}"
        self._engines['old'] = create_engine(url_old)
        
        logger.info("Database engines initialized.")

    @cache_results(ttl=3600)  # Cache for 1 hour
    def _table_exists_in_new_db(self, table_name):
        try:
            inspector = inspect(self._engines['new'])
            return inspector.has_table(table_name)
        except Exception as e:
            logger.error(f"Error checking for table '{table_name}' in new DB: {e}")
            # Fallback to old DB in case of error
            return False

    def get_engine_for_table(self, table_name):
        if table_name in self.ALWAYS_OLD_ENGINE_TABLES:
            return self._engines['old']
        if self._table_exists_in_new_db(table_name):
            # logger.debug(f"Using 'new' database engine for table '{table_name}'.")
            return self._engines['new']
        else:
            # logger.debug(f"Using 'old' database engine for table '{table_name}'.")
            return self._engines['old']

# Singleton instance
db_manager = DatabaseManager()
