"""Utilities for EQDB"""
import os

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

here = os.path.dirname(__file__)


class ReducedItem:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


def get_zone_waypoint(short_name):
    if short_name == 'blackburrow':
        return {'y': 38, 'x': -7, 'z': 3}
    elif short_name == 'commons':
        return {'y': -127, 'x': 503, 'z': -51}
    elif short_name == 'ecommons':
        return {'y': -1603, 'x': -356, 'z': 3}
    elif short_name == 'feerrott':
        return {'y': -430, 'x': -1830, 'z': -51}
    elif short_name == 'freportw':
        return {'y': -283, 'x': -396, 'z': -23}
    elif short_name == 'grobb':
        return {'y': 223, 'x': -200, 'z': 3.75}
    elif short_name == 'everfrost':
        return {'y': 2133, 'x': -6972, 'z': -58}
    elif short_name == 'halas':
        return {'y': 26, 'x': 0, 'z': 3.75}
    elif short_name == 'highkeep':
        return {'y': -17, 'x': -1, 'z': -4}
    elif short_name == 'lavastorm':
        return {'y': 918, 'x': 1318, 'z': 119}
    elif short_name == 'neriakb':
        return {'y': 3, 'x': -493, 'z': -10}
    elif short_name == 'northkarana':
        return {'y': -688, 'x': -175, 'z': -7.5}
    elif short_name == 'eastkarana':
        return {'y': 1333, 'x': 423, 'z': 1}
    elif short_name == 'oasis':
        return {'y': 532, 'x': 110, 'z': 6}
    elif short_name == 'oggok':
        return {'y': 465, 'x': 513, 'z': 3.75}
    elif short_name == 'oot':
        return {'y': 394, 'x': -9172, 'z': 6}
    elif short_name == 'qey2hh1':
        return {'y': -3570, 'x': -14816, 'z': 36}
    elif short_name == 'qeynos2':
        return {'y': 165, 'x': 392, 'z': 4}
    elif short_name == 'qrg':
        return {'y': 45, 'x': -66, 'z': 4}
    elif short_name == 'rivervale':
        return {'y': -10, 'x': -140, 'z': 4}
    elif short_name == 'gukbottom':
        return {'y': 1157, 'x': -233, 'z': -80}
    elif short_name == 'lakerathe':
        return {'y': 2404, 'x': 2673, 'z': 95}
    elif short_name == 'southkarana':
        return {'y': -6689, 'x': 1027, 'z': 0}
    elif short_name == 'akanon':
        return {'y': 1279, 'x': -761, 'z': -24.25}
    elif short_name == 'cauldron':
        return {'y': -1790, 'x': -700, 'z': 100}
    elif short_name == 'felwithea':
        return {'y': 240, 'x': -626, 'z': -10.25}
    elif short_name == 'gfaydark':
        return {'y': 458, 'x': -385, 'z': 0}
    elif short_name == 'kaladima':
        return {'y': 90, 'x': 197, 'z': 3.75}
    elif short_name == 'mistmoore':
        return {'y': -294, 'x': 122, 'z': -179}
    elif short_name == 'erudnext':
        return {'y': -1216, 'x': -240, 'z': 52}
    elif short_name == 'hole':
        return {'y': 287, 'x': -543, 'z': -140}
    elif short_name == 'paineel':
        return {'y': 839, 'x': 210, 'z': 4}
    elif short_name == 'tox':
        return {'y': -1510, 'x': -916, 'z': -33}
    elif short_name == 'stonebrunt':
        return {'y': -4531, 'x': 673, 'z': 0}
    elif short_name == 'dulak':
        return {'y': -190, 'x': -1190, 'z': 4}
    elif short_name == 'gunthak':
        return {'y': 1402, 'x': -410, 'z': 3}
    elif short_name == 'burningwood':
        return {'y': 7407, 'x': -3876, 'z': -233}
    elif short_name == 'cabeast':
        return {'y': 969, 'x': -136, 'z': 4.68}
    elif short_name == 'citymist':
        return {'y': 249, 'x': -572, 'z': 4}
    elif short_name == 'dreadlands':
        return {'y': 3005, 'x': 9633, 'z': 1049}
    elif short_name == 'fieldofbone':
        return {'y': -1684, 'x': 1617, 'z': -55}
    elif short_name == 'firiona':
        return {'y': -2397, 'x': 1825, 'z': -98}
    elif short_name == 'frontiermtns':
        return {'y': 53, 'x': 392, 'z': -102}
    elif short_name == 'karnor':
        return {'y': 251, 'x': 160, 'z': 3.75}
    elif short_name == 'lakeofillomen':
        return {'y': 985, 'x': -1070, 'z': 78}
    elif short_name == 'overthere':
        return {'y': -2757, 'x': 1480, 'z': 11}
    elif short_name == 'skyfire':
        return {'y': -3100, 'x': 780, 'z': -158}
    elif short_name == 'timorous':
        return {'y': -12256.8, 'x': 4366.5, 'z': -278}
    elif short_name == 'trakanon':
        return {'y': -1620, 'x': -4720, 'z': -473}
    elif short_name == 'chardokb':
        return {'y': 315, 'x': -210, 'z': 1.5}
    elif short_name == 'cobaltscar':
        return {'y': -1064, 'x': -1633, 'z': 296}
    elif short_name == 'eastwastes':
        return {'y': -4037, 'x': 464, 'z': 144}
    elif short_name == 'greatdivide':
        return {'y': -6646, 'x': 3287, 'z': -35}
    elif short_name == 'iceclad':
        return {'y': 1300, 'x': 3127, 'z': 111}
    elif short_name == 'wakening':
        return {'y': 1455, 'x': 4552, 'z': -60}
    elif short_name == 'westwastes':
        return {'y': 1323, 'x': 808, 'z': -196}
    elif short_name == 'cobaltscar':
        return {'y': -1065, 'x': -1634, 'z': 299}
    elif short_name == 'sirens':
        return {'y': -590, 'x': 20, 'z': -93}
    elif short_name == 'dawnshroud':
        return {'y': -280, 'x': -1260, 'z': 97}
    elif short_name == 'fungusgrove':
        return {'y': 2398, 'x': 1359, 'z': -261}
    elif short_name == 'sharvahl':
        return {'y': 55, 'x': 250, 'z': -188}
    elif short_name == 'ssratemple':
        return {'y': 0, 'x': -6.5, 'z': 4}
    elif short_name == 'tenebrous':
        return {'y': -1514, 'x': -967, 'z': -56}
    elif short_name == 'umbral':
        return {'y': -640, 'x': 1840, 'z': 24}
    elif short_name == 'twilight':
        return {'y': 1338, 'x': -1028, 'z': 39}
    elif short_name == 'scarlet':
        return {'y': -956, 'x': -1777, 'z': -99}
    elif short_name == 'paludal':
        return {'y': -1175, 'x': 220, 'z': -236}
    elif short_name == 'bazaar':
        return {'y': -175, 'x': 105, 'z': -15}
    elif short_name == 'airplane':
        return {'y': 1560, 'x': 700, 'z': -680}
    elif short_name == 'fearplane':
        return {'y': -1305, 'x': 1065, 'z': 3}
    elif short_name == 'hateplaneb':
        return {'y': 680, 'x': -400, 'z': 4}
    elif short_name == 'poknowledge':
        return {'y': 50, 'x': -215, 'z': -160}
    elif short_name == 'potranquility':
        return {'y': -192, 'x': -8, 'z': -628}
    elif short_name == 'potimea':
        return {'y': 110, 'x': 0, 'z': 8}
    elif short_name == 'barindu':
        return {'y': -515, 'x': 210, 'z': -117}
    elif short_name == 'kodtaz':
        return {'y': -2422, 'x': 1536, 'z': -348}
    elif short_name == 'natimbi':
        return {'y': 125, 'x': -310, 'z': 520}
    elif short_name == 'qvic':
        return {'y': -1403, 'x': -1018, 'z': -490}
    elif short_name == 'txevu':
        return {'y': -20, 'x': -316, 'z': -420}
    elif short_name == 'wallofslaughter':
        return {'y': 13, 'x': -943, 'z': 130}
    else:
        return {}


