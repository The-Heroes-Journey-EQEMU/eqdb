from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)

class ExpansionDB:
    def __init__(self, connection_string):
        """Initialize the expansion database connection"""
        self.engine = create_engine(connection_string)
        logger.info("Expansion database initialized")
    
    def get_all_expansions(self):
        """Get all expansions with their details"""
        expansions_data = [
            {
                'id': 0,
                'name': 'Classic',
                'short_name': 'classic',
                'release_date': '1999-03-16',
                'description': 'Original EverQuest release with classic zones and content'
            },
            {
                'id': 1,
                'name': 'The Ruins of Kunark',
                'short_name': 'kunark',
                'release_date': '2000-04-24',
                'description': 'First expansion introducing the Iksar race and Kunark continent'
            },
            {
                'id': 2,
                'name': 'The Scars of Velious',
                'short_name': 'velious',
                'release_date': '2000-12-05',
                'description': 'Second expansion featuring the frozen continent of Velious'
            },
            {
                'id': 3,
                'name': 'The Shadows of Luclin',
                'short_name': 'luclin',
                'release_date': '2001-12-04',
                'description': 'Third expansion introducing the Vah Shir race and Luclin moon'
            },
            {
                'id': 4,
                'name': 'The Planes of Power',
                'short_name': 'planes',
                'release_date': '2002-10-28',
                'description': 'Fourth expansion featuring divine planes and deity quests'
            },
            {
                'id': 5,
                'name': 'The Legacy of Ykesha',
                'short_name': 'loy',
                'release_date': '2003-02-25',
                'description': 'Fifth expansion introducing the Froglok race and Ykesha content'
            },
            {
                'id': 6,
                'name': 'Lost Dungeons of Norrath',
                'short_name': 'ldon',
                'release_date': '2003-09-09',
                'description': 'Sixth expansion featuring instanced dungeons and adventure system'
            },
            {
                'id': 7,
                'name': 'Gates of Discord',
                'short_name': 'god',
                'release_date': '2004-02-10',
                'description': 'Seventh expansion featuring the continent of Taelosia'
            },
            {
                'id': 8,
                'name': 'Omens of War',
                'short_name': 'oow',
                'release_date': '2004-09-14',
                'description': 'Eighth expansion featuring the continent of Kuua'
            },
            {
                'id': 9,
                'name': 'Dragons of Norrath',
                'short_name': 'don',
                'release_date': '2005-02-15',
                'description': 'Ninth expansion featuring dragon-themed content'
            },
            {
                'id': 10,
                'name': 'Depths of Darkhollow',
                'short_name': 'dodh',
                'release_date': '2005-09-13',
                'description': 'Tenth expansion featuring underground content'
            },
            {
                'id': 11,
                'name': 'Prophecy of Ro',
                'short_name': 'por',
                'release_date': '2006-02-21',
                'description': 'Eleventh expansion featuring the continent of Taelosia'
            },
            {
                'id': 12,
                'name': 'The Serpent\'s Spine',
                'short_name': 'tss',
                'release_date': '2006-09-19',
                'description': 'Twelfth expansion featuring the continent of Taelosia'
            },
            {
                'id': 13,
                'name': 'The Buried Sea',
                'short_name': 'tbs',
                'release_date': '2007-02-13',
                'description': 'Thirteenth expansion featuring nautical content'
            },
            {
                'id': 14,
                'name': 'Secrets of Faydwer',
                'short_name': 'sof',
                'release_date': '2007-11-13',
                'description': 'Fourteenth expansion featuring the continent of Faydwer'
            },
            {
                'id': 15,
                'name': 'Seeds of Destruction',
                'short_name': 'sod',
                'release_date': '2008-10-21',
                'description': 'Fifteenth expansion featuring the continent of Taelosia'
            },
            {
                'id': 16,
                'name': 'Underfoot',
                'short_name': 'uf',
                'release_date': '2009-12-15',
                'description': 'Sixteenth expansion featuring underground content'
            },
            {
                'id': 17,
                'name': 'House of Thule',
                'short_name': 'hot',
                'release_date': '2010-10-12',
                'description': 'Seventeenth expansion featuring dream-themed content'
            },
            {
                'id': 18,
                'name': 'Veil of Alaris',
                'short_name': 'voa',
                'release_date': '2011-11-15',
                'description': 'Eighteenth expansion featuring the continent of Alaris'
            },
            {
                'id': 19,
                'name': 'Rain of Fear',
                'short_name': 'rof',
                'release_date': '2012-11-28',
                'description': 'Nineteenth expansion featuring the continent of Taelosia'
            }
        ]
        return expansions_data
    
    def get_expansion_by_id(self, expansion_id):
        """Get expansion details by ID"""
        expansions = self.get_all_expansions()
        for expansion in expansions:
            if expansion['id'] == expansion_id:
                return expansion
        return None
    
    def get_expansion_by_name(self, name):
        """Get expansion details by name (case-insensitive)"""
        expansions = self.get_all_expansions()
        for expansion in expansions:
            if expansion['name'].lower() == name.lower() or expansion['short_name'].lower() == name.lower():
                return expansion
        return None
    
    def get_zones_by_expansion(self):
        """Get zones grouped by expansion from the database"""
        with self.engine.connect() as conn:
            query = text("""
                SELECT DISTINCT z.expansion, z.short_name, z.long_name
                FROM zone z
                WHERE z.expansion IS NOT NULL
                ORDER BY z.expansion, z.long_name
            """)
            results = conn.execute(query).fetchall()
            
            zones_by_expansion = {}
            for row in results:
                expansion_id = row[0]
                zone_data = {
                    'short_name': row[1],
                    'long_name': row[2],
                    'expansion_id': expansion_id
                }
                
                # Get expansion name
                expansion_info = self.get_expansion_by_id(expansion_id)
                if expansion_info:
                    zone_data['expansion_name'] = expansion_info['name']
                else:
                    zone_data['expansion_name'] = f'Expansion {expansion_id}'
                
                if expansion_id not in zones_by_expansion:
                    zones_by_expansion[expansion_id] = {
                        'expansion_info': expansion_info,
                        'zones': []
                    }
                zones_by_expansion[expansion_id]['zones'].append(zone_data)
            
            return zones_by_expansion
    
    def get_zones_in_expansion(self, expansion_id):
        """Get zones for a specific expansion"""
        with self.engine.connect() as conn:
            query = text("""
                SELECT short_name, long_name
                FROM zone
                WHERE expansion = :expansion_id
                ORDER BY long_name
            """)
            results = conn.execute(query, {"expansion_id": expansion_id}).fetchall()
            
            zones = []
            expansion_info = self.get_expansion_by_id(expansion_id)
            
            for row in results:
                zone_data = {
                    'short_name': row[0],
                    'long_name': row[1],
                    'expansion_id': expansion_id,
                    'expansion_name': expansion_info['name'] if expansion_info else f'Expansion {expansion_id}'
                }
                zones.append(zone_data)
            
            return zones 