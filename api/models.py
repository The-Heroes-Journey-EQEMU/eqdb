from flask_restx import fields

def create_models(api, v1):
    """Create all API models"""
    
    # Common response models
    paginated_model = api.model('PaginatedResponse', {
        'items': fields.List(fields.Raw),
        'total': fields.Integer,
        'page': fields.Integer,
        'per_page': fields.Integer
    })

    # User models
    user_model = v1.model('User', {
        'id': fields.Integer(description='User ID'),
        'email': fields.String(description='User email'),
        'is_admin': fields.Boolean(description='Admin status'),
        'created_at': fields.DateTime(description='Account creation date'),
        'last_login': fields.DateTime(description='Last login date'),
        'preferences': fields.Raw(description='User preferences')
    })

    user_create_model = v1.model('UserCreate', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
        'is_admin': fields.Boolean(description='Admin status', default=False)
    })

    user_login_model = v1.model('UserLogin', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password')
    })

    user_update_model = v1.model('UserUpdate', {
        'email': fields.String(description='User email'),
        'is_admin': fields.Boolean(description='Admin status')
    })

    password_change_model = v1.model('PasswordChange', {
        'current_password': fields.String(required=True, description='Current password'),
        'new_password': fields.String(required=True, description='New password')
    })

    # API Key models
    api_key_model = v1.model('ApiKey', {
        'id': fields.Integer(description='API Key ID'),
        'name': fields.String(description='API Key name'),
        'key_prefix': fields.String(description='API Key prefix'),
        'created_at': fields.DateTime(description='Creation date'),
        'last_used': fields.DateTime(description='Last usage date'),
        'is_active': fields.Boolean(description='Active status')
    })

    api_key_create_model = v1.model('ApiKeyCreate', {
        'name': fields.String(required=True, description='API Key name')
    })

    api_key_response_model = v1.model('ApiKeyResponse', {
        'id': fields.Integer(description='API Key ID'),
        'name': fields.String(description='API Key name'),
        'key_prefix': fields.String(description='API Key prefix'),
        'full_key': fields.String(description='Full API Key (only shown once)'),
        'created_at': fields.DateTime(description='Creation date'),
        'is_active': fields.Boolean(description='Active status')
    })

    # Authentication response models
    login_response_model = v1.model('LoginResponse', {
        'access_token': fields.String(description='JWT access token'),
        'refresh_token': fields.String(description='JWT refresh token'),
        'user': fields.Nested(user_model, description='User information')
    })

    # Item response model - using Raw to allow all fields from the database
    item_model = v1.model('Item', {
        'id': fields.Integer(description='Item ID'),
        'Name': fields.String(description='Item name'),
        'icon': fields.Integer(description='Item icon ID'),
        'itemtype': fields.Integer(description='Item type'),
        'slots': fields.Integer(description='Equipment slots'),
        'classes': fields.Integer(description='Allowed classes'),
        'races': fields.Integer(description='Allowed races'),
        'ac': fields.Integer(description='Armor class'),
        'hp': fields.Integer(description='Hit points'),
        'mana': fields.Integer(description='Mana'),
        'endur': fields.Integer(description='Endurance'),
        'astr': fields.Integer(description='Strength'),
        'asta': fields.Integer(description='Stamina'),
        'aagi': fields.Integer(description='Agility'),
        'adex': fields.Integer(description='Dexterity'),
        'acha': fields.Integer(description='Charisma'),
        'aint': fields.Integer(description='Intelligence'),
        'awis': fields.Integer(description='Wisdom'),
        'mr': fields.Integer(description='Magic resistance'),
        'fr': fields.Integer(description='Fire resistance'),
        'cr': fields.Integer(description='Cold resistance'),
        'dr': fields.Integer(description='Disease resistance'),
        'pr': fields.Integer(description='Poison resistance'),
        'price': fields.Integer(description='Item price'),
        'weight': fields.Integer(description='Item weight'),
        'size': fields.Integer(description='Item size'),
        'material': fields.Integer(description='Item material'),
        'color': fields.Integer(description='Item color'),
        'lore': fields.String(description='Item lore'),
        'nodrop': fields.Integer(description='No drop flag'),
        'norent': fields.Integer(description='No rent flag'),
        'attuneable': fields.Integer(description='Attuneable flag'),
        'questitemflag': fields.Integer(description='Quest item flag'),
        'tradeskills': fields.Integer(description='Tradeskill flag'),
        'created': fields.String(description='Creation date'),
        'updated': fields.String(description='Last update date'),
        'verified': fields.String(description='Verification date'),
        'source': fields.String(description='Data source'),
        'serialization': fields.Raw(description='Serialization data'),
        'serialized': fields.Raw(description='Serialized data'),
        'augslot1type': fields.Integer(description='Augment slot 1 type'),
        'augslot2type': fields.Integer(description='Augment slot 2 type'),
        'augslot3type': fields.Integer(description='Augment slot 3 type'),
        'augslot4type': fields.Integer(description='Augment slot 4 type'),
        'augslot5type': fields.Integer(description='Augment slot 5 type'),
        'augslot6type': fields.Integer(description='Augment slot 6 type'),
        'augslot1visible': fields.Integer(description='Augment slot 1 visibility'),
        'augslot2visible': fields.Integer(description='Augment slot 2 visibility'),
        'augslot3visible': fields.Integer(description='Augment slot 3 visibility'),
        'augslot4visible': fields.Integer(description='Augment slot 4 visibility'),
        'augslot5visible': fields.Integer(description='Augment slot 5 visibility'),
        'augslot6visible': fields.Integer(description='Augment slot 6 visibility'),
        'augtype': fields.Integer(description='Augment type'),
        'augrestrict': fields.Integer(description='Augment restrictions'),
        'augdistiller': fields.Integer(description='Augment distiller'),
        'heirloom': fields.Integer(description='Heirloom flag'),
        'favor': fields.Integer(description='Favor points'),
        'guildfavor': fields.Integer(description='Guild favor points'),
        'fvnodrop': fields.Integer(description='FV no drop flag'),
        'ldontheme': fields.Integer(description='LDON theme'),
        'ldonprice': fields.Integer(description='LDON price'),
        'ldonsold': fields.Integer(description='LDON sold flag'),
        'ldonsellbackrate': fields.Integer(description='LDON sellback rate'),
        'scriptfileid': fields.Integer(description='Script file ID'),
        'expendablearrow': fields.Integer(description='Expendable arrow flag'),
        'powersourcecapacity': fields.Integer(description='Power source capacity'),
        'bardeffect': fields.Integer(description='Bard effect'),
        'bardeffecttype': fields.Integer(description='Bard effect type'),
        'bardlevel': fields.Integer(description='Bard level'),
        'bardlevel2': fields.Integer(description='Bard level 2'),
        'bardname': fields.String(description='Bard name'),
        'bardtype': fields.Integer(description='Bard type'),
        'bardvalue': fields.Integer(description='Bard value'),
        'clickeffect': fields.Integer(description='Click effect'),
        'clicklevel': fields.Integer(description='Click level'),
        'clicklevel2': fields.Integer(description='Click level 2'),
        'clickname': fields.String(description='Click name'),
        'clicktype': fields.Integer(description='Click type'),
        'focuseffect': fields.Integer(description='Focus effect'),
        'focuslevel': fields.Integer(description='Focus level'),
        'focuslevel2': fields.Integer(description='Focus level 2'),
        'focusname': fields.String(description='Focus name'),
        'focustype': fields.Integer(description='Focus type'),
        'proceffect': fields.Integer(description='Proc effect'),
        'proclevel': fields.Integer(description='Proc level'),
        'proclevel2': fields.Integer(description='Proc level 2'),
        'procname': fields.String(description='Proc name'),
        'proctype': fields.Integer(description='Proc type'),
        'procrate': fields.Integer(description='Proc rate'),
        'worneffect': fields.Integer(description='Worn effect'),
        'wornlevel': fields.Integer(description='Worn level'),
        'wornlevel2': fields.Integer(description='Worn level 2'),
        'wornname': fields.String(description='Worn name'),
        'worntype': fields.Integer(description='Worn type'),
        'scrolleffect': fields.Integer(description='Scroll effect'),
        'scrolllevel': fields.Integer(description='Scroll level'),
        'scrolllevel2': fields.Integer(description='Scroll level 2'),
        'scrollname': fields.String(description='Scroll name'),
        'scrolltype': fields.Integer(description='Scroll type'),
        'UNK012': fields.Integer(description='Unknown field 12'),
        'UNK013': fields.Integer(description='Unknown field 13'),
        'UNK014': fields.Integer(description='Unknown field 14'),
        'UNK033': fields.Integer(description='Unknown field 33'),
        'UNK054': fields.Integer(description='Unknown field 54'),
        'UNK059': fields.Integer(description='Unknown field 59'),
        'UNK060': fields.Integer(description='Unknown field 60'),
        'UNK120': fields.Integer(description='Unknown field 120'),
        'UNK121': fields.Integer(description='Unknown field 121'),
        'UNK123': fields.Integer(description='Unknown field 123'),
        'UNK124': fields.Integer(description='Unknown field 124'),
        'UNK127': fields.Integer(description='Unknown field 127'),
        'UNK132': fields.String(description='Unknown field 132'),
        'UNK134': fields.String(description='Unknown field 134'),
        'UNK137': fields.Integer(description='Unknown field 137'),
        'UNK142': fields.Integer(description='Unknown field 142'),
        'UNK147': fields.Integer(description='Unknown field 147'),
        'UNK152': fields.Integer(description='Unknown field 152'),
        'UNK157': fields.Integer(description='Unknown field 157'),
        'UNK193': fields.Integer(description='Unknown field 193'),
        'UNK214': fields.Integer(description='Unknown field 214'),
        'UNK220': fields.Integer(description='Unknown field 220'),
        'UNK221': fields.Integer(description='Unknown field 221'),
        'UNK223': fields.Integer(description='Unknown field 223'),
        'UNK224': fields.Integer(description='Unknown field 224'),
        'UNK225': fields.Integer(description='Unknown field 225'),
        'UNK226': fields.Integer(description='Unknown field 226'),
        'UNK227': fields.Integer(description='Unknown field 227'),
        'UNK228': fields.Integer(description='Unknown field 228'),
        'UNK229': fields.Integer(description='Unknown field 229'),
        'UNK230': fields.Integer(description='Unknown field 230'),
        'UNK231': fields.Integer(description='Unknown field 231'),
        'UNK232': fields.Integer(description='Unknown field 232'),
        'UNK233': fields.Integer(description='Unknown field 233'),
        'UNK234': fields.Integer(description='Unknown field 234'),
        'UNK236': fields.Integer(description='Unknown field 236'),
        'UNK237': fields.Integer(description='Unknown field 237'),
        'UNK238': fields.Integer(description='Unknown field 238'),
        'UNK239': fields.Integer(description='Unknown field 239'),
        'UNK240': fields.Integer(description='Unknown field 240'),
        'UNK241': fields.Integer(description='Unknown field 241')
    })

    # NPC response model
    npc_model = v1.model('NPC', {
        'id': fields.Integer(description='NPC ID'),
        'name': fields.String(description='NPC name'),
        'zone': fields.String(description='Zone name'),
        'level': fields.Integer(description='NPC level'),
        'race': fields.String(description='NPC race'),
        'class': fields.String(description='NPC class')
    })

    # Spell response model
    spell_model = v1.model('Spell', {
        'id': fields.Integer(description='Spell ID'),
        'name': fields.String(description='Spell name'),
        'level': fields.Integer(description='Spell level'),
        'classes': fields.String(description='Classes that can use the spell'),
        'mana': fields.Integer(description='Mana cost'),
        'cast_time': fields.String(description='Cast time')
    })

    # Tradeskill response model
    tradeskill_model = v1.model('Tradeskill', {
        'id': fields.Integer(description='Tradeskill ID'),
        'name': fields.String(description='Tradeskill name'),
        'skill': fields.String(description='Required skill'),
        'trivial': fields.Integer(description='Trivial level'),
        'components': fields.List(fields.Raw, description='Required components')
    })

    # Loot response model
    loot_model = v1.model('Loot', {
        'id': fields.Integer(description='Loot table ID'),
        'npc_id': fields.Integer(description='NPC ID'),
        'items': fields.List(fields.Raw, description='Loot items')
    })

    models = {
        'item_model': item_model,
        'npc_model': npc_model,
        'spell_model': spell_model,
        'tradeskill_model': tradeskill_model,
        'loot_model': loot_model,
        'paginated_model': paginated_model,
        'user_model': user_model,
        'user_create_model': user_create_model,
        'user_login_model': user_login_model,
        'user_update_model': user_update_model,
        'password_change_model': password_change_model,
        'api_key_model': api_key_model,
        'api_key_create_model': api_key_create_model,
        'api_key_response_model': api_key_response_model,
        'login_response_model': login_response_model
    }

    return models

# Create models for import
models = None 