def get_bane_dmg_body(num):
    """Returns the "Body Type" of a bane."""
    if num == 1:
        return 'Humanoid'
    elif num == 2:
        return 'Lycanthrope'
    elif num == 3:
        return 'Undead'
    elif num == 4:
        return 'Giant'
    elif num == 5:
        return 'Construct'
    elif num == 6:
        return 'Extraplanar'
    elif num == 7:
        return 'Monster'
    elif num == 8:
        return 'Undead Pet'
    elif num == 9:
        return 'Raid Giant'
    elif num == 10:
        return 'Raid Coldain'
    elif num == 11:
        return 'Untargetable'
    elif num == 12:
        return 'Vampyre'
    elif num == 13:
        return 'Atenha Ra'
    elif num == 14:
        return 'Greater Akheva'
    elif num == 15:
        return 'Khati Sha'
    elif num == 16:
        return 'Seru'
    elif num == 17:
        return 'Grieg Veneficus'
    elif num == 18:
        return 'Draz Nurakk'
    elif num == 19:
        return 'God'
    elif num == 20:
        return 'Luggald'
    elif num == 21:
        return 'Animal'
    elif num == 22:
        return 'Insect'
    elif num == 23:
        return 'Fire Creature'
    elif num == 24:
        return 'Elemental'
    elif num == 25:
        return 'Plant'
    elif num == 26:
        return 'Dragon'
    elif num == 27:
        return 'Summoned Creature'
    elif num == 28:
        return 'Summoned Creature 2'
    elif num == 29:
        return 'Dragon 2'
    elif num == 30:
        return 'Velious Dragon'
    elif num == 31:
        return 'Familiar'
    elif num == 32:
        return 'Dragon 3'
    elif num == 33:
        return 'Boxes'
    elif num == 34:
        return 'Muramite'
    elif num == 60:
        return 'Untargetable 2'
    elif num == 63:
        return 'Swarm Pet'
    elif num == 64:
        return 'Monster Summoning'
    elif num == 66:
        return 'Invisible Man'
    elif num == 67:
        return 'Special'
    elif num == 257:
        return 'Terris Thule'
    else:
        return f'Unknown body num {num}'


