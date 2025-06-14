import os
import sys
import configparser

here = os.path.dirname(__file__)
if os.path.exists(os.path.join(here, 'configuration.ini')):
    print('Configuration already exists, please modify configuration.ino')
    sys.exit(0)

site_config = configparser.ConfigParser()

site_config['DEFAULT'] = {'site_fqdn': 'localhost',
                          'site_type': 'Development',
                          'debug': True,
                          'site_version': '0.0.0.0'}

site_config['thj'] = {'expansion': 5}

site_config['database'] = {'driver': '',
                           'user': '',
                           'password': '',
                           'database': '',
                           'host': '',
                           'port': ''}

site_config['local_database'] = {'connection': 'sqlite:///local_db.db'}

site_config['path'] = {'app_log': 'c:\\site\\eqdb\\eqdb.log',
                       'flask_log': 'c:\\site\\eqdb\\flask.log'}

site_config['discord'] = {'client_id': '',
                          'client_secret': ''}

with open(os.path.join(here, 'configuration.ini')) as fh:
    site_config.write(fh)

