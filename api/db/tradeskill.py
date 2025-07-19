from sqlalchemy import text
import os
from api.db_manager import db_manager

def parse_skill(skill_num):
    """Parse skill number to tradeskill name"""
    skill_map = {
        59: 'Alchemy',
        60: 'Baking',
        61: 'Tailoring',
        63: 'Blacksmithing',
        64: 'Fletching',
        65: 'Brewing',
        68: 'Jewel Crafting',
        69: 'Pottery',
        58: 'Research',
        56: 'Poison Making',
        57: 'Tinkering'
    }
    return skill_map.get(skill_num, f'Unknown Skill {skill_num}')

class TradeskillDB:
    def __init__(self):
        """Initialize the TradeskillDB class."""
        pass
    
    def get_tradeskill_raw_data(self, tradeskill_id=None, name=None):
        """Get raw tradeskill data from the database"""
        engine = db_manager.get_engine_for_table('tradeskill_recipe')
        with engine.connect() as conn:
            if tradeskill_id:
                # For ID search, we'll return the tradeskill category if it's a valid skill number
                if tradeskill_id in [59, 60, 61, 63, 64, 65, 68, 69, 58, 56, 57]:
                    return {
                        'id': tradeskill_id,
                        'name': parse_skill(tradeskill_id),
                        'skill': parse_skill(tradeskill_id)
                    }
                return None
            elif name:
                # For name search, find matching tradeskill categories
                query = text("""
                    SELECT DISTINCT tradeskill, COUNT(*) as recipe_count
                    FROM tradeskill_recipe 
                    WHERE tradeskill IN (59, 60, 61, 63, 64, 65, 68, 69, 58, 56, 57)
                    AND enabled = 1
                    GROUP BY tradeskill
                    ORDER BY tradeskill
                """)
                results = conn.execute(query).fetchall()
                
                tradeskills = []
                for row in results:
                    skill_num = row[0]
                    skill_name = parse_skill(skill_num)
                    
                    # Filter by name if provided
                    if name.lower() in skill_name.lower():
                        tradeskills.append({
                            'id': skill_num,
                            'name': skill_name,
                            'skill': skill_name,
                            'recipe_count': row[1]
                        })
                
                return tradeskills[:50]  # Limit to 50 results
            return None

    def get_recipe_raw_data(self, recipe_id=None, name=None, tradeskill=None):
        """Get raw recipe data from the database"""
        engine = db_manager.get_engine_for_table('tradeskill_recipe')
        with engine.connect() as conn:
            if recipe_id:
                # Get recipe details
                query = text("""
                    SELECT id, name, tradeskill, skillneeded, trivial, nofail, 
                           replace_container, must_learn, enabled, min_expansion
                    FROM tradeskill_recipe 
                    WHERE id = :recipe_id AND enabled = 1
                """)
                result = conn.execute(query, {"recipe_id": recipe_id}).fetchone()
                if result:
                    recipe_data = dict(result._mapping)
                    recipe_data['tradeskill_name'] = parse_skill(recipe_data['tradeskill'])
                    
                    # Get component items
                    components_query = text("""
                        SELECT tre.item_id, i.Name as item_name, tre.componentcount, 
                               tre.successcount, tre.failcount, tre.iscontainer
                        FROM tradeskill_recipe_entries tre
                        JOIN items i ON tre.item_id = i.id
                        WHERE tre.recipe_id = :recipe_id
                        ORDER BY tre.componentcount DESC, tre.successcount DESC, i.Name
                    """)
                    components_result = conn.execute(components_query, {"recipe_id": recipe_id}).fetchall()
                    
                    components = []
                    success_items = []
                    fail_items = []
                    
                    for comp in components_result:
                        comp_data = dict(comp._mapping)
                        if comp_data['componentcount'] > 0:
                            components.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['componentcount']
                            })
                        if comp_data['successcount'] > 0:
                            success_items.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['successcount']
                            })
                        if comp_data['failcount'] > 0:
                            fail_items.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['failcount']
                            })
                    
                    recipe_data['components'] = components
                    recipe_data['success_items'] = success_items
                    recipe_data['fail_items'] = fail_items
                    
                    return recipe_data
                return None
            elif name:
                query = text("""
                    SELECT id, name, tradeskill, skillneeded, trivial, nofail, 
                           replace_container, must_learn, enabled, min_expansion
                    FROM tradeskill_recipe 
                    WHERE name LIKE :name AND enabled = 1
                    ORDER BY name
                    LIMIT 50
                """)
                results = conn.execute(query, {"name": f"%{name}%"}).fetchall()
                recipes = []
                for row in results:
                    recipe_data = dict(row._mapping)
                    recipe_data['tradeskill_name'] = parse_skill(recipe_data['tradeskill'])
                    
                    # Get component items for this recipe
                    recipe_id = recipe_data['id']
                    components_query = text("""
                        SELECT tre.item_id, i.Name as item_name, tre.componentcount, 
                               tre.successcount, tre.failcount, tre.iscontainer
                        FROM tradeskill_recipe_entries tre
                        JOIN items i ON tre.item_id = i.id
                        WHERE tre.recipe_id = :recipe_id
                        ORDER BY tre.componentcount DESC, tre.successcount DESC, i.Name
                    """)
                    components_result = conn.execute(components_query, {"recipe_id": recipe_id}).fetchall()
                    
                    components = []
                    success_items = []
                    fail_items = []
                    
                    for comp in components_result:
                        comp_data = dict(comp._mapping)
                        if comp_data['componentcount'] > 0:
                            components.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['componentcount']
                            })
                        if comp_data['successcount'] > 0:
                            success_items.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['successcount']
                            })
                        if comp_data['failcount'] > 0:
                            fail_items.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['failcount']
                            })
                    
                    recipe_data['components'] = components
                    recipe_data['success_items'] = success_items
                    recipe_data['fail_items'] = fail_items
                    
                    recipes.append(recipe_data)
                return recipes
            elif tradeskill:
                # Convert tradeskill name to skill number
                skill_map = {v: k for k, v in {
                    59: 'Alchemy', 60: 'Baking', 61: 'Tailoring', 63: 'Blacksmithing',
                    64: 'Fletching', 65: 'Brewing', 68: 'Jewel Crafting', 69: 'Pottery',
                    58: 'Research', 56: 'Poison Making', 57: 'Tinkering'
                }.items()}
                
                skill_num = skill_map.get(tradeskill)
                if skill_num is None:
                    return []
                
                query = text("""
                    SELECT id, name, tradeskill, skillneeded, trivial, nofail, 
                           replace_container, must_learn, enabled, min_expansion
                    FROM tradeskill_recipe 
                    WHERE tradeskill = :skill_num AND enabled = 1
                    ORDER BY name
                    LIMIT 50
                """)
                results = conn.execute(query, {"skill_num": skill_num}).fetchall()
                recipes = []
                for row in results:
                    recipe_data = dict(row._mapping)
                    recipe_data['tradeskill_name'] = parse_skill(recipe_data['tradeskill'])
                    
                    # Get component items for this recipe
                    recipe_id = recipe_data['id']
                    components_query = text("""
                        SELECT tre.item_id, i.Name as item_name, tre.componentcount, 
                               tre.successcount, tre.failcount, tre.iscontainer
                        FROM tradeskill_recipe_entries tre
                        JOIN items i ON tre.item_id = i.id
                        WHERE tre.recipe_id = :recipe_id
                        ORDER BY tre.componentcount DESC, tre.successcount DESC, i.Name
                    """)
                    components_result = conn.execute(components_query, {"recipe_id": recipe_id}).fetchall()
                    
                    components = []
                    success_items = []
                    fail_items = []
                    
                    for comp in components_result:
                        comp_data = dict(comp._mapping)
                        if comp_data['componentcount'] > 0:
                            components.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['componentcount']
                            })
                        if comp_data['successcount'] > 0:
                            success_items.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['successcount']
                            })
                        if comp_data['failcount'] > 0:
                            fail_items.append({
                                'item_id': comp_data['item_id'],
                                'item_name': comp_data['item_name'],
                                'count': comp_data['failcount']
                            })
                    
                    recipe_data['components'] = components
                    recipe_data['success_items'] = success_items
                    recipe_data['fail_items'] = fail_items
                    
                    recipes.append(recipe_data)
                return recipes
            return None