def get_bane_dmg_race(num):
    """Returns the "Race Type" of a bane."""
    if num == 12:
        return 'Gnome'
    elif num == 20:
        return 'Venril Sathir'
    elif num == 26:
        return 'Froglok'
    elif num == 39:
        return 'Gnoll'
    elif num == 40:
        return 'Goblin'
    elif num == 51:
        return 'Lizard Man'
    elif num == 54:
        return 'Orc'
    elif num == 60:
        return 'Skeleton'
    elif num == 134:
        return 'Mosquito'
    elif num == 202:
        return 'Grimling'
    elif num == 206:
        return 'Owlbear'
    elif num == 208:
        return 'Vampire'
    elif num == 215:
        return 'Tegi'
    elif num == 217:
        return 'Shissar'
    elif num == 220:
        return 'Stonegrabber'
    elif num == 230:
        return 'Akheva'
    elif num == 232:
        return 'Sonic Wolf'
    elif num == 236:
        return 'Seru'
    elif num == 356:
        return 'Chokadai'
    elif num == 392:
        return 'Ukun'
    elif num == 396:
        return 'Kyv'
    elif num == 400:
        return 'Huvul'
    elif num == 402:
        return 'Mastruq'
    elif num == 409:
        return 'Bazu'
    elif num == 410:
        return 'Feran'
    elif num == 432:
        return 'Drake'
    elif num == 456:
        return 'Sporali'
    elif num == 466:
        return 'Dark Lord'
    elif num == 520:
        return 'Bixie'
    elif num == 524:
        return 'Gnoll'
    elif num == 525:
        return 'Griffin'
    elif num == 574:
        return 'Minotaur'
    elif num == 579:
        return 'Wereorc'
    elif num == 581:
        return 'Wyvern'
    else:
        return 'Unknown Race'


def get_elem_dmg_type(num):
    """Returns the elemental damage type."""
    if num == 1:
        return 'Magic'
    elif num == 2:
        return 'Fire'
    elif num == 3:
        return 'Cold'
    elif num == 4:
        return 'Poison'
    elif num == 5:
        return 'Disease'
    elif num == 6:
        return 'Chromatic'
    elif num == 7:
        return 'Prismatic'
    elif num == 8:
        return 'Phys'
    elif num == 9:
        return 'Corruption'
    else:
        raise Exception(f'Unknown elemental type: {num}')

def translate_specials(spc):
    specials = []
    if 'E' in spc:
        specials.append('Enrages')
    if 'F' in spc:
        specials.append('Flurries')
    if 'R' in spc:
        specials.append('Rampages')
    if 'r' in spc:
        specials.append('Wild Rampages')
    if 'S' in spc:
        specials.append('Summons')
    if 'T' in spc:
        specials.append('Triple Attacks')
    if 'Q' in spc:
        specials.append('Quad Attacks')
    if 'b' in spc:
        specials.append('Bane Attacks')
    if 'm' in spc:
        specials.append('Magical Attacks')
    if 'U' in spc:
        specials.append('Immune to Slow')
    if 'C' in spc:
        specials.append('Immune to Charm')
    if 'N' in spc:
        specials.append('Immune to Stuns')
    if 'I' in spc:
        specials.append('Immune to Snare')
    if 'D' in spc:
        specials.append('Immune to Slow')
    if 'K' in spc:
        specials.append('Immune to Dispel Magic')
    if 'A' in spc:
        specials.append('Immune to Melee')
    if 'B' in spc:
        specials.append('Immune to Magic')
    if 'f' in spc:
        specials.append('Will not flee')
    if 'O' in spc:
        specials.append('Immune to non-bane Melee')
    if 'W' in spc:
        specials.append('Immune to non-magical Melee')
    if 'G' in spc:
        specials.append('Cannot be agroed')
    if 'g' in spc:
        specials.append('Belly Caster')
    if 'd' in spc:
        specials.append('Ignores Feign Death')
    if 'Y' in spc:
        specials.append('Has a Ranged Attack')
    if 'L' in spc:
        specials.append('Dual Wields')
    if 't' in spc:
        specials.append('Focused Hate')
    if 'n' in spc:
        specials.append('Does not buff/heal friends')
    if 'p' in spc:
        specials.append('Immune to Pacify')
    if 'J' in spc:
        specials.append('Leashed to combat area')
    if 'j' in spc:
        specials.append('Thetered to combat area')
    if 'o' in spc:
        specials.append('Destructible Object')
    if 'Z' in spc:
        specials.append('Immune to player damage')
    if 'i' in spc:
        specials.append('Immune to Taunt')
    if 'e' in spc:
        specials.append('Will always flee')
    if 'h' in spc:
        specials.append('Flee at low percent health')

    return specials


def get_aug_type(num):
    if num == 1:
        return '1 (Stats)'
    elif num == 2:
        return '2 (Worn)'
    elif num == 3:
        return '3 (Spells)'
    elif num == 4:
        return '4 (Proc)'
    else:
        return 'HEY IDIOT, FIX ME'


def get_class_string(num):
    """Returns the classes that can use this item."""
    out_str = ''
    if num == 65535:
        return 'ALL'
    elif num == 0:
        return 'NONE'

    while num > 0:
        if num >= 32768:
            num -= 32768
            out_str += 'BER '
        if num >= 16384:
            num -= 16384
            out_str += 'BST '
        if num >= 8192:
            num -= 8192
            out_str += 'ENC '
        if num >= 4096:
            num -= 4096
            out_str += 'MAG '
        if num >= 2048:
            num -= 2048
            out_str += 'WIZ '
        if num >= 1024:
            num -= 1024
            out_str += 'NEC '
        if num >= 512:
            num -= 512
            out_str += 'SHM '
        if num >= 256:
            num -= 256
            out_str += 'ROG '
        if num >= 128:
            num -= 128
            out_str += 'BRD '
        if num >= 64:
            num -= 64
            out_str += 'MNK '
        if num >= 32:
            num -= 32
            out_str += 'DRU '
        if num >= 16:
            num -= 16
            out_str += 'SHD '
        if num >= 8:
            num -= 8
            out_str += 'RNG '
        if num >= 4:
            num -= 4
            out_str += 'PAL '
        if num >= 2:
            num -= 2
            out_str += 'CLR '
        if num >= 1:
            num -= 1
            out_str += 'WAR '
    return out_str.strip()


