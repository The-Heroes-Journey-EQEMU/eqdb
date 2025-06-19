from db.item import ItemDB
from db.npc import NPCDB
from db.spell import SpellDB
from db.zone import ZoneDB
from db.tradeskill import TradeskillDB
from db.quest import QuestDB

# Initialize database connections
item = ItemDB()
npc = NPCDB()
spell = SpellDB()
zone = ZoneDB()
tradeskill = TradeskillDB()
quest = QuestDB() 