from api.db.item import ItemDB
from api.db.spell import SpellDB
from api.db.npc import NPCDB
from api.db.zone import ZoneDB
from api.db.tradeskill import TradeskillDB
from api.db.quest import QuestDB
from api.db.expansion import ExpansionDB
from api.db.expansion_items import ExpansionItemsDB

# Initialize database connections
item = ItemDB()
npc = NPCDB()
spell = SpellDB()
zone = ZoneDB()
tradeskill = TradeskillDB()
quest = QuestDB() 