def get_slot_string(num):
    """Returns the classes that can use this item."""
    out_str = ''
    if num == 0:
        return 'NONE'
    while num > 0:
        if num >= 4194304:
            num -= 4194304
            out_str += 'Ammo '
        if num >= 1048576:
            num -= 1048576
            out_str += 'Waist '
        if num >= 524288:
            num -= 524288
            out_str += 'Feet '
        if num >= 262144:
            num -= 262144
            out_str += 'Legs '
        if num >= 131072:
            num -= 131072
            out_str += 'Chest '
        if num >= 65536:
            num -= 65536
        if num >= 32768:
            num -= 32768
            out_str += 'Finger '
        if num >= 16384:
            num -= 16384
            out_str += 'Secondary '
        if num >= 8192:
            num -= 8192
            out_str += 'Primary '
        if num >= 4096:
            num -= 4096
            out_str += 'Hands '
        if num >= 2048:
            num -= 2048
            out_str += 'Range '
        if num >= 1024:
            num -= 1024
        if num >= 512:
            num -= 512
            out_str += 'Wrist '
        if num >= 256:
            num -= 256
            out_str += 'Back '
        if num >= 128:
            num -= 128
            out_str += 'Arms '
        if num >= 64:
            num -= 64
            out_str += 'Shoulders '
        if num >= 32:
            num -= 32
            out_str += 'Neck '
        if num >= 16:
            num -= 16
        if num >= 8:
            num -= 8
            out_str += 'Face '
        if num >= 4:
            num -= 4
            out_str += 'Head '
        if num >= 2:
            num -= 2
            out_str += 'Ear '
        if num >= 1:
            num -= 1
            out_str += 'Charm '
    return out_str.strip()


def get_type_string(num):
    """Returns the appropriate item type based on id number."""
    if num == 0:
        return '1H Slashing'
    elif num == 1:
        return '2H Slashing'
    elif num == 2:
        return '1H Piercing'
    elif num == 3:
        return '1H Blunt'
    elif num == 4:
        return '2H Blunt'
    elif num == 35:
        return '2H Piercing'
    elif num == 27:
        return 'Arrow'
    elif num == 5:
        return 'Archery'
    elif num == 45:
        return 'Hand to Hand'
    elif num == 8:
        return 'Shield'
    else:
        return '__na__'


def lookup_class(name):
    if 'None' in name:
        return 0
    if 'Warrior' in name:
        return 1
    elif 'Cleric' in name:
        return 2
    elif 'Paladin' in name:
        return 4
    elif 'Ranger' in name:
        return 8
    elif 'Shadow Knight' in name:
        return 16
    elif 'Druid' in name:
        return 32
    elif 'Monk' in name:
        return 64
    elif 'Bard' in name:
        return 128
    elif 'Rogue' in name:
        return 256
    elif 'Shaman' in name:
        return 512
    elif 'Necromancer' in name:
        return 1024
    elif 'Wizard' in name:
        return 2048
    elif 'Magician' in name:
        return 4096
    elif 'Enchanter' in name:
        return 8192
    elif 'Beastlord' in name:
        return 16384
    elif 'Berserker' in name:
        return 32768


def lookup_weapon_types(name):
    if 'One Hand Slash' in name:
        return 0
    elif 'Two Hand Slash' in name:
        return 1
    elif 'One Hand Piercing' in name:
        return 2
    elif 'One Hand Blunt' in name:
        return 3
    elif 'Two Hand Blunt' in name:
        return 4
    elif 'Two Hand Piercing' in name:
        return 35
    elif 'Arrow' in name:
        return 27
    elif 'Bow' in name:
        return 5
    elif 'Hand to Hand' in name:
        return 45
    elif 'Shield' in name:
        return 8
    else:
        return 10


def get_stat_weights(weights, item, bane_body=None):
    """Helper to calculate and return stat weights."""
    value = 0
    for weight in weights:
        # Fix the resist weights by adding their heroic counterpart

        if weight == 'pr':
            value += (item.pr + item.heroic_pr) * weights[weight]
        elif weight == 'mr':
            value += (item.mr + item.heroic_mr) * weights[weight]
        elif weight == 'cr':
            value += (item.cr + item.heroic_cr) * weights[weight]
        elif weight == 'dr':
            value += (item.dr + item.heroic_dr) * weights[weight]
        elif weight == 'fr':
            value += (item.fr + item.heroic_fr) * weights[weight]
        elif weight == 'w_eff':
            if not item.delay or item.delay == 0:
                continue
            value += round((item.damage / item.delay), 2) * weights[weight]
        elif 'bane_damage' in weight:
            if bane_body:
                value += item.banedmgamt * weights[weight]
            else:
                value += item.banedmgraceamt * weights[weight]
        else:
            value += getattr(item, weight) * weights[weight]
    return value


def fix_npc_name(name):
    """Helper to fix names to readible standards"""
    if name.startswith('#'):
        name = name[1:]
    name = name.replace('_', ' ')
    return name.strip()


def lookup_slot(name):
    if 'Charm' in name:
        return 1
    elif 'Ear' in name:
        return 2
    elif 'Head' in name:
        return 4
    elif 'Face' in name:
        return 8
    elif 'Neck' in name:
        return 32
    elif 'Shoulders' in name:
        return 64
    elif 'Arms' in name:
        return 128
    elif 'Back' in name:
        return 256
    elif 'Wrist' in name:
        return 512
    elif 'Range' in name:
        return 2048
    elif 'Hands' in name:
        return 4096
    elif 'Primary' in name:
        return 8192
    elif 'Secondary' in name:
        return 16384
    elif 'Finger' in name:
        return 32768
    elif 'Chest' in name:
        return 131072
    elif 'Legs' in name:
        return 262144
    elif 'Feet' in name:
        return 524288
    elif 'Waist' in name:
        return 1048576
    elif 'Ammo' in name:
        return 2097152
    else:
        raise Exception(f'Unknown slot name: {name}.')


