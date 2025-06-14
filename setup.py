from distutils.core import setup

setup(name='EQDB',
      version='2.1',
      description='EverQuest Database for The Heroes Journey Emulator Server',
      install_requires=[
          'sqlalchemy',
          'flask',
          'Flask-Discord',
          'mysqldb',
        ])