def get_focus_values(focus_type, sub_type, engine, SpellsNewReference):
    with Session(bind=engine) as session:
        ret_ids = []
        # "All" queries
        ignore_effects = []
        for i in range(2, 13):
            ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([137, 138]))
        ignore_params = and_(*ignore_effects)
        all_haste_query = session.query(SpellsNewReference.id).\
            filter(SpellsNewReference.effectid1 == 127).\
            filter(SpellsNewReference.effect_base_value1 > 0).\
            filter(ignore_params).\
            order_by(SpellsNewReference.id)

        all_range_query = session.query(SpellsNewReference.id).\
            filter(SpellsNewReference.effectid1 == 129).\
            filter(SpellsNewReference.effect_base_value1 > 0).\
            filter(ignore_params).\
            order_by(SpellsNewReference.id)

        add_effects = []
        ignore_effects = []
        for i in range(2, 13):
            add_effects.append(getattr(SpellsNewReference, f'effectid{i}').in_([139]))
            ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([138]))
        add_params = or_(*add_effects)
        ignore_params = and_(*ignore_effects)
        all_pres_query = session.query(SpellsNewReference.id).\
            filter(SpellsNewReference.effectid1 == 132).\
            filter(SpellsNewReference.effect_base_value1 > 0).\
            filter(ignore_params).\
            filter(add_params).\
            order_by(SpellsNewReference.id)

        if focus_type == 'Beneficial':
            add_effects = []
            for i in range(2, 13):
                add_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 138,
                                        getattr(SpellsNewReference, f'effect_base_value{i}') == 1))
            add_params = or_(*add_effects)

            if sub_type == 'Preservation':
                all_ids = all_pres_query.all()
                for entry in all_ids:
                    ret_ids.append(entry[0])

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 132). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Range':
                all_ids = all_range_query.all()
                for entry in all_ids:
                    ret_ids.append(entry[0])

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 129). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Haste':
                all_ids = all_haste_query.all()
                for entry in all_ids:
                    ret_ids.append(entry[0])

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 127). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Duration':
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 128). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Healing':
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 125). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            else:
                raise f'Unknown subtype: {sub_type}'
        elif focus_type == 'Detrimental':
            add_effects = []
            for i in range(2, 13):
                add_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 138,
                                        getattr(SpellsNewReference, f'effect_base_value{i}') == 0))
            add_params = or_(*add_effects)
            if sub_type == 'Preservation':
                all_ids = all_pres_query.all()
                for entry in all_ids:
                    ret_ids.append(entry[0])

                ignore_effects = []
                for i in range(2, 13):
                    ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([138]))
                ignore_params = and_(*ignore_effects)

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 132). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    filter(ignore_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Range':
                all_ids = all_range_query.all()
                for entry in all_ids:
                    ret_ids.append(entry[0])

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 129). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Haste':
                all_ids = all_haste_query.all()
                for entry in all_ids:
                    ret_ids.append(entry[0])

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 127). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Duration':
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 128). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Damage (All)':
                ignore_effects = []
                for i in range(2, 13):
                    ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([135, 140]))
                ignore_params = and_(*ignore_effects)

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 124). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    filter(ignore_params). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Damage (Fire)':
                ignore_effects = []
                type_effects = []
                for i in range(2, 13):
                    ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([140]))
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 135,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 2))
                ignore_params = and_(*ignore_effects)
                type_effects = or_(*type_effects)

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 124). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    filter(ignore_params). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Damage (Cold)':
                ignore_effects = []
                type_effects = []
                for i in range(2, 13):
                    ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([140]))
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 135,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 3))
                ignore_params = and_(*ignore_effects)
                type_effects = or_(*type_effects)

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 124). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    filter(ignore_params). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Damage (Magic)':
                ignore_effects = []
                type_effects = []
                for i in range(2, 13):
                    ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([140]))
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 135,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 1))
                ignore_params = and_(*ignore_effects)
                type_effects = or_(*type_effects)

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 124). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    filter(ignore_params). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Damage (Poison)':
                ignore_effects = []
                type_effects = []
                for i in range(2, 13):
                    ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([140]))
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 135,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 4))
                ignore_params = and_(*ignore_effects)
                type_effects = or_(*type_effects)

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 124). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    filter(ignore_params). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Damage (Disease)':
                ignore_effects = []
                type_effects = []
                for i in range(2, 13):
                    ignore_effects.append(getattr(SpellsNewReference, f'effectid{i}').not_in([140]))
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 135,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 5))
                ignore_params = and_(*ignore_effects)
                type_effects = or_(*type_effects)

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 124). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    filter(ignore_params). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Damage (DoT)':
                type_effects = []
                for i in range(2, 13):
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 140,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') >= 4))
                type_effects = or_(*type_effects)

                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 124). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(add_params). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            else:
                raise f'Unknown subtype: {sub_type}'
        elif focus_type == 'Pet':
            if sub_type == 'Pet Power':
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 167). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            else:
                raise f'Unknown subtype: {sub_type}'
        elif focus_type == 'Melee':
            if sub_type == 'Ferocity':
                return [3886, 3887, 3888, 6323, 6324, 7835, 9615, 15841, 20517]
            elif sub_type == 'Cleave':
                return [3883, 3884, 3885, 6321, 6322, 7834, 9614, 15840, 20516]
            elif sub_type == 'Dodging':
                return [3889, 3890, 3891, 7832, 9612, 15838, 20514]
            elif sub_type == 'Parry':
                return [3892, 3893, 3894, 6327, 6328, 6329, 7833, 7837, 9613, 9617, 15839, 20515]
            elif sub_type == 'Sharpshooting':
                return [3896, 3897, 3898, 6325, 6326, 7836, 9616, 15842, 20518]
            else:
                raise f'Unknown subtype: {sub_type}'
        elif focus_type == 'Bard':
            if sub_type == 'Wind':
                type_effects = []
                for i in range(2, 13):
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 414,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 54))
                type_effects = or_(*type_effects)
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 413). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Stringed':
                type_effects = []
                for i in range(2, 13):
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 414,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 49))
                type_effects = or_(*type_effects)
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 413). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Brass':
                type_effects = []
                for i in range(2, 13):
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 414,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 12))
                type_effects = or_(*type_effects)
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 413). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Percussion':
                type_effects = []
                for i in range(2, 13):
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 414,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 70))
                type_effects = or_(*type_effects)
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 413). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            elif sub_type == 'Singing':
                type_effects = []
                for i in range(2, 13):
                    type_effects.append(and_(getattr(SpellsNewReference, f'effectid{i}') == 414,
                                             getattr(SpellsNewReference, f'effect_base_value{i}') == 41))
                type_effects = or_(*type_effects)
                query = session.query(SpellsNewReference.id). \
                    filter(SpellsNewReference.effectid1 == 413). \
                    filter(SpellsNewReference.effect_base_value1 > 0). \
                    filter(type_effects). \
                    order_by(SpellsNewReference.id)
                ids = query.all()
                for entry in ids:
                    ret_ids.append(entry[0])
                return ret_ids
            else:
                raise Exception(f'Unknown sub_type: {sub_type}')
        else:
            raise Exception(f'Unknown focus type: {focus_type}')


def get_map_data(short_name):
    lines = []
    if short_name == 'Unknown':
        return lines
    with open(os.path.join(here, 'maps', f'{short_name}.txt'), 'r') as fh:
        data = fh.read()
        for line in data.split('\n'):
            if line.startswith('L'):
                split_line = line.split()
                lines.append({'x1': float(split_line[1].strip(',')),
                              'y1': float(split_line[2].strip(',')),
                              'z1': float(split_line[3].strip(',')),
                              'x2': float(split_line[4].strip(',')),
                              'y2': float(split_line[5].strip(',')),
                              'z2': float(split_line[6].strip(',')),
                              'rgb': f'{split_line[7].strip(",")}, {split_line[8].strip(",")}, {split_line[9].strip(",")}'})
    return lines


def parse_skill(skill_num):
    if skill_num == 0:
        return '1H Blunt'
    elif skill_num == 1:
        return '1H Slashing'
    elif skill_num == 2:
        return '2H Blunt'
    elif skill_num == 3:
        return '2H Slashing'
    elif skill_num == 4:
        return 'Abjuration'
    elif skill_num == 5:
        return 'Alteration'
    elif skill_num == 6:
        return 'Apply Poison'
    elif skill_num == 7:
        return 'Archery'
    elif skill_num == 8:
        return 'Backstab'
    elif skill_num == 9:
        return 'Bind Wounds'
    elif skill_num == 10:
        return 'Bash'
    elif skill_num == 11:
        return 'Block'
    elif skill_num == 13:
        return 'Channeling'
    elif skill_num == 14:
        return 'Conjuration'
    elif skill_num == 15:
        return 'Defense'
    elif skill_num == 17:
        return 'Disarm Traps'
    elif skill_num == 18:
        return 'Divination'
    elif skill_num == 19:
        return 'Dodge'
    elif skill_num == 22:
        return 'Dual Wield'
    elif skill_num == 24:
        return 'Evocation'
    elif skill_num == 27:
        return 'Forage'
    elif skill_num == 28:
        return 'Hand to Hand'
    elif skill_num == 29:
        return 'Hide'
    elif skill_num == 30:
        return 'Kick'
    elif skill_num == 31:
        return 'Meditate'
    elif skill_num == 32:
        return 'Mend'
    elif skill_num == 35:
        return 'Pick Locks'
    elif skill_num == 36:
        return 'Piercing'
    elif skill_num == 37:
        return 'Riposte'
    elif skill_num == 39:
        return 'Safe Fall'
    elif skill_num == 40:
        return 'Sense Heading'
    elif skill_num == 42:
        return 'Sneak'
    elif skill_num == 43:
        return 'Specialize Abjuration'
    elif skill_num == 44:
        return 'Specialize Alteration'
    elif skill_num == 45:
        return 'Specialize Conjuration'
    elif skill_num == 46:
        return 'Specialize Divination'
    elif skill_num == 47:
        return 'Specialize Evocation'
    elif skill_num == 50:
        return 'Swimming'
    elif skill_num == 51:
        return 'Throwing'
    elif skill_num == 53:
        return 'Tracking'
    elif skill_num == 55:
        return 'Fishing'
    elif skill_num == 56:
        return 'Poison Making'
    elif skill_num == 57:
        return 'Tinkering'
    elif skill_num == 58:
        return 'Research'
    elif skill_num == 59:
        return 'Alchemy'
    elif skill_num == 60:
        return 'Baking'
    elif skill_num == 61:
        return 'Tailoring'
    elif skill_num == 63:
        return 'Blacksmithing'
    elif skill_num == 64:
        return 'Fletching'
    elif skill_num == 65:
        return 'Brewing'
    elif skill_num == 66:
        return 'Alcohol Tolerance'
    elif skill_num == 68:
        return 'Jewel Crafting'
    elif skill_num == 69:
        return 'Pottery'
    elif skill_num == 71:
        return 'Intimidate'
    elif skill_num == 73:
        return 'Taunt'
    elif skill_num == 75:
        return 'Non-Tradeskill'
    elif skill_num == 255:
        return 'none'
    else:
        return 'Unknown skill'


def get_object_type(obj_id):
    if obj_id == 10:
        return 'Tool Box'
    elif obj_id == 11:
        return 'Research'
    elif obj_id == 12:
        return 'Mortar'
    elif obj_id == 13:
        return 'Self Dusting'
    elif obj_id == 14:
        return 'Baking'
    elif obj_id == 15:
        return 'Baking'
    elif obj_id == 16:
        return 'Tailoring'
    elif obj_id == 17:
        return 'Forge'
    elif obj_id == 18:
        return 'Fletching'
    elif obj_id == 19:
        return 'Brew Barrel'
    elif obj_id == 20:
        return 'Jewelcraft'
    elif obj_id == 21:
        return 'Pottery Wheel'
    elif obj_id == 22:
        return 'Pottery Kiln'
    elif obj_id == 24:
        return 'Wizard Only Research'
    elif obj_id == 25:
        return 'Mage Only Research'
    elif obj_id == 26:
        return 'Necromancer Only Research'
    elif obj_id == 27:
        return 'Enchanter Only Research'
    elif obj_id == 28:
        return 'Class/Race Limited'
    elif obj_id == 29:
        return 'Class/Race Limited'
    elif obj_id == 30:
        return 'Always Works'
    elif obj_id == 31:
        return 'High Elf Forge'
    elif obj_id == 32:
        return 'Dark Elf Forge'
    elif obj_id == 33:
        return 'Ogre Forge'
    elif obj_id == 34:
        return 'Dwarven Forge'
    elif obj_id == 35:
        return 'Gnome Forge'
    elif obj_id == 36:
        return 'Barbarian Forge'
    elif obj_id == 38:
        return 'Iksar Forge'
    elif obj_id == 39:
        return 'Human Forge'
    elif obj_id == 40:
        return 'Human Forge'
    elif obj_id == 41:
        return 'Halfling Tailoring Kit'
    elif obj_id == 42:
        return 'Erudite Tailoring Kit'
    elif obj_id == 43:
        return 'Wood Elf Tailoring Kit'
    elif obj_id == 44:
        return 'Wood Elf Fletching Kit'
    elif obj_id == 45:
        return 'Iksar Pottery Wheel'
    elif obj_id == 47:
        return 'Troll Forge'
    elif obj_id == 48:
        return 'Wood Elf Forge'
    elif obj_id == 49:
        return 'Halfling Forge'
    elif obj_id == 50:
        return 'Erudite Forge'
    elif obj_id == 53:
        return 'Augment'
    else:
        raise NotImplementedError(f'Unknown object id: {obj_id}')


def get_era_zones(era_name):
    if era_name == 'Classic':
        return [48, 55, 36, 17, 68, 58, 70, 22, 10, 15, 98, 24, 30, 16, 52, 29, 6, 5, 46, 64, 74, 20, 51, 33, 32,
                44, 42, 41, 40, 8, 67, 2, 34, 61, 37, 69, 49, 75, 76, 19, 31, 60, 1, 35, 62, 56, 77, 59, 65, 23,
                63, 47, 54, 39, 18, 27, 57, 11, 13, 73, 72, 186, 71, 45, 4, 50, 66, 14, 3, 12, 38, 21, 9, 25]
    elif era_name == 'Kunark':
        return [106, 82, 103, 84, 92, 88, 102, 97, 85, 87, 90, 104, 86, 94, 78, 105, 107, 93, 89, 91, 83, 81, 80,
                79, 96, 95, 108, 277, 225, 228, 227, 224, 226]
    elif era_name == 'LoY':
        return [277, 225, 228, 227, 224, 226]
    elif era_name == 'Velious':
        return [117, 123, 116, 129, 113, 125, 114, 115, 121, 118, 110, 127, 126, 128, 100, 124, 111, 119, 101, 120,
                109, 112]
    elif era_name == 'Luclin':
        return [163, 167, 166, 160, 168, 169, 161, 152, 159, 165, 150, 162, 154, 179, 155, 174, 164, 153, 157,
                171, 173, 156, 175, 172, 170, 176, 158]
    elif era_name == 'Planes':
        return [181, 278, 209, 214, 213, 200, 211, 221, 215, 205, 218, 222, 217, 206, 201, 202, 204, 210, 219, 223,
                203, 208, 216, 220, 212, 207]
    elif era_name == 'LDoN':
        return [264, 239, 229, 254, 259, 249, 244, 237, 275, 262, 247, 232, 242, 268, 263, 248, 238, 233, 272, 276,
                258, 253, 243, 270, 261, 274, 251, 246, 256, 236, 231, 266, 241, 234, 257, 252, 267, 269, 273, 265,
                230, 250, 255, 235, 260, 245, 240, 271]
    elif era_name == 'GoD':
        return [283, 284, 294, 296, 293, 280, 281, 295, 299, 282, 288, 286, 285, 287, 298, 279, 998, 289, 297, 292,
                290, 291]
    elif era_name == 'OoW':
        return [317, 328, 329, 330, 318, 319, 320, 302, 335, 304, 305, 306, 307, 308, 309, 316, 303, 334, 331, 332,
                333, 301, 336, 300]
    elif era_name == 'DoN':
        return [345, 344, 341, 339, 338, 346, 337, 343, 340, 342]
    elif era_name == 'DoDH':
        return [360, 359, 365, 367, 351, 348, 361, 357, 347, 364, 368, 363, 366, 358, 349, 356, 355, 354, 350, 362]
    elif era_name == 'PoR':
        return [385, 369, 388, 389, 381, 382, 387, 384, 391, 392, 375, 370, 376, 371, 393, 374, 386, 372, 378, 377,
                373, 380, 390, 379, 383]
    elif era_name == 'TSS':
        return [406, 411, 398, 395, 394, 405, 402, 397, 412, 407, 400, 410, 396, 403, 408, 413, 415, 409, 399, 414,
                401, 404]
    elif era_name == 'TBS':
        return [422, 428, 427, 424, 418, 416, 429, 425, 430, 420, 421, 426, 417, 423, 435, 431, 432, 433, 434, 419]
    elif era_name == 'SoF':
        return [445, 449, 446, 451, 442, 436, 440, 441, 444, 443, 437, 439, 447, 438, 448]
    elif era_name == 'SoD':
        return [468, 456, 471, 474, 452, 458, 454, 453, 470, 476, 455, 466, 467, 472, 457, 477, 469, 473, 459, 460, 461,
                462, 463, 464, 465, 475]
    elif era_name == 'UF':
        return [485, 492, 480, 490, 481, 484, 495, 487, 488, 491, 483, 486, 482, 489, 493, 494]
    elif era_name == 'HoT':
        return [709, 706, 711, 701, 702, 710, 707, 708, 712, 700, 703, 704, 705]
    elif era_name == 'VoA':
        return [724, 728, 732, 730, 727, 726, 734, 733, 735, 729, 725, 731]
    elif era_name == 'RoF':
        return [760, 755, 758, 759, 754, 752, 757, 756, 753]
    else:
        raise Exception(f'Unknown era: {era_name}')


def lookup_zone_name(item_id):
    if item_id == -1:
        return 'Quest'
    if item_id == -2:
        return 'Tradeskill'
    zone_id = int(int(item_id) / 1000)
    with open(os.path.join(here, 'item_files/zonelist.txt'), 'r') as fh:
        zone_list = fh.read()
    for line in zone_list.split('\n'):
        if f'{zone_id}\t' in line:
            return line.split(str(zone_id))[1].strip()


def check_sympathetic(name):
    if 'Sympathetic Strike' in name:
        split_name = name.split('of Flames')
        return f'{split_name[0]}{split_name[1]}'
    elif 'Sympathetic Healing' in name:
        split_name = name.split('Burst')
        return f'{split_name[0]}{split_name[1]}'
    else:
        return name


def get_era_name(era_id):
    if era_id == 0:
        return 'Classic'
    elif era_id == 1:
        return "Ruins of Kunark"
    elif era_id == 2:
        return "Scars of Velious"
    elif era_id == 3:
        return "Shadows of Luclin"
    elif era_id == 4:
        return "Planes of Power"
    elif era_id == 5:
        return "Legacy of Ykesha"
    elif era_id == 6:
        return "Lost Dungeons of Norrath"
    elif era_id == 7:
        return "Gates of Discord"
    elif era_id == 8:
        return "Omens of War"
    elif era_id == 9:
        return "Dragons of Norrath"
    elif era_id == 10:
        return "Depths of Darkhollow"
    elif era_id == 11:
        return "Prophecy of Ro"
    elif era_id == 12:
        return "The Serpents Spine"
    elif era_id == 13:
        return "The Buried Sea"
    elif era_id == 14:
        return "Secrets of Faydwer"
    elif era_id == 15:
        return "Seeds of Destruction"
    elif era_id == 16:
        return "Underfoot"
    elif era_id == 17:
        return "House of Thule"
    elif era_id == 18:
        return "Veil of Alaris"
    elif era_id == 19:
        return "Rain of Fear"
    else:
        return "Unknown Era"


def get_era_id(name):
    if name == 'Classic':
        return 0
    elif name == 'Kunark':
        return 1
    elif name == 'Velious':
        return 2
    elif name == 'Luclin':
        return 3
    elif name == 'Planes':
        return 4
    elif name == 'Ykesha':
        return 5
    elif name == 'LDoN':
        return 6
    elif name == 'GoD':
        return 7
    elif name == 'OoW':
        return 8
    elif name == 'DoN':
        return 9
    elif name == 'DoDH':
        return 10
    elif name == 'PoR':
        return 11
    elif name == 'TSS':
        return 12
    elif name == 'TBS':
        return 13
    elif name == 'SoF':
        return 14
    elif name == 'SoD':
        return 15
    elif name == 'UF':
        return 16
    elif name == 'HoT':
        return 17
    elif name == 'VoA':
        return 18
    elif name == 'RoF':
        return 19
    elif name == 'CoTF':
        return 20
    elif name == 'TDS':
        return 21
    elif name == 'TBM':
        return 22
    elif name == 'EoK':
        return 23
    elif name == 'RoS':
        return 24
    elif name == 'TBL':
        return 25
    elif name == 'ToV':
        return 26
    elif name == 'CoV':
        return 27
    elif name == 'ToL':
        return 28
    elif name == 'NoS':
        return 29
    elif name == 'LS':
        return 30
    elif name == 'TOB':
        return 31
    elif name == 'Unknown':
        return 999
    else:
        raise Exception(f'Unknown era name {name}')
