# coding: utf8

import tcod
from bearlibterminal import terminal as blt
import math
import textwrap
import shelve
import random
import os
import copy
import dungeon
import vaults
import caves
import stair_vaults
import quest_vaults
import special_vaults
import red_outpost
import vierfort
import north_warren
import mirefield_keep
import beggars_hole
import black_hollow
import cindemere
import overworld
import quests as master_quests
import encounters
#import dbhash
#import anydbm
import sys
from PIL import Image
 
#actual size of the window
SCREEN_WIDTH = 135
SCREEN_HEIGHT = 90
 
#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 60

#size of view for map scrolling
VIEW_WIDTH = 105
VIEW_HEIGHT = 70

MINIMAP_OFFSET = 4
MINIMAP_FLAG = True #lets me turn off minimap for local testing - should be True for release
STARTING_EXPLORED = False #again for testing, allows for fully explored maps - should be False for release
SHOW_ALL_OBJECTS = False #for testing, shows every object on map - should be False for release
 
ANIMATION_FRAMES = 25
 
#sizes and coordinates relevant for the GUI
PANEL_HEIGHT = SCREEN_HEIGHT - VIEW_HEIGHT
BAR_WIDTH = SCREEN_WIDTH - VIEW_WIDTH
BAR_HEIGHT = SCREEN_HEIGHT - PANEL_HEIGHT
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
SIDE_X = SCREEN_WIDTH - BAR_WIDTH
MSG_X = 1
MSG_WIDTH = SCREEN_WIDTH - 25
MSG_HEIGHT = PANEL_HEIGHT - 4
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40
 
#vault map generation constants
VAULT_SIZE = 20
 
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True	#light walls or not
SIGHT_RANGE = 30
 
LIMIT_FPS = 20	#20 frames-per-second maximum
 
wall_char = [int("0xE018", 16), int("0xE019", 16), int("0xE020", 16), int("0xE021", 16), int("0xE022", 16), int("0xE023", 16), int("0xE024", 16), int("0xE025", 16), int("0xE026", 16), int("0xE027", 16), int("0xE028", 16), int("0xE029", 16), int("0xE030", 16), int("0xE031", 16), int("0xE032", 16), int("0xE033", 16),int("0xE018", 16), int("0xE019", 16), int("0xE020", 16), int("0xE021", 16), int("0xE023", 16), int("0xE024", 16)]

town_wall_char = [int("0xE034", 16), int("0xE035", 16), int("0xE036", 16), int("0xE037", 16)]

red_wall_char = [int("0xE038", 16), int("0xE039", 16), int("0xE040", 16), int("0xE041", 16), int("0xE038", 16), int("0xE039", 16), int("0xE040", 16), int("0xE041", 16), int("0xE038", 16), int("0xE039", 16), int("0xE040", 16), int("0xE041", 16), int("0xE042", 16), int("0xE043", 16), int("0xE044", 16), int("0xE045", 16), int("0xE046", 16), int("0xE047", 16)]

tree_char = [int("0xE049", 16), int("0xE050", 16)]

mountain_char = [int("0xE051", 16), int("0xE052", 16), int("0xE053", 16), int("0xE054", 16)]

water_char = [int("0xE055", 16), int("0xE056", 16)]

shrub_char = [int("0xE057", 16), int("0xE058", 16)]

ground_char = [int("0xE059", 16), int("0xE060", 16), int("0xE061", 16)]

grass_char = [int("0xE062", 16), int("0xE063", 16), int("0xE064", 16)]

indoor_char = [int("0xE065", 16)]

castle_char = int("0xE066", 16)
village_char = int("0xE067", 16)
cave_char = int("0xE068", 16)
 
light_wall_char = int("0xE001", 16)
dark_wall_char = int("0xE002", 16)
light_ground_char = int("0xE003", 16)
dark_ground_char = int("0xE004", 16)
closed_door_char = int("0xE005", 16)
open_door_char = int("0xE006", 16)
stairs_down_char = int("0xE007", 16)
stairs_up_char = int("0xE008", 16)
torch_wall_char = int("0xE048", 16)
 
colour_dark_wall = "darkest grey"
colour_dark_ground = "black"
colour_light_wall = "darker flame"
colour_light_ground = "darker orange"
colour_darkvision_wall = "light grey"
colour_darkvision_ground = "darkest grey"
colour_light_grass = "dark green"

METAL_WEAPON_COLOUR = "sky"
OTHER_WEAPON_COLOUR = "darker orange"
METAL_ARMOUR_COLOUR = "sky"
OTHER_ARMOUR_COLOUR = "darker orange"
MISC_COLOUR = "yellow"
 
ABILITY_MODIFIER = {1: -5, 2: -4, 3: -4, 4: -3, 5: -3, 6: -2, 7: -2, 8: -1, 9: -1, 10: 0, 11: 0, 12: 1, 13: 1, 14: 2, 15: 2, 16: 3, 17: 3, 18: 4, 19: 4, 20: 5, 21: 5, 22: 6, 23: 6, 24: 7, 25: 7, 26: 8, 27: 8, 28: 9, 29: 9, 30: 10}

PROFICIENCY_BONUS = {1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8:3, 9: 4, 10: 4, 11: 4, 12: 4, 13: 5, 14: 5, 15: 5, 16: 5, 17: 6, 18: 6, 19: 6, 20: 6}

XP_TO_LEVEL = {1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000}

PLAYER_STARTING_XP = 0
PLAYER_XP_MODIFER = 0.5
STARTING_DUNGEON_LEVEL = 1
STARTING_DUNGEON_BRANCH = 'overworld'

LEVEL_CAP = 10

SNEAK_ATTACK_MODIFIER = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5, 11: 6, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 9, 18: 9, 19: 10, 20: 10}

STARTING_LEVEL_TO_CR = 3 #this will make the first dungeon level easy apart from special vault monsters
DUNGEON_LEVEL_TO_CR = 2 #factor of what CR monsters can appear on dungeon levels, ie. 2 means that on dlevel 1, the max CR is 0.5
NPC_LEVEL_TO_CR = 3 #factor of what CR NPC's appear on certain levels

MONSTER_CR = {'adult_red_dragon': 17, 'air_elemental': 5, 'allosaurus': 2, 'animated_armour': 1, 'ankylosaurus': 3, 'ape': 0.5, 'awakened_shrub': 0, 'awakened_tree': 2, 'axe_beak': 0.25, 'baboon': 0, 'badger': 0, 'banshee': 4, 'bat': 0, 'basilisk': 3, 'black_bear': 0.5, 'blink_dog': 0.25, 'blood_hawk': 0.25, 'boar': 0.25, 'brown_bear': 1, 'bugbear': 1, 'camel': 0.125, 'cat': 0, 'centaur': 2, 'chimera': 6, 'cockatrice': 0.5, 'constrictor_snake': 0.25, 'crab': 0, 'crocodile': 0.5, 'cyclops': 6, 'death_dog': 1, 'deer': 0, 'dire_wolf': 1, 'doppelganger': 3, 'draft_horse': 0.25, 'eagle': 0, 'earth_elemental': 5, 'elephant': 4, 'elk': 0.25, 'fire_elemental': 5, 'fire_giant': 9, 'flameskull': 4, 'flesh_golem': 5, 'flying_snake': 0.125, 'flying_sword': 0.25, 'frog': 0, 'frost_giant': 8, 'gargoyle': 2, 'ghost': 4, 'ghoul': 1, 'giant_ape': 7, 'giant_badger': 0.25, 'giant_bat': 0.25, 'giant_boar': 2, 'giant_centipede': 0.25, 'giant_constrictor_snake': 2, 'giant_crab': 0.125, 'giant_crocodile': 5, 'giant_eagle': 1, 'giant_elk': 2, 'giant_fire_beetle': 0, 'giant_frog': 0.25, 'giant_goat': 0.5, 'giant_hyena': 1, 'giant_lizard': 0.25, 'giant_octopus': 1, 'giant_owl': 0.25, 'giant_poisonous_snake': 0.25, 'giant_rat': 0.125, 'giant_scorpion': 3, 'giant_sea_horse': 0.5, 'giant_shark': 5, 'giant_spider': 1, 'giant_toad': 1, 'giant_vulture': 1, 'giant_wasp': 0.5, 'giant_weasel': 0.125, 'giant_wolf_spider': 0.25, 'gnoll': 0.5, 'goat': 0, 'goblin': 0.25, 'grick': 2, 'griffon': 2, 'harpy': 1, 'hawk': 0, 'hell_hound': 3, 'hill_giant': 5, 'hippogriff': 1, 'hobgoblin': 0.5, 'hunter_shark': 2, 'hydra': 8, 'hyena': 0, 'jackal': 0, 'killer_whale': 3, 'kobold': 0.25, 'lion': 1, 'lizard': 0, 'lizardfolk': 0.5, 'mammoth': 6, 'manticore': 3, 'mastiff': 0.25, 'medusa': 6, 'merfolk': 0.125, 'minotaur': 3, 'mule': 0.125, 'mummy': 3, 'nothic': 2, 'ochre_jelly': 2, 'octopus': 0, 'ogre': 2, 'orc': 0.5, 'owl': 0, 'owlbear': 3, 'panther': 0.25, 'pegasus': 2, 'phase_spider': 3, 'plesiosaurus': 2, 'poisonous_snake': 0.125, 'polar_bear': 2, 'pony': 0.125, 'pteranodon': 0.25, 'quipper': 0, 'rat': 0, 'raven': 0, 'reef_shark': 0.5, 'rhinoceros': 2, 'riding_horse': 0.25, 'sabre_toothed_tiger': 2, 'satyr': 0.5, 'scorpion': 0, 'sea_horse': 0, 'skeleton': 0.25, 'spectator': 3, 'spider': 0, 'stirge': 0.125, 'stone_golem': 10, 'swarm_of_bats': 0.25, 'swarm_of_insects': 0.5, 'swarm_of_poisonous_snakes': 2, 'swarm_of_quippers': 1, 'swarm_of_rats': 0.25, 'swarm_of_ravens': 0.25, 'tiger': 1, 'triceratops': 5, 'troll': 5, 'twig_blight': 0.125, 'tyrannosaurus_rex': 8, 'vulture': 0, 'warhorse': 0.5, 'water_elemental': 5, 'weasel': 0, 'werewolf': 3, 'wight': 3, 'winter_wolf': 3, 'wolf': 0.25, 'worg': 0.5, 'wyvern': 6, 'yeti': 3, 'young_green_dragon': 8, 'zombie': 0.25}

NPC_CR = {'acolyte': 0.25, 'archmage': 12, 'assassin': 8, 'bandit': 0.125, 'bandit_captain': 2, 'berserker': 2, 'commoner': 0, 'cultist': 0.125, 'cult_fanatic': 2, 'gladiator': 5, 'guard': 0.125, 'knight': 3, 'mage': 6, 'noble': 0.125, 'priest': 2, 'scout': 0.5, 'spy': 1, 'thug': 0.5, 'tribal_warrior': 0.125, 'veteran': 3}

CLERIC_CANTRIP = {'guidance', 'light', 'resistance', 'sacred flame', 'spare the dying', 'thaumaturgy'}
CLERIC_1 = {'bless', 'command', 'cure wounds', 'detect magic', 'guiding bolt', 'healing word', 'inflict wounds', 'sanctuary', 'shield of faith'}
CLERIC_2 = {'aid', 'augury', 'hold person', 'lesser restoration', 'prayer of healing', 'silence', 'spiritual weapon', 'warding bond'}
CLERIC_3 = {'beacon of hope', 'dispel magic', 'mass healing word', 'protection from energy', 'remove curse', 'revivify', 'speak with dead', 'spirit guardians'}
CLERIC_4 = {'death ward', 'divination', 'freedom of movement', 'guardian of faith', 'locate creature'}
CLERIC_5 = {'commune', 'flame strike', 'greater restoration', 'mass cure wounds', 'raise dead'}
CLERIC_6 = {'blade barrier', 'find the path', 'harm', 'heal', 'heroes feast', 'true seeing'}
CLERIC_7 = {'etherealness', 'fire storm', 'regenerate', 'resurrection'}
CLERIC_8 = {'antimagic field', 'earthquake', 'holy aura'}
CLERIC_9 = {'astral projection', 'gate', 'mass heal', 'true resurrection'}


WIZARD_CANTRIP = {'acid splash', 'chill touch', 'dancing lights', 'fire bolt', 'light', 'mage hand', 'minor illusion', 'poison spray', 'presdigitation', 'ray of frost', 'shocking grasp'}
WIZARD_1 = {'burning hands', 'charm person', 'comprehend languages', 'detect magic', 'disguise self', 'identify', 'mage armour', 'magic missile', 'shield', 'silent image', 'sleep', 'thunderwave'}
WIZARD_2 = {'arcane lock', 'blur', 'darkness', 'flaming sphere', 'hold person', 'invisibility', 'knock', 'levitate', 'magic weapon', 'misty step', 'shatter', 'spider climb', 'suggestion', 'web'}
WIZARD_3 = {'counterspell', 'dispel magic', 'fireball', 'fly', 'haste', 'lightning bolt', 'major image', 'protection from energy'}
WIZARD_4 = {'arcane eye', 'dimension door', 'greater invisibility', 'ice storm', 'stoneskin', 'wall of fire'}
WIZARD_5 = {'cone of cold', 'dominate person', 'dream', 'passwall', 'wall of stone'}
WIZARD_6 = {'chain lightning', 'disintegrate', 'globe of invulnerability', 'mass suggestion', 'ottos irresistible dance', 'true seeing'}
WIZARD_7 = {'delayed blast fireball', 'finger of death', 'mordenkainens sword', 'teleport'}
WIZARD_8 = {'dominate monster', 'maze', 'power word stun', 'sunburst'}
WIZARD_9 = {'foresight', 'imprisonment', 'meteor swarm', 'power word kill', 'time stop'}

DRUID_CANTRIP = {'druidcraft', 'guidance', 'mending', 'poison spray', 'produce flame', 'resistance', 'shillelagh', 'thorn whip'}
DRUID_1 = {'animal friendship', 'charm person', 'conjure minor animals', 'create or destroy water', 'cure wounds', 'detect magic', 'detect poison and disease', 'entangle', 'faerie fire', 'fog cloud', 'goodberry', 'healing word', 'jump', 'longstrider,' 'purify food and drink', 'speak with animals', 'thunderwave'}
DRUID_2 = {'animal messenger', 'barkskin', 'beast sense', 'darkvision', 'enhance ability', 'find traps', 'flame blade', 'flaming sphere', 'gust of wind', 'heat metal', 'hold person', 'lesser restoration', 'locate animals or plants', 'locate object', 'moonbeam', 'pass without trace', 'protection from poison', 'spike growth'}
DRUID_3 = {'call lightning', 'conjure animals', 'daylight', 'dispel magic', 'feign death', 'meld into stone', 'plant growth', 'protection from energy', 'sleet storm', 'speak with plants', 'water breathing', 'water walk', 'wind wall'}
DRUID_4 = {'blight', 'confusion', 'conjure minor elementals', 'conjure woodland beings', 'control water', 'dominate beast', 'freedom of movement', 'giant insect', 'grasping vine', 'hallucinatory terrain', 'ice storm', 'locate creature', 'polymorph', 'stone shape', 'stoneskin', 'wall of fire'}
DRUID_5 = {'antilife shell', 'awaken', 'commune with nature', 'conjure elemental', 'contagion', 'geas', 'greater restoration', 'insect plague', 'mass cure wounds', 'planar binding', 'reincarnate', 'scrying', 'tree stride', 'wall of stone'}
DRUID_6 = {'conjure fey', 'find the path', 'heal', 'heroes feast', 'move earth', 'sunbeam', 'transport via plants', 'wall of thorns', 'wind walk'}
DRUID_7 = {'fire storm', 'mirage arcane', 'plane shift', 'regenerate', 'reverse gravity'}
DRUID_8 = {'animal shapes', 'antipathy/sympathy', 'control weather', 'earthquake', 'feeblemind', 'sunburst', 'tsunami'}
DRUID_9 = {'foresight', 'shapechange', 'storm of vengeance', 'true resurrection'}

WARLOCK_CANTRIP = {'chill touch', 'eldritch blast', 'mage hand', 'minor illusion', 'poison spray', 'presdigitation', 'true strike'}
WARLOCK_1 = {'charm person', 'comprehend languages', 'expeditious retreat', 'hellish rebuke', 'illusory script', 'protection from evil and good', 'unseen servant', 'find familiar'}
WARLOCK_2 = {'darkness', 'enthrall', 'hold person', 'invisibility', 'mirror image', 'misty step', 'ray of enfeeblement', 'shatter', 'spider climb', 'suggestion'}
WARLOCK_3 = {'counterspell', 'dispel magic', 'fear', 'fly', 'gaseous form', 'hypnotic pattern', 'magic circle', 'major image', 'remove curse', 'tongues', 'vampiric touch'}
WARLOCK_4 = {'banishment', 'blight', 'dimension door', 'hallucinatory terrain'}
WARLOCK_5 = {'contact other plane', 'dream', 'hold monster', 'scrying'}
WARLOCK_6 = {'circle of death', 'conjure fey', 'create undead', 'eyebite', 'flesh to stone', 'mass suggestion', 'true seeing'}
WARLOCK_7 = {'etherealness', 'finger of death', 'forcecage', 'plane shift'}
WARLOCK_8 = {'demiplane', 'dominate monster', 'feeblemind', 'glibness' 'power word stun'}
WARLOCK_9 = {'astral projection', 'foresight', 'imprisonment', 'power word kill', 'true polymorph'}

CANTRIPS_PER_LEVEL = {1: 3, 2: 3, 3: 3, 4: 4, 5: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 10: 5, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5, 18: 5, 19: 5, 20: 5}

SPELL_SLOTS_PER_LEVEL = {1: [2, 0, 0, 0, 0, 0, 0, 0, 0], 2: [3, 0, 0, 0, 0, 0, 0, 0, 0], 3: [4, 2, 0, 0, 0, 0, 0, 0, 0], 4: [4, 3, 0, 0, 0, 0, 0, 0, 0], 5: [4, 3, 2, 0, 0, 0, 0, 0, 0], 6: [4, 3, 3, 0, 0, 0, 0, 0, 0], 7: [4, 3, 3, 1, 0, 0, 0, 0, 0], 8: [4, 3, 3, 2, 0, 0, 0, 0, 0], 9: [4, 3, 3, 3, 1, 0, 0, 0, 0], 10: [4, 3, 3, 3, 2, 0, 0, 0, 0], 11: [4, 3, 3, 3, 2, 1, 0, 0, 0], 12: [4, 3, 3, 3, 2, 1, 0, 0, 0], 13: [4, 3, 3, 3, 2, 1, 1, 0, 0], 14: [4, 3, 3, 3, 2, 1, 1, 0, 0], 15: [4, 3, 3, 3, 2, 1, 1, 1, 0], 16: [4, 3, 3, 3, 2, 1, 1, 1, 0], 17: [4, 3, 3, 3, 2, 1, 1, 1, 1], 18: [4, 3, 3, 3, 2, 1, 1, 1, 1], 19: [4, 3, 3, 3, 3, 2, 2, 1, 1]}

WARLOCK_SPELL_SLOTS_PER_LEVEL = {1: 1, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 3, 12: 3, 13: 3, 14: 3, 15: 3, 16: 3, 17: 4, 18: 4, 19: 4, 20: 4}

DAMAGE_TYPES = {'acid', 'bludgeoning', 'cold', 'fire', 'force', 'lightning', 'necrotic', 'piercing', 'poison', 'psychic', 'radiant', 'slashing', 'thunder'}

#ai values
AI_INTEREST = 90 #percentage chance per turn that a monster will stay interested in player once out of sight

BASE_MOVEMENT_COST = 100
BASE_ACTION_COST = 300
REST_COST = 100
OPEN_DOOR_COST = 100
TALK_COST = 100

STANDARD_TURN_LENGTH = 300

FLAVOUR_TEXT_RATE = 50

RANDOM_MONSTER_GEN_CHANCE = 10
RANDOM_MONSTERS_PER_VAULT = 3
CHANCE_OF_NPC = 10

vaults = vaults.vault_layouts
caves = caves.vault_layouts
quest_vaults = quest_vaults.vault_layouts
stair_vaults = stair_vaults.vault_layouts
special_vaults = special_vaults.vault_layouts
encounters = encounters.encounters
dungeon = dungeon.dungeon

class Tile:
	#a tile of the map and its properties
	def __init__(self, blocked, block_sight = None, openable=False, char = '#', diggable=True):
		self.blocked = blocked
		self.char = char
 
		#all tiles start unexplored
		self.explored = STARTING_EXPLORED
 
		#by default, if a tile is blocked, it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight
		
		self.openable = openable
		
		self.diggable = diggable
		
		if dungeon_branch.theme == 'overworld':
			self.light_char = random.choice(mountain_char)
			self.dark_char = self.light_char
		elif dungeon_branch.theme == 'red':
			self.light_char = random.choice(red_wall_char)
			self.dark_char = self.light_char
		elif dungeon_branch.theme == 'town':
			self.light_char = random.choice(town_wall_char)
			self.dark_char = self.light_char
		else:
			self.light_char = random.choice(wall_char)
			self.dark_char = self.light_char
			
		if dungeon_branch.theme == 'overworld':
			self.empty_char = random.choice(grass_char)
		elif dungeon_branch.theme == 'town':
			self.empty_char = random.choice(ground_char)
		else:
			self.empty_char = random.choice(indoor_char)
		
	def open(self):
		if self.openable:
			self.blocked = False
			self.block_sight = False
			self.char = '='
			fov_map = initialize_fov()
			if familiar: fov_map_fam = initialize_fov()
			
	def close(self):
		if self.openable:
			self.blocked = True
			self.block_sight = True
			self.char = '+'
			fov_map = initialize_fov()
			if familiar: fov_map_fam = initialize_fov()
			
	def make_wall(self):
		self.blocked = True
		self.block_sight = True
		self.char = '#'
		
	def destroy_wall(self):
		global effects
		
		self.blocked = False
		self.block_sight = False
		self.char = '.'
		
	def flip_wall_status(self):
		if self.blocked:
			self.destroy_wall()
		else:
			self.make_wall()
 
class Rect:
	#a rectangle on the map. used to characterize a room.
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
 
	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self.y2) // 2
		return (center_x, center_y)
 
	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
	#this is a generic object: the player, a monster, an item, the stairs...
	#it's always represented by a character on screen.
	def __init__(self, x, y, char, name, colour, big_char=None, small_char=None, blocks=False, always_visible=False, fighter=None, ai=None, item=None, equipment=None, effect=None, quantity=None, unique=False):
		self.x = x
		self.y = y
		self.cooldown = 0
		self.char = char
		self.big_char = big_char
		self.small_char = small_char
		self.name = name
		self.proper_noun = False
		self.custom_name = False
		self.colour = colour
		self.blocks = blocks
		self.always_visible = always_visible
		self.fighter = fighter
		if self.fighter:  #let the fighter component know who owns it
			self.fighter.owner = self
		self.inventory = []
		self.followers = []
		self.quantity = quantity
		self.gold = 0.0
		self.value = None #base price if able to be bought and sold
		self.last_quiver = None #variable used to track thrown weapons used by player to re-equip automatically if picked up again
		self.versatile_weapon_with_two_hands = False #variable to use when tracking versatile weapon use
		self.two_weapon_fighting = False #variable to use when tracking dual wielding 
		
		self.last_action = None
		self.move_cost = None
		self.action_cost = None
		
		self.has_swapped = False
		self.has_been_seen = False
 
		self.ai = ai
		self.old_ai = None #storage space if we change ai's
		if self.ai:	 #let the AI component know who owns it
			self.ai.owner = self
 
		self.item = item
		if self.item:  #let the Item component know who owns it
			self.item.owner = self
 
		self.equipment = equipment
		if self.equipment:	#let the Equipment component know who owns it
			self.equipment.owner = self
 
			#there must be an Item component for the Equipment component to work properly
			self.item = Item()
			self.item.owner = self
			
		self.effect = effect
		if self.effect:
			self.effect.owner = self
			
		self.true_self = None #this is where we store the object during polymorphs
		
		self.familiar = None #used to distinguish whether this is a familiar and if so, the identity of it
		
		self.unique = unique #this indicates whether we want to show a visible sign to the player of a unique actor or something else
		
		self.flavour_text = None
		self.chatty = False #used to note NPCs that we want to talk without being spoken to
		
		self.wants = None
		self.wants_text = None
		self.reward = None
		self.reward_text = None
		
		self.merchant = False
		self.guildmaster = None
		
		self.links_to = None #used to store links to other branches and levels for stairs and other portals
		
		self.description = None
		
	def flavour_text_check(self):
		### check if we have flavour text and if so, use it
		if self.flavour_text is not None and self.chatty:
			if random.randint(1, FLAVOUR_TEXT_RATE) == FLAVOUR_TEXT_RATE:
				if player.can_see_object(self):
					message(self.name_for_printing() + ' says: ' + random.choice(self.flavour_text))
	
	def record_last_action(self, action):
		self.last_action = action #record the most recent last action
	
	def add_cooldown(self):
		if self.last_action == None: #this will happen in odd cases where a last action hasn't been recorded for some reason - defaults to action cost for now
			if self.action_cost is not None:
				value = self.action_cost
			else:
				value = BASE_ACTION_COST
		elif self.last_action == 'action':
			if self.action_cost is not None:
				value = self.action_cost
			else:
				value = BASE_ACTION_COST
		elif self.last_action == 'door':
			value = OPEN_DOOR_COST
		elif self.last_action == 'rest':
			value = REST_COST
		elif self.last_action == 'talk':
			value = TALK_COST
		elif self.last_action == 'move':
			if self.move_cost is not None:
				value = self.move_cost
			else:
				value = BASE_MOVEMENT_COST
			
			if self.fighter: #hiding movement cost increased by 50%
				for condition in self.fighter.conditions: 
					if condition.name == 'hidden':
						value = int(value * 1.5)
						
			if self.fighter: #heavy armour without required strength movemenet increased by 50% (apart from dwarves)
				if self.fighter.race != 'Mountain Dwarf' and self.fighter.race != 'Hill Dwarf':
					for item in self.inventory:
						if item.equipment:
							if item.equipment.is_equipped == 'body':
								if 'heavy armour' in item.equipment.properties and not self.fighter.can_join:
									test = None
									if 'str 13' in item.equipment.properties: test = 13
									if 'str 15' in item.equipment.properties: test = 15
									if test is not None:
										if self.fighter.strength < test:
											value = int(value * 1.5)
						
		else: #default use of action cost for any other unspecified cases
			if self.action_cost is not None:
				value = self.action_cost
			else:
				value = BASE_ACTION_COST
 
		self.cooldown += value
 
	def move(self, dx, dy):
		stuck = False
		for condition in self.fighter.conditions:
			if condition.name == 'stuck':
				stuck = True
		if stuck:
			self.record_last_action('move')
			if self.fighter.saving_throw('strength', condition.special):
				condition.remove_from_actor(self)
				if player.can_see_object(self): message(self.name_for_printing() + ' is no longer stuck.', 'white')
		else:
			#move by the given amount, if the destination is not blocked
			self.record_last_action('move')
			if not (0 > self.x + dx or self.x + dx > MAP_WIDTH-1 or 0 > self.y + dy or self.y + dy > MAP_HEIGHT-1):
				if not is_blocked(self.x + dx, self.y + dy):
					if self.fighter:
						self.fighter.check_opportunity_attack(dx, dy)
					if self.fighter: #if still alive after attacks of opportunity 
						self.x += dx
						self.y += dy
						update_lookup_map()
			
	def move_towards(self, target_x, target_y):
		#move towards and open doors if necessary
		stuck = False
		for condition in self.fighter.conditions:
			if condition.name == 'stuck':
				stuck = True
		if stuck:
			self.record_last_action('move')
			if self.fighter.saving_throw('strength', condition.special):
				condition.remove_from_actor(self)
				if player.can_see_object(self): message(self.name_for_printing() + ' is no longer stuck.', 'white')
		else:
			dx = target_x - self.x
			dy = target_y - self.y
			ddx = 0 
			ddy = 0
			if dx > 0:
				ddx = 1
			elif dx < 0:
				ddx = -1
			if dy > 0:
				ddy = 1
			elif dy < 0:
				ddy = -1
			if is_blocked(self.x + ddx, self.y + ddy): #if we're blocked, try and walk around
				if ddx == -1 and ddy == -1: #up-left
					if not is_blocked(self.x, self.y-1):
						ddx = 0
						ddy = -1
					elif not is_blocked(self.x-1, self.y):
						ddx = -1
						ddy = 0
				elif ddx == 0 and ddy == -1: #up
					if not is_blocked(self.x+1, self.y-1):
						ddx = 1
						ddy = -1
					elif not is_blocked(self.x-1, self.y-1):
						ddx = -1
						ddy = -1
				elif ddx == 1 and ddy == -1: #up-right
					if not is_blocked(self.x, self.y-1):
						ddx = 0
						ddy = -1
					elif not is_blocked(self.x+1, self.y):
						ddx = 1
						ddy = 0
				elif ddx == 1 and ddy == 0: #right
					if not is_blocked(self.x+1, self.y-1):
						ddx = 1
						ddy = -1
					elif not is_blocked(self.x+1, self.y+1):
						ddx = 1
						ddy = 1
				elif ddx == 1 and ddy == 1: #down-right
					if not is_blocked(self.x+1, self.y):
						ddx = 1
						ddy = 0
					elif not is_blocked(self.x, self.y+1):
						ddx = 0
						ddy = 1
				elif ddx == 0 and ddy == 1: #down
					if not is_blocked(self.x+1, self.y+1):
						ddx = 1
						ddy = 1
					elif not is_blocked(self.x-1, self.y+1):
						ddx = -1
						ddy = 1
				elif ddx == -1 and ddy == 1: #down-left
					if not is_blocked(self.x, self.y+1):
						ddx = 0
						ddy = 1
					elif not is_blocked(self.x-1, self.y):
						ddx = -1
						ddy = 0
				elif ddx == -1 and ddy == 0: #left
					if not is_blocked(self.x-1, self.y-1):
						ddx = -1
						ddy = -1
					elif not is_blocked(self.x-1, self.y+1):
						ddx = -1
						ddy = 1
			if not is_blocked(self.x + ddx, self.y + ddy):
				if self.fighter:
					self.fighter.check_opportunity_attack(ddx, ddy)
				if self.fighter: #if still alive after attacks of opportunity 
					self.move(ddx, ddy)
					self.record_last_action('move')
			elif is_openable(self.x + ddx, self.y + ddy):
				self.open_door(ddx, ddy)
				self.record_last_action('action')
			else: #can't find a way, so try and walk around randomly
				if ddx != 0:
					ddy = random.randint(-1, 1) #make a random decision to try and walk around an obstacle - this may or may not work but it's simple
					if 0 < (self.x + ddx) < MAP_WIDTH and 0 < (self.x + ddy) < MAP_HEIGHT:
						if not is_blocked(self.x + ddx, self.y + ddy):
							if self.fighter:
								self.fighter.check_opportunity_attack(ddx, ddy)
							if self.fighter: #if still alive after attacks of opportunity 
								self.move(ddx, ddy)
								self.record_last_action('move')
								return
				if ddy != 0:
					ddx = random.randint(-1, 1) #make a random decision to try and walk around an obstacle - this may or may not work but it's simple
					if 0 < (self.x + ddx) < MAP_WIDTH and 0 < (self.x + ddy) < MAP_HEIGHT:
						if not is_blocked(self.x + ddx, self.y + ddy):
							if self.fighter:
								self.fighter.check_opportunity_attack(ddx, ddy)
							if self.fighter: #if still alive after attacks of opportunity 
								self.move(ddx, ddy)
								self.record_last_action('move')
								return
						
	def move_away_from(self, target_x, target_y):
		stuck = False
		for condition in self.fighter.conditions:
			if condition.name == 'stuck':
				stuck = True
		if stuck:
			self.record_last_action('move')
			if self.fighter.saving_throw('strength', condition.special):
				condition.remove_from_actor(self)
				if player.can_see_object(self): message(self.name_for_printing() + ' is no longer stuck.', 'white')
		else:
			#move away from target and open doors if necessary
			dx = target_x - self.x
			dy = target_y - self.y
			ddx = 0 
			ddy = 0
			if dx > 0:
				ddx = -1
			elif dx < 0:
				ddx = 1
			if dy > 0:
				ddy = -1
			elif dy < 0:
				ddy = 1
			if not is_blocked(self.x + ddx, self.y + ddy):
				if self.fighter:
					self.fighter.check_opportunity_attack(ddx, ddy)
				if self.fighter: #if still alive after attacks of opportunity 
					self.move(ddx, ddy)
					self.record_last_action('move')
			elif is_openable(self.x + ddx, self.y + ddy):
				self.open_door(ddx, ddy)
				self.record_last_action('action')
			else:
				if ddx != 0:
					ddy = random.randint(-1, 1) #make a random decision to try and walk around an obstacle - this may or may not work but it's simple
					if not is_blocked(self.x + ddx, self.y + ddy):
						if self.fighter:
							self.fighter.check_opportunity_attack(ddx, ddy)
						if self.fighter: #if still alive after attacks of opportunity 
							self.move(ddx, ddy)
							self.record_last_action('move')
							return
				if ddy != 0:
					ddx = random.randint(-1, 1) #make a random decision to try and walk around an obstacle - this may or may not work but it's simple
					if not is_blocked(self.x + ddx, self.y + ddy):
						if self.fighter:
							self.fighter.check_opportunity_attack(ddx, ddy)
						if self.fighter: #if still alive after attacks of opportunity 
							self.move(ddx, ddy)
							self.record_last_action('move')
							return
					
	def swap_place(self, object):
		self.record_last_action('move')
		(temp_x, temp_y) = (self.x, self.y)
		(self.x, self.y) = (object.x, object.y)
		(object.x, object.y) = (temp_x, temp_y)
		
	def open_door(self, dx, dy):
		if self.true_self is None:
			self.record_last_action('door')
			map[self.x + dx][self.y + dy].open()
 
	def distance_to(self, other):
		#return the distance to another object
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)
 
	def distance(self, x, y):
		#return the distance to some coordinates
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
		
	def can_see(self, x, y):
		darkvision = False
		blindsight = False
		close_enough_to_see = False
		if self.fighter:
			if 'darkvision' in self.fighter.traits and self.distance(x, y) < 5: 
				darkvision = True
			if 'blindsight' in self.fighter.traits:
				blindsight = True
		if self.distance(x, y) < 3: close_enough_to_see = True
		fov_map.compute_fov(self.x, self.y)
		if fov_map.fov[y, x]: #the target is in field of view
			if darkvision or blindsight or close_enough_to_see or light_map[x][y] == 2: #the square is lit or we have darkvision or we are within 2 squares so close enough to see in the dark
				return True #so we can see that square
		for actor in actors:
			if self.familiar == actor:
				if actor.can_see(x, y):
					return True #this means we have a familiar and it can see that location
		return False
		
	def can_see_object(self, target):
		hidden = False
		invisible = False
		darkvision = False
		blindsight = False
		close_enough_to_see = False
		if target.fighter:
			for condition in target.fighter.conditions:
				if condition.name == 'hidden':
					hidden = True
				if condition.name == 'invisibility':
					invisible = True
		if hidden: return False #don't bother going further
		if self.fighter:
			if 'darkvision' in self.fighter.traits and self.distance(target.x, target.y) < 5:
				darkvision = True
			if 'blindsight' in self.fighter.traits:
				blindsight = True
		if invisible and not blindsight: return False #don't bother going further in this case
		if self.distance(target.x, target.y) < 3: close_enough_to_see = True
		if not hidden: #if hidden, always fail
			fov_map.compute_fov(self.x, self.y)
			if fov_map.fov[target.y, target.x]: #the target is in field of view
				if darkvision or blindsight or close_enough_to_see or light_map[target.x][target.y] == 2: #the square is lit or we have darkvision or we are within 2 squares so close enough to see in the dark
					return True #so we can see that square
		for actor in actors:
			if self.familiar == actor:
				if actor.can_see_object(target):
					return True #this means we have a familiar and it can see that object
		return False
		
	def name_for_printing(self, definite_article=True, capitalise=False, display_inventory=False):
		name = self.name #working variable
		name = name.replace("_", " ")
		over_ride = None
		prefix = []
		suffix = []
		tail = []
		inventory = []
		equipment_list = []
		carried_list = []
		inventory_string = ''
		if self.fighter:
			for condition in self.fighter.conditions:
				if condition.name_over_ride is not None:
					over_ride = condition.name_over_ride
				if condition.name_prefix is not None:
					prefix.append(condition.name_prefix)
				if condition.name_suffix is not None:
					suffix.append(condition.name_suffix)
				if condition.name_tail is not None:
					tail.append(condition.name_tail)
		if self.item:
			for condition in self.item.conditions:
				if condition.name_over_ride is not None:
					over_ride = condition.name_over_ride
				if condition.name_prefix is not None:
					prefix.append(condition.name_prefix)
				if condition.name_suffix is not None:
					suffix.append(condition.name_suffix)
				if condition.name_tail is not None:
					tail.append(condition.name_tail)
		if over_ride is not None: name = over_ride
		for pre in prefix:
			name = pre + name
		for suf in suffix:
			name = name + suf
		for tai in tail:
			name = name + tai
		if display_inventory and self != player:
			if len(self.inventory) > 0:
				inventory_string = ' ('
				for item in self.inventory:
					item_name = item.name_for_printing(definite_article=False)
					if item.equipment:
						if item.equipment.is_equipped is not None:
							equipment_list.append(item_name)
						else:
							carried_list.append(item_name)
					else:
						carried_list.append(item_name)
				if len(equipment_list) > 0:
					inventory_string = inventory_string + 'equipped: '
					for item in equipment_list:
						inventory_string = inventory_string + item + ', '
					inventory_string = inventory_string[:-2]
					inventory_string = inventory_string + '; '
				if len(carried_list) > 0:
					inventory_string = inventory_string + 'carried: '
					for item in carried_list:
						inventory_string = inventory_string + item + ', '
				inventory_string = inventory_string[:-2] + ')'
		if self.proper_noun or self.custom_name:
			return name.title() + inventory_string
		else:
			if definite_article: name = 'the ' + name
			if capitalise:
				return name.capitalize() + inventory_string
			else:
				return name + inventory_string
			
	def use_quantity(self, user, amount=1):
		self.quantity -= amount
		if self.quantity <= 0: #this item has run out
			if self.equipment:
				self.equipment.dequip(user) #so unequip it first
			user.inventory.remove(self) #then remove it from the inventory
		
class Fighter:
	#combat-related properties and methods (monster, player, NPC).
	def __init__(self, hp, strength, dexterity, constitution, intelligence, wisdom, charisma, clevel, proficiencies, traits, spells, xp, race=None, role=None, death_function=None, ac=10, num_dmg_die=1, dmg_die=2, dmg_bonus=0, dmg_type = 'bludgeoning', to_hit=0, ranged_num_dmg_die=None, ranged_dmg_die=None, ranged_dmg_bonus=None, ranged_dmg_type=None, ranged_to_hit=None, challenge_rating=None, casting_stat='intelligence', faction='monster', natural_weapon='Unarmed'):
		self.max_hp = hp
		self.base_max_hp = hp
		self.hp = hp
		self.temp_hp = 0
		self.race = race
		self.role = role
		self.strength = strength
		self.dexterity = dexterity
		self.constitution = constitution
		self.intelligence = intelligence
		self.wisdom = wisdom
		self.charisma = charisma
		self.base_strength = strength
		self.base_dexterity = dexterity
		self.base_constitution = constitution
		self.base_intelligence = intelligence
		self.base_wisdom = wisdom
		self.base_charisma = charisma
		self.clevel = clevel
		self.proficiencies = proficiencies
		self.traits = traits
		self.spells = spells
		self.casting_stat = casting_stat
		self.conditions = []
		self.base_ac = ac
		self.base_num_dmg_die = num_dmg_die
		self.base_dmg_die = dmg_die
		self.base_dmg_bonus = dmg_bonus
		self.base_dmg_type = dmg_type
		self.base_to_hit = to_hit
		self.ranged_base_num_dmg_die = ranged_num_dmg_die
		self.ranged_base_dmg_die = ranged_dmg_die
		self.ranged_base_dmg_bonus = ranged_dmg_bonus
		self.ranged_base_dmg_type = ranged_dmg_type
		self.ranged_base_to_hit = ranged_to_hit
		self.monster = True #this is a tag which makes monsters skip their to_hit and dexterity bonus for ac - should be set for false for PC's
		self.faction = faction
		self.true_faction = self.faction #variable to be used if charmed
		self.asked_to_join = False #variable to record whether we have tried to recruit
		self.always_join = False #variable to record when recruitment should always be successful - used by dismissed npcs
		self.opportunity_attack = False #variable to make sure we only attack of opportunity once per turn
		self.can_join = False #used to determine whether this creature is recruitable
		self.magic = False #used to determine if graphical flag is shown
		self.ranged = False #as above
		
		self.xp = xp
		self.death_function = death_function
		self.challenge_rating = challenge_rating
		
		self.natural_weapon = natural_weapon
		
		if 'magic' in self.proficiencies and self.role != 'Warlock':
			self.spell_slots = list(SPELL_SLOTS_PER_LEVEL[self.clevel])
		else:
			self.spell_slots = [0,0,0,0,0,0,0,0,0]
			
		if 'magic' in self.proficiencies and self.role == 'Warlock':
			self.warlock_spell_slots = WARLOCK_SPELL_SLOTS_PER_LEVEL[self.clevel]
		else:
			self.warlock_spell_slots = 0
			
	
 
	def attack(self, target, ranged=False, advantage=False, disadvantage=False, opportunity_attack=False, use_ranged_stats=False, ammo_limit=None):
	
		self.owner.record_last_action('action')
		
		if opportunity_attack:
			number_of_attacks = 1
		else:
			number_of_attacks = 1 
			for trait in self.traits:
				if trait == 'extra attack':
					number_of_attacks += 1
			if self.owner.two_weapon_fighting and not ranged:
				number_of_attacks += 1
				
		ammo_used = 0 #used to track amount of ammunition to reduce from quiver in due course
		if ammo_limit is None: ammo_limit = 1 #hacky way to get around the way this function is build - if we have proper ammo, then we should have a proper ammo limit. if we don't have proper ammo, then the limit will be none, but the ammo_used will never go up. this lets us do a simple comparison while avoiding comparing a null value
				
		has_sneak_attacked = False #need to monitor if a successful sneak attack is made because that damage bonus is only applied once per round, not for each blow
				
		for i in range(number_of_attacks):
			if target.fighter is not None and not is_unconscious(target) and ammo_used < ammo_limit: #target is still alive, so keep attacking
				
				if i == (number_of_attacks - 1) and self.owner.two_weapon_fighting and not opportunity_attack and not ranged: #off hand attack will be last attack of the round while using two-weapon fighting and not making an opportunity attack and not using a ranged attack
					off_hand_attack = True
				else:
					off_hand_attack = False
				
				to_hit_bonus = 0 
				damage = 0
				attacker_monster = self.monster
				target_monster = target.fighter.monster
				
				### identify whether there is a weapon in the 'main hand' slot - identify if it is not a ranged weapon and what is in the quiver - if it is armour, check if we are proficient, else give disadvantage
				launcher = False
				weapon_in_main_hand = None
				weapon_in_off_hand = None
				thrown = False
				quiver = None
				for item in self.owner.inventory:
					if item.equipment:
						if item.equipment.is_equipped:
							if item.equipment.is_equipped == 'main hand':
								weapon_in_main_hand = item
								if 'launcher' in item.equipment.properties:
									launcher = True
							if item.equipment.is_equipped == 'off hand':
								weapon_in_off_hand = item
							if item.equipment.is_equipped == 'quiver':
								quiver = item
							if item.equipment.is_equipped == 'body':
								if 'light armour' in item.equipment.properties:
									if 'light armour' not in self.proficiencies:
										disadvantage = True
								if 'medium armour' in item.equipment.properties:
									if 'medium armour' not in self.proficiencies:
										disadvantage = True
								if 'heavy armour' in item.equipment.properties:
									if 'heavy armour' not in self.proficiencies:
										disadvantage = True
							if item.equipment.is_equipped == 'off hand':
								if 'shield' in item.equipment.properties:
									if 'shields' not in self.proficiencies:
										disadvantage = True
				
				if ranged:
					if not launcher:
						if quiver is not None:
							thrown = True
					if launcher:
						ammo_used += 1
							
				weapon_to_use = None
				if off_hand_attack:
					weapon_to_use = weapon_in_off_hand
				elif not ranged and weapon_in_main_hand and not launcher:
					weapon_to_use = weapon_in_main_hand
				elif ranged and weapon_in_main_hand and launcher:
					weapon_to_use = weapon_in_main_hand
				elif ranged and thrown:
					weapon_to_use = quiver
						
				### add combat modifier - if there is a weapon in the 'main hand' slot, then use the strength modifier - unless that weapon has the 'finesse' property, in which case use the dexterity modifier - if the actor has a proficiency in that weapon or that class of weapon, add the proficiency bonus - otherwise, use the base 'to hit modifier
				
				finesse = False
				if weapon_to_use is not None:
					if 'finesse' in weapon_to_use.equipment.properties and ABILITY_MODIFIER[self.dexterity] > ABILITY_MODIFIER[self.strength]:
						finesse = True
						to_hit_bonus = ABILITY_MODIFIER[self.dexterity]
					elif launcher: #launcher's use dexterity for to-hit bonus
						to_hit_bonus = ABILITY_MODIFIER[self.dexterity]
					else: #all other scenarios including thrown weapons use strength
						to_hit_bonus = ABILITY_MODIFIER[self.strength]
				else:
					if use_ranged_stats:
						to_hit_bonus = self.ranged_base_to_hit
					else:
						to_hit_bonus = self.base_to_hit
					
				#deal with any magical or other effects from equipment
				for item in self.owner.inventory:
					if item.equipment:
						if item.equipment.is_equipped:
							if item.equipment.is_equipped != 'quiver' or item == weapon_in_main_hand: #we don't want to give bonuses for this unless it's actually the weapon we're using
								for condition in item.item.conditions:
									if condition.to_hit_bonus != 0:
										to_hit_bonus += condition.to_hit_bonus
									if condition.damage_bonus != 0:
										damage += condition.damage_bonus
				
				proficient = False
				if weapon_to_use is not None:
					if weapon_to_use.name in self.proficiencies:
						proficient = True
					else:
						if 'simple weapon' in weapon_to_use.equipment.properties:
							if 'simple weapons' in self.proficiencies:
								proficient = True
						if 'martial weapon' in weapon_to_use.equipment.properties:
							if 'martial weapons' in self.proficiencies:
								proficient = True
				
				if proficient: to_hit_bonus += PROFICIENCY_BONUS[self.clevel]
				
				duelist = False #work out if using a one-handed weapon in main hand with the dueling fighting style - this gives a +2 bonus to damage later
				if 'dueling' in self.proficiencies:
					if weapon_to_use is not None:
						if not ranged:
							if 'two-handed' not in weapon_to_use.equipment.properties and not self.owner.versatile_weapon_with_two_hands:
								duelist = True 
								
				versatile = False #work out if we are using a one-handed weapon with two hands
				if weapon_to_use is not None:
					if 'versatile' in weapon_to_use.equipment.properties:
						if self.owner.versatile_weapon_with_two_hands:
							versatile = True

				### work out if pack tactics applies - if an ally is next to the target then give an advantage
				if 'pack tactics' in self.traits:
					for actor in actors:
						if actor.fighter:
							if actor.fighter.faction == self.faction and actor != self.owner:
								if actor.distance_to(target) < 2:
									advantage = True
									break #only need to apply it once
								
				### work out if protection applies from a nearby ally and deal with the consequences if this is the case
				for actor in actors:
					if actor.fighter:
						if 'protection' in actor.fighter.proficiencies or 'protection without shield' in actor.fighter.proficiencies:
							if actor.fighter.faction == target.fighter.faction and actor != target:
								if not is_incapacitated(actor):
									if actor.distance_to(target) < 2:
										has_shield = False
										if 'protection without shield' in actor.fighter.proficiencies:
											has_shield = True
										else:
											for item in actor.inventory:
												if item.equipment:
													if item.equipment.is_equipped:
														if 'shield' in item.equipment.properties:
															has_shield = True
										if has_shield:
											can_protect = True #test to see if we have already used this ability this round
											for condition in target.fighter.conditions:
												if condition.name == 'has protected':
													can_protect = False
											if can_protect:
												disadvantage = True
												obj = Condition(name='has protected', duration=1, visible=False)
												obj.owner = actor 
												actor.fighter.conditions.append(obj)#this condition prohibits protection from being used more than once a round

				### figure out if we are too close to properly use ranged weapons
				if (ranged or use_ranged_stats) and self.owner.distance_to(target) < 2:
					disadvantage = True #disadvantage for firing too close to the target
					
				### give bonus if using ranged and have that fighting style
				if (ranged or use_ranged_stats):
					if 'archery' in self.proficiencies: to_hit_bonus += 2
				
				### find out if we are hidden, can sneak attack and are using a finesse weapon - if so, then we can sneak attack
				
				hidden = False
				invisible = False
				for condition in self.conditions:
					if condition.name == 'hidden':
						hidden = True
						advantage = True #give advantage to hidden attackers - this might be reset for multiple attacks and advantage might carry over but this isn't a problem, hidden attackers can get advantage for multiple attacks on the same turn
					if condition.name == 'invisibility':
						invisible = True
						if 'blindsight' not in target.fighter.traits:
							advantage = True #as above - invisible attackers get advantage but the exception to this is blindsight because they can still sense invisible actors - will need to update this for magical detection in due course
				
				sneak_attack = False
				if not has_sneak_attacked:
					if 'sneak attack' in self.traits:
						if (finesse or ranged or use_ranged_stats) or self.monster:
							if hidden: #always sneak attack when hidden
								sneak_attack = True
							else:
								for actor in actors: #sneak attack when allies are next to target
									if actor.fighter.faction == self.faction and actor != self.owner:
										if actor.distance_to(target) < 2:
											sneak_attack = True
				
				if 'lucky' in self.traits: lucky = True
				else: lucky = False
				
				attack_roll = d20_roll(advantage, disadvantage, lucky)

				### compare the d20 to the defender's armour class - if the d20 roll was a 1, then it always misses, if the d20 roll was 20, then it always hits with critical damage
				
				#first of all get the defender's ac
				#start by finding out what armour and shields are being used
				equipped_armour = None
				equipped_shield = None
				for item in target.inventory:
					if item.equipment:
						if item.equipment.is_equipped:
							if item.equipment.is_equipped == 'body':
								equipped_armour = item
							elif 'shield' in item.equipment.properties:
								equipped_shield = item
				
				#now apply any dexterity modifier based on the weight of the armour (if any)
				dex_modifier = ABILITY_MODIFIER[target.fighter.dexterity]
				if equipped_armour is not None:
					defender_ac = equipped_armour.equipment.ac
					if 'light armour' in equipped_armour.equipment.properties:
						if dex_modifier > 0:
							defender_ac += dex_modifier
					elif 'medium armour' in equipped_armour.equipment.properties:
						if dex_modifier > 0:
							if dex_modifier > 2: dex_modifier = 2 #cap the modifier at 2
							defender_ac += dex_modifier
					elif 'heavy armour' in equipped_armour.equipment.properties:
						pass #no dex modifier for heavy armour
				else:  
					defender_ac = target.fighter.base_ac
					if not target_monster: #monsters don't get this benefit while unarmoured because it's already factored in
						if dex_modifier > 0: 
							defender_ac += dex_modifier #full benefit for dexterity while unarmoured
						
				#finally deal with equipped shields
				if equipped_shield:
					defender_ac += equipped_shield.equipment.ac
				
				#deal with any other bonuses to ac from equipment
				for item in target.inventory:
					if item.equipment:
						if item.equipment.is_equipped:
							for condition in item.item.conditions:
								if condition.to_hit_bonus != 0:
									defender_ac += condition.ac_bonus
				
				#compare the roll to the calculated ac, while also taking into account 20's always being hits and 1's always being misses
				if 'superior critical' in self.traits: critical_min = 18
				elif 'improved critical' in self.traits: critical_min = 19
				else: critical_min = 20
				
				successful_attack = False
				if attack_roll >= critical_min: 
					successful_attack = True
				elif attack_roll != 1:
					if attack_roll + to_hit_bonus > defender_ac:
						successful_attack = True
						
				#special case for shield spell - if a successful attack and spell in place, use the spell, add 5AC to defender and see if the hit was still successful along with setting the spell to expire that turn
				
				if successful_attack:
					for condition in target.fighter.conditions:
						if condition.name == 'shield': 
							condition.permanent = False
							condition.duration = 1 #make the condition expire the next turn - we need to do it this way in case multiple attacks are aimed at the same target - the bonus should apply to all attacks
							successful_attack = False #reset the calculation and start again
							if attack_roll == 20: 
								successful_attack = True
							elif attack_roll != 1:
								if attack_roll + to_hit_bonus > defender_ac + 5:
									successful_attack = True
				
				### identify whether any hit was a critical hit - usually this is if there is a d20 roll of 20, although can change with certain abilities
				
				critical_hit = False
				if attack_roll >= critical_min: 
					critical_hit = True
					
				savage = False
				if 'savage' in self.traits:
					savage = True
				
				### roll for damage - this is based on the weapon's attributes if there is one - if there isn't one, then it's based on the base attributes of that creature - if it's a critical hit, then roll twice and add them together - add an extra d6 for sneak attacks (and do this twice if a critical hit
				
				if off_hand_attack and not 'two-weapon fighting' in self.proficiencies: #handle two-weapon fighting style
					no_dmg_bonus = True
				else:
					no_dmg_bonus = False
				
				if duelist: damage += 2 #flat bonus for dueling fighting style
				if successful_attack:
					if weapon_to_use:
						num_dmg_die = weapon_to_use.equipment.num_dmg_die
						dmg_die = weapon_to_use.equipment.dmg_die
						if versatile: dmg_die += 2
						roll = dice_roll(num_dmg_die, dmg_die)
						if roll <= 2:
							if 'great weapon fighting' in self.proficiencies: 
								if ('two-handed' in weapon_to_use.equipment.properties) or ('versatile' in weapon_to_use.equipment.properties and self.owner.versatile_weapon_with_two_hands is True):
									roll = dice_roll(num_dmg_die, dmg_die) #second roll for this fighting style using two handed weapons
						if no_dmg_bonus and damage > 0:
							damage = roll
						else:
							damage += roll
						if (finesse and ABILITY_MODIFIER[self.dexterity] > ABILITY_MODIFIER[self.strength]) or (ranged and launcher): bonus = ABILITY_MODIFIER[self.dexterity]
						else: bonus = ABILITY_MODIFIER[self.strength]
						if no_dmg_bonus and bonus > 0:
							pass
						else:
							damage += bonus
						if critical_hit: #add a second roll with modifiers
							roll = dice_roll(num_dmg_die, dmg_die)
							if roll <= 2:
								if 'great weapon fighting' in self.proficiencies: 
									if ('two-handed' in weapon_to_use.equipment.properties) or ('versatile' in weapon_to_use.equipment.properties and self.owner.versatile_weapon_with_two_hands is True):
										dice_roll(num_dmg_die, dmg_die) #second roll for this fighting style using two handed weapons
							damage += roll
							if (finesse and ABILITY_MODIFIER[self.dexterity] > ABILITY_MODIFIER[self.strength]) or (ranged and launcher): bonus = ABILITY_MODIFIER[self.dexterity]
							else: bonus = ABILITY_MODIFIER[self.strength]
							if no_dmg_bonus and bonus > 0:
								pass
							else:
								damage += bonus
							if savage: #add an extra die to the damage
								roll = dice_roll(1, dmg_die) #only 1 die
								if roll <= 2:
									if 'great weapon fighting' in self.proficiencies: 
										if ('two-handed' in weapon_to_use.equipment.properties) or ('versatile' in weapon_to_use.equipment.properties and self.owner.versatile_weapon_with_two_hands is True):
											dice_roll(1, dmg_die) #second roll for this fighting style using two handed weapons
								damage += roll
						if sneak_attack: #add extra damage rolls for sneak attack
							has_sneak_attacked = True #record successful sneak attack
							for i in range(SNEAK_ATTACK_MODIFIER[self.clevel]): #number of rolls depends on clvl
								damage += dice_roll(1, 6) #extra 1d6 damage per roll
							if critical_hit: #sneak attack rolled twice as well
								for i in range(SNEAK_ATTACK_MODIFIER[self.clevel]): #number of rolls depends on clvl
									damage += dice_roll(1, 6) #extra 1d6 damage per roll

					else: #unarmed or natural attack for monsters
						if use_ranged_stats:
							roll = dice_roll(self.ranged_base_num_dmg_die, self.ranged_base_dmg_die)
						else:
							roll = dice_roll(self.base_num_dmg_die, self.base_dmg_die)
						damage += roll
						if self.monster: #inherent damage bonus for monsters
							if use_ranged_stats:
								damage += self.ranged_base_dmg_bonus
							else:
								damage += self.base_dmg_bonus
						else: #if no inherent bonus, use the stats
							damage += ABILITY_MODIFIER[self.strength]
						if critical_hit: #second dice roll for critical hits
							if use_ranged_stats:
								roll = dice_roll(self.ranged_base_num_dmg_die, self.ranged_base_dmg_die)
							else:
								roll = dice_roll(self.base_num_dmg_die, self.base_dmg_die)
							damage += roll
							if self.monster: #inherent damage bonus for monsters
								if use_ranged_stats:
									damage += self.ranged_base_dmg_bonus
								else:
									damage += self.base_dmg_bonus
							else: #if no inherent bonus, use the stats
								damage += ABILITY_MODIFIER[self.strength]
						if sneak_attack: #add extra damage rolls for sneak attack
							has_sneak_attacked = True #record successful sneak attack
							for i in range(SNEAK_ATTACK_MODIFIER[self.clevel]): #number of rolls depends on clvl
								damage += dice_roll(1, 6) #extra 1d6 damage per roll
							if critical_hit: #sneak attack rolled twice as well
								for i in range(SNEAK_ATTACK_MODIFIER[self.clevel]): #number of rolls depends on clvl
									damage += dice_roll(1, 6) #extra 1d6 damage per roll
				
				damage_type = None
				if weapon_to_use is not None:
					for property in weapon_to_use.equipment.properties:
						if property in DAMAGE_TYPES: #there should only be one damage type per weapon
							damage_type = property
				if damage_type is None:
					damage_type = self.base_dmg_type
				
				fov_map.compute_fov(player.x, player.y)#reset fov_map to player
				if self.owner == player or target == player:
					player_can_see = True
				else:
					player_can_see = player.can_see_object(self.owner) 
				adv_string = ''
				if advantage and not disadvantage: adv_string = ' (+)'
				elif disadvantage and not advantage: adv_string = ' (-)'
				opportunity_attack_string = ''
				if opportunity_attack: opportunity_attack_string = ' (OA)'
				if successful_attack:
					if critical_hit and sneak_attack:
						if player_can_see: 
							if off_hand_attack:
								message(self.owner.name_for_printing() + ' sneak attacks and critically hits ' + target.name_for_printing() + ' with the off hand for ' + str(damage) + ' hit points!' + adv_string + opportunity_attack_string)
							else:
								message(self.owner.name_for_printing() + ' sneak attacks and critically hits ' + target.name_for_printing() + ' for ' + str(damage) + ' hit points!' + adv_string + opportunity_attack_string)
					elif critical_hit:
						if player_can_see: 
							if off_hand_attack:
								message(self.owner.name_for_printing() + ' critically hits ' + target.name_for_printing() + ' with the off hand for ' + str(damage) + ' hit points!' + adv_string + opportunity_attack_string)
							else:
								message(self.owner.name_for_printing() + ' critically hits ' + target.name_for_printing() + ' for ' + str(damage) + ' hit points!' + adv_string + opportunity_attack_string)
					elif sneak_attack:
						if player_can_see: 
							if off_hand_attack:
								message(self.owner.name_for_printing() + ' sneak attacks ' + target.name_for_printing() + ' with the off hand for ' + str(damage) + ' hit points!' + adv_string + opportunity_attack_string)
							else:
								message(self.owner.name_for_printing() + ' sneak attacks ' + target.name_for_printing() + ' for ' + str(damage) + ' hit points!' + adv_string + opportunity_attack_string)
					else:
						if player_can_see: 
							if off_hand_attack:
								message(self.owner.name_for_printing() + ' hits ' + target.name_for_printing() + ' with the off hand for ' + str(damage) + ' hit points.' + adv_string + opportunity_attack_string)
							else:
								message(self.owner.name_for_printing() + ' hits ' + target.name_for_printing() + ' for ' + str(damage) + ' hit points.' + adv_string + opportunity_attack_string)
					target.fighter.take_damage(damage, self.owner, damage_type)
				elif player_can_see:
					message(self.owner.name_for_printing() + ' attacks ' + target.name_for_printing() + ' but misses.' + adv_string + opportunity_attack_string)

				### deal with special case of poisonous weapons or monsters
				#if successful_attack and weapon_to_use is not None:
				#	if 'poisonous' in weapon_to_use.equipment.properties:
				#		apply_poison(target)
						
				#if successful_attack and attacker_monster and weapon_to_use is None:
				#	if 'poisonous' in self.traits:
				#		apply_poison(target)
						
				### deal with conditions on magic weapons which can cause further effects
				if successful_attack and weapon_to_use is not None:
					for condition in weapon_to_use.item.conditions:
						if condition.damage_on_hit:
							condition.effect_on_hit(target, self)
							
				### deal with conditions on attacker which can cause further effects
				if successful_attack:
					for condition in self.conditions:
						if condition.damage_on_hit:
							condition.effect_on_hit(target, self.owner)
							
					if target.fighter:
						for condition in target.fighter.conditions:
							condition.effect_on_being_hit(target, self.owner)
						
				### if it was a sneak attack and the defender is still alive, do an active perception check against the hidden attacker to see if they are exposed
				
				if hidden:
					if target.fighter is not None: #should be set to none by now if dead
						dex_roll = random.randint(1, 20)
						dex_bonus = ABILITY_MODIFIER[self.dexterity] #dex bonus for stealth
						if 'stealthy' in self.traits:
							dex_bonus += PROFICIENCY_BONUS[self.clevel]
						for item in self.owner.inventory:
							if item.equipment:
								if item.equipment.is_equipped:
									if 'unstealthy' in item.equipment.properties:
										dex_bonus -= 2
						wis_roll = random.randint(1, 20)
						wis_bonus = ABILITY_MODIFIER[target.fighter.wisdom]
						if 'perception' in target.fighter.proficiencies: #bonus if that actor has a perception proficiency
							wis_bonus += PROFICIENCY_BONUS[target.fighter.clevel]
							
						if dex_roll + dex_bonus < wis_roll + wis_bonus: #active wisdom/perception vs dexterity/stealth check
							if player_can_see: message(self.owner.name_for_printing() + ' has been spotted.')
							for condition in self.conditions:
								if condition.name == 'hidden':
									condition.remove_from_actor(self.owner)
				
				if invisible: #cancel invisibility if attack while invisible
					for condition in self.conditions:
						if condition.name == 'invisibility':
							condition.remove_from_actor(self.owner)
							if player.can_see_object(self.owner):
								message(self.owner.name_for_printing() + ' becomes visible by attacking.', 'white')
								
				if ranged or use_ranged_stats:
					projectile_effect(self.owner.x, self.owner.y, target.x, target.y, [255,255,255])
		return ammo_used
		
	def calc_ac(self):
		#first of all get the defender's ac
		#start by finding out what armour and shields are being used
		equipped_armour = None
		equipped_shield = None
		for item in self.owner.inventory:
			if item.equipment:
				if item.equipment.is_equipped:
					if item.equipment.is_equipped == 'body':
						equipped_armour = item
					elif 'shield' in item.equipment.properties:
						equipped_shield = item
		
		#now apply any dexterity modifier based on the weight of the armour (if any)
		dex_modifier = ABILITY_MODIFIER[self.dexterity]
		if equipped_armour is not None:
			defender_ac = equipped_armour.equipment.ac
			if 'light armour' in equipped_armour.equipment.properties:
				if dex_modifier > 0:
					defender_ac += dex_modifier
			elif 'medium armour' in equipped_armour.equipment.properties:
				if dex_modifier > 0:
					if dex_modifier > 2: dex_modifier = 2 #cap the modifier at 2
					defender_ac += dex_modifier
			elif 'heavy armour' in equipped_armour.equipment.properties:
				pass #no dex modifier for heavy armour
		else:  
			defender_ac = self.base_ac
			if not self.monster: #monsters don't get this benefit while unarmoured because it's already factored in
				if dex_modifier > 0: 
					defender_ac += dex_modifier #full benefit for dexterity while unarmoured
				
		#deal with equipped shields
		if equipped_shield:
			defender_ac += equipped_shield.equipment.ac
			
		#deal with conditions with bonus ac
		for condition in self.conditions:
			if condition.ac_bonus != 0:
				#if condition.variable_bonus is True:
				#	if condition.ac_bonus > 0: lower_bound = 1
				#	if condition.ac_bonus < 0: lower_bound = -1
				#	defender_ac += random.randint(lower_bound, condition.ac_bonus)
				#else:
				defender_ac += condition.ac_bonus
					
		#deal with bonus for fighting style of defence
		if equipped_armour is not None:
			if 'defence' in self.proficiencies:
				defender_ac += 1
			
		return defender_ac
 
	def take_damage(self, damage, attacker, damage_type='bludgeoning'):

		immune_dmg_test = damage_type + ' immune'
		resist_dmg_test = damage_type + ' resistance'
		vulnerable_dmg_test = damage_type + ' vulnerable'
		if immune_dmg_test in self.traits: #immune to this type - no damage
			damage = 0
			message(self.owner.name_for_printing() + ' is immune to ' + damage_type + ' damage.')
		else:
			if resist_dmg_test in self.traits: #resistant to this type of damage - half damage applies
				damage = damage // 2
				message(self.owner.name_for_printing() + ' is resistant to ' + damage_type + ' damage.')
			if vulnerable_dmg_test in self.traits: #vulnerable to this type - double damage applies
				damage = damage * 2
				message(self.owner.name_for_printing() + ' is vulnerable to ' + damage_type + ' damage.')
		
		if self.faction == 'neutral':
			if attacker.fighter.faction == 'player':
				make_hostile(self.owner)
		#apply damage if possible
		if damage > 0:
			if self.temp_hp > 0:
				self.temp_hp -= damage
				if self.temp_hp < 0: #this means we should carry over this damage to main hp
					damage = abs(self.temp_hp) #this converts to a positive number the carryover damage
					self.temp_hp = 0
				else:
					damage = 0
			self.hp -= damage
 
			#check for death. if there's a death function, call it
			if self.hp <= 0:
				if 'relentless' in self.traits:
					has_used_relentless = False
					for condition in self.conditions:
						if condition.name == 'used relentless':
							has_used_relentless = True
					if has_used_relentless:
						function = self.death_function
						if function is not None:
							function(self.owner, attacker)
					else:
						player_can_see = player.can_see_object(self.owner) 
						if player_can_see: message(self.owner.name_for_printing() + ' uses relentless endurance to stay alive.')
						self.hp = 1
						obj = Condition(name='used relentless', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest
						obj.owner = self.owner
						self.conditions.append(obj)
				else:
					function = self.death_function
					if function is not None:
						function(self.owner, attacker)
 
	def heal(self, amount):
		#first, if unconscious, remove that condition and give 1 hp
		for condition in self.conditions:
			if condition.name == 'unconscious':
				condition.remove_from_actor(self.owner)
				self.hp = 1
		#heal by the given amount, without going over the maximum
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp
			
	def saving_throw(self, type, difficulty, advantage=False, disadvantage=False):
		if type == 'strength': 
			bonus = ABILITY_MODIFIER[self.strength]
			if 'strength save' in self.traits:
				bonus += PROFICIENCY_BONUS[self.clevel]
		if type == 'dexterity': 
			bonus = ABILITY_MODIFIER[self.dexterity]
			if 'dexterity save' in self.traits:
				bonus += PROFICIENCY_BONUS[self.clevel]
		if type == 'constitution': 
			bonus = ABILITY_MODIFIER[self.constitution]
			if 'constitution save' in self.traits:
				bonus += PROFICIENCY_BONUS[self.clevel]
		if type == 'wisdom': 
			bonus = ABILITY_MODIFIER[self.wisdom]
			if 'wisdom save' in self.traits:
				bonus += PROFICIENCY_BONUS[self.clevel]
		if type == 'intelligence': 
			bonus = ABILITY_MODIFIER[self.intelligence]
			if 'intelligence save' in self.traits:
				bonus += PROFICIENCY_BONUS[self.clevel]
		if type == 'charisma': 
			bonus = ABILITY_MODIFIER[self.charisma]
			if 'charisma save' in self.traits:
				bonus += PROFICIENCY_BONUS[self.clevel]

		for condition in self.conditions:
			if condition.saving_throw_bonus != 0:
				if condition.variable_bonus is True:
					if condition.saving_throw_bonus > 0: lower_bound = 1
					if condition.saving_throw_bonus < 0: lower_bound = -1
					bonus += random.randint(lower_bound, condition.saving_throw_bonus)
				else:
					bonus += condition.saving_throw_bonus
			if condition.name == 'resistance': #need to remove this because it only works for one saving throw - if we get here, then it's used up
				condition.remove_from_actor(condition.owner)
		
		if 'lucky' in self.traits: lucky = True
		else: lucky = False
		roll = d20_roll(advantage, disadvantage, lucky)

		if roll + bonus > difficulty: 
			return True #successful saving throw
		else: 
			return False #failed saving throw

	def spell_dc(self):
		bonus = 0
		if self.casting_stat == 'intelligence': 
			bonus = ABILITY_MODIFIER[self.intelligence]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		if self.casting_stat == 'wisdom': 
			bonus = ABILITY_MODIFIER[self.wisdom]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		if self.casting_stat == 'charisma': 
			bonus = ABILITY_MODIFIER[self.charisma]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		return 10 + bonus
			
	def spell_attack(self, advantage=False, disadvantage=False):
		if 'lucky' in self.traits: lucky = True
		else: lucky = False
		roll = d20_roll(advantage, disadvantage, lucky)
		bonus = 0
		if self.casting_stat == 'intelligence': 
			bonus = ABILITY_MODIFIER[self.intelligence]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		if self.casting_stat == 'wisdom': 
			bonus = ABILITY_MODIFIER[self.wisdom]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		if self.casting_stat == 'charisma': 
			bonus = ABILITY_MODIFIER[self.charisma]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		return roll + bonus
		
	def ranged_spell_attack(self, target, advantage=False, disadvantage=False):
		if 'lucky' in self.traits: lucky = True
		else: lucky = False
		roll = d20_roll(advantage, disadvantage, lucky)
		bonus = 0
		if self.casting_stat == 'intelligence': 
			bonus = ABILITY_MODIFIER[self.intelligence]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		if self.casting_stat == 'wisdom': 
			bonus = ABILITY_MODIFIER[self.wisdom]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		if self.casting_stat == 'charisma': 
			bonus = ABILITY_MODIFIER[self.charisma]
			if 'magic' in self.proficiencies: 
				bonus += PROFICIENCY_BONUS[self.clevel]
		if ((roll != 1) and (roll + bonus > target.fighter.calc_ac())) or (roll == 20):
			return True #hit
		else:
			return False #miss 
			
	def melee_spell_attack(self, target, advantage=False, disadvantage=False):
		if 'lucky' in self.traits: lucky = True
		else: lucky = False
		roll = d20_roll(advantage, disadvantage, lucky)
		if self.monster: bonus = self.base_to_hit
		else: bonus = ABILITY_MODIFIER[self.strength]
		if ((roll != 1) and (roll + bonus > target.fighter.calc_ac())) or (roll == 20):
			return True #hit
		else:
			return False #miss 
			
	def use_spell_slot(self, spell): #function for NPC's to use up spell slots
		level = None
		if spell in WIZARD_1 or spell in CLERIC_1: level = 0 #these are 1 less then actual level
		if spell in WIZARD_2 or spell in CLERIC_2: level = 1
		if spell in WIZARD_3 or spell in CLERIC_3: level = 2
		if spell in WIZARD_4 or spell in CLERIC_4: level = 3
		if spell in WIZARD_5 or spell in CLERIC_5: level = 4
		if spell in WIZARD_6 or spell in CLERIC_6: level = 5
		if spell in WIZARD_7 or spell in CLERIC_7: level = 6
		if spell in WIZARD_8 or spell in CLERIC_8: level = 7
		if spell in WIZARD_9 or spell in CLERIC_9: level = 8
		if level is not None:
			self.spell_slots[level] -= 1
			
	def check_opportunity_attack(self, dx, dy):
		#x, y is the map coordinates that this unit is moving to
		#first we want to create a list of adjacent units for the starting square
		#and then create a list of adjacent units for the destination square
		#all units in the first list but not the second list get an attack of opportunity
		#provided they have not already taken that reaction this turn
		
		if 'cunning action' in self.traits: #this trait avoids opportunity attacks
			return
		
		first_list = []
		second_list = []
		
		for actor in actors:
			if actor != self.owner:
				if actor.fighter:
					if actor.fighter.opportunity_attack is False:
						if actor.fighter.faction != self.faction and actor.fighter.faction != 'neutral' and self.faction != 'neutral':
							if not is_incapacitated(actor):
								if actor.can_see_object(self.owner):
									if actor.distance_to(self.owner) < 2:
										first_list.append(actor)
									if actor.distance(self.owner.x + dx, self.owner.y + dy) < 2:
										second_list.append(actor)
							
		for actor in first_list:
			if actor not in second_list:
				if actor.fighter:
					for condition in actor.fighter.conditions:
						if condition.name == 'invisibility':
							return #don't take opportunity attacks while invisible because it cancels the effect - creatures should deliberately take actions to break this
					actor.fighter.attack(self.owner, opportunity_attack=True)
					actor.fighter.opportunity_attack = True

			
class BasicMonster:
	memory_x = None
	memory_y = None
	broken_los = True
	target_monster = None
	focus = None

	def pay_attention(self, x, y):
		(self.memory_x, self.memory_y) = (x, y)
	
	#AI for a basic monster.
	def take_turn(self):
		#a basic monster takes its turn. if you can see it, it can see you (before taking into account view distances)
		monster = self.owner
		monster.has_swapped = False #reset this variable for each turn
		#first check if unconscious or otherwise incapacitated
		#first check if unconscious or otherwise incapacitated
		if is_incapacitated(monster):
			return #take no action if knocked out
			
		monster.flavour_text_check()
			
		#find closest monster in sight and attack it!
		if self.target_monster:
			if self.target_monster.fighter is None or is_unconscious(self.target_monster):
				self.target_monster = None #don't go after the dead or dying
				
		if self.target_monster:
			if self.target_monster.fighter:
				if not monster.can_see_object(self.target_monster):
					self.target_monster = None #don't pursue a target we can't see
				
		#loop through all available objects looking for a closer target - might need to adjust this to make sneak attacks more viable
		for actor in actors:
			if not is_unconscious(actor):
				if actor.fighter:
					faction_test = True
					if actor.fighter.faction == monster.fighter.faction: 
						faction_test = False #we don't want to attack our own faction
					if actor.fighter.faction == 'player' and monster.fighter.faction == 'neutral': #special case - neutrals should not attack the player
						faction_test = False
					if faction_test:
						if monster.can_see_object(actor) and actor.fighter.hp > 0:
							if self.target_monster == None: 
								self.target_monster = actor
							else:
								if actor.distance_to(monster) < self.target_monster.distance_to(monster):
									self.target_monster = actor
		if self.target_monster is not None and monster.can_see_object(self.target_monster):
			self.pay_attention(self.target_monster.x, self.target_monster.y)
			self.broken_los = False
			#move towards player if far away
			if monster.distance_to(self.target_monster) >= 2:
				monster.move_towards(self.target_monster.x, self.target_monster.y)

			#close enough, attack! (if the target is still alive)
			elif self.target_monster.fighter.hp > 0:
				monster.fighter.attack(self.target_monster)
	
		elif self.memory_x != None and self.memory_y != None and monster.distance(self.memory_x, self.memory_y) > 0: 
			#if can't see target but has a memory of target
			self.broken_los = True
			monster.move_towards(self.memory_x, self.memory_y)
				
		if (monster.x == self.memory_x and monster.y == self.memory_y) or random.randint(0, 100) > AI_INTEREST:
			self.broken_los = True
			self.memory_x = None
			self.memory_y = None

		if self.focus is None:
			if self.memory_x == None or self.memory_y == None: #fake a memory so the monster wanders to location in line of sight
				count = 0 
				while True:
					count += 1
					x = random.randint(monster.x - 10, monster.x + 10)
					y = random.randint(monster.y - 10, monster.y + 10)
					if can_walk_between(monster.x, monster.y, x, y) or count > 10: break
				self.broken_los = True
				self.memory_x = x
				self.memory_y = y
		else:
			count = 0
			while True:
				count += 1
				x = random.randint(self.focus[0] - 5, self.focus[0] + 5)
				y = random.randint(self.focus[1] - 5, self.focus[1] + 5)
				if can_walk_between(monster.x, monster.y, x, y) or count > 10: break
			self.broken_los = True
			self.memory_x = x
			self.memory_y = y
 
class MagicMonster:
	memory_x = None
	memory_y = None
	broken_los = True
	target_monster = None
	focus = None

	def pay_attention(self, x, y):
		(self.memory_x, self.memory_y) = (x, y)
		
	def move_towards_or_swap(self, x, y):
		test_object = None
		if x is None: return
		dx = x - self.owner.x
		dy = y - self.owner.y
		ddx = 0 
		ddy = 0
		if dx > 0:
			ddx = 1
		elif dx < 0:
			ddx = -1
		if dy > 0:
			ddy = 1
		elif dy < 0:
			ddy = -1
		next_step_x = self.owner.x + ddx
		next_step_y = self.owner.y + ddy
		if not is_blocked(next_step_x, next_step_y):
			self.owner.move_towards(next_step_x, next_step_y)
			return
		if is_blocked(next_step_x, next_step_y) and is_openable(next_step_x, next_step_y):
			map[next_step_x][next_step_y].open()
			return
		
		#for actor in actors:
		#	if actor.x == next_step_x and actor.y == next_step_y:
		#		test_object = actor
		
		test_object = lookup_map.get((next_step_x, next_step_y))
				
		if test_object is not None:
			if test_object.fighter:
				if test_object.fighter.faction == self.owner.fighter.faction and test_object != self.owner and not test_object.has_swapped:
					if not (test_object == player and not is_incapacitated(player)): #we don't want to let AI's swap with the player unless the player is out of action
						self.owner.swap_place(test_object)
						self.owner.has_swapped = True #this is to make sure npc's don't just swap places over and over again
						test_object.has_swapped = True
						return
		self.owner.move_towards(x, y)
			
	def available_spells(self):
		#return a list of spells for which there are available spell slots
		monster = self.owner 
		available_spells = []
		for spell in monster.fighter.spells:
			level = None
			if spell in WIZARD_1 or spell in CLERIC_1: level = 1
			if spell in WIZARD_2 or spell in CLERIC_2: level = 2
			if spell in WIZARD_3 or spell in CLERIC_3: level = 3
			if spell in WIZARD_4 or spell in CLERIC_4: level = 4
			if spell in WIZARD_5 or spell in CLERIC_5: level = 5
			if spell in WIZARD_6 or spell in CLERIC_6: level = 6
			if spell in WIZARD_7 or spell in CLERIC_7: level = 7
			if spell in WIZARD_8 or spell in CLERIC_8: level = 8
			if spell in WIZARD_9 or spell in CLERIC_9: level = 9
			if level is None: #either a cantrip or a unique spell without a slot
				available_spells.append(spell)
			if level is not None:
				if monster.fighter.spell_slots[level-1] > 0: #we have an available spell slot
					available_spells.append(spell)
		return available_spells
		
	def allies_in_sight(self):
		#return a list of allies within line of sight including self
		monster = self.owner
		allies = []
		for actor in actors:
			if actor.fighter:
				if actor.fighter.faction == monster.fighter.faction:
					if monster.can_see_object(actor):
						allies.append(actor)
		return allies
	
	#AI for a basic monster.
	def take_turn(self):
		monster = self.owner
		monster.has_swapped = False #reset this variable for each turn
		#first check if unconscious or otherwise incapacitated
		if is_incapacitated(monster):
			return #take no action if knocked out
			
		monster.flavour_text_check()
			
		#steal the fov for a moment so the monster can look around in a more CPU intensive way than normal monsters
		fov_map.compute_fov(monster.x, monster.y)
		#special case if someone has changed factions - no longer fight them
		if self.target_monster is not None:
			if self.target_monster.fighter:
				if self.target_monster.fighter.faction == monster.fighter.faction:
					self.target_monster = None
				if self.target_monster is not None:
					if not monster.can_see_object(self.target_monster):
						self.target_monster = None #don't pursue a target we can't see
		if self.target_monster:
			if self.target_monster.fighter is None or is_unconscious(self.target_monster):
				self.target_monster = None #don't go after the dead or dying
				
		available_spells = self.available_spells()
		allies_in_sight = self.allies_in_sight()
				
		#loop through all available objects looking for a closer target - might need to adjust this to make sneak attacks more viable
		for actor in actors:
			if not is_unconscious(actor):
				if actor.fighter:
					faction_test = True
					if actor.fighter.faction == monster.fighter.faction: 
						faction_test = False #we don't want to attack our own faction
					if actor.fighter.faction == 'player' and monster.fighter.faction == 'neutral': #special case - neutrals should not attack the player
						faction_test = False
					if faction_test:
						if monster.can_see_object(actor) and actor.fighter.hp > 0:
							if self.target_monster == None: 
								self.target_monster = actor
							else:
								if actor.distance_to(monster) < self.target_monster.distance_to(monster):
									self.target_monster = actor
									
		if self.target_monster is not None and self.target_monster.fighter:
			self.pay_attention(self.target_monster.x, self.target_monster.y)

			if monster.distance_to(self.target_monster) < 2: #we are in melee range, so let's fight hand to hand - chance to use close range spells if they are options
				if 'shocking grasp' in available_spells:
					if random.randint(1, 10) <= 5: #50% chance
						cast_shocking_grasp(monster, self.target_monster)
						monster.fighter.use_spell_slot('shocking grasp')
						return
				if 'inflict wounds' in available_spells:
					if random.randint(1, 10) <= 5: #50% chance
						cast_inflict_wounds(monster, self.target_monster)
						monster.fighter.use_spell_slot('inflict wounds')
						return
				monster.fighter.attack(self.target_monster)
				return
			else: #at a distance, so we don't want to close in on them, but we want to use long-range spells to attack
				if 'fire bolt' in available_spells:
					if random.randint(1, 10) <= 3: #30% chance
						cast_fire_bolt(monster, self.target_monster)
						return
				if 'sacred flame' in available_spells:
					if random.randint(1, 10) <= 3: #30% chance
						cast_sacred_flame(monster, self.target_monster)
						return
				if 'magic missile' in available_spells:
					if random.randint(1, 10) <= 2: #20% chance
						cast_magic_missile(monster, self.target_monster)
						monster.fighter.use_spell_slot('magic missile')
						return
				if 'fireball' in available_spells:
					if random.randint(1, 10) <= 3: #30% chance
						if monster.distance_to(self.target_monster) > 4: #don't use fireball too close
							test = False #need to check if any allies will get caught in blast
							for ally in allies_in_sight:
								if ally.distance_to(self.target_monster) < 4: test = True
							if not test:
								cast_fireball(monster, self.target_monster)
								monster.fighter.use_spell_slot('fireball')
								return
				elif 'cure wounds' in available_spells:
					target = None
					for ally in allies_in_sight:
						if ally.fighter:
							if ally.distance_to(monster) < 2: #need to be 1 square away
								if ally.fighter.hp <= ally.fighter.max_hp // 4: #25% health
									target = ally
					if target is not None:
						if random.randint(1, 10) <= 5: #50% chance
							cast_cure_wounds(monster, target)
							monster.fighter.use_spell_slot('cure wounds')
							return
				return

		if self.memory_x is not None: #this should be a memory of an enemy
			if (self.memory_x == monster.x and self.memory_y == monster.y) or random.randint(0, 100) > AI_INTEREST: #reset if we are on the memory or we get bored
				self.memory_x = None
				self.memory_y = None
			else:
				test_x = monster.x
				test_y = monster.y
				monster.move_towards(self.memory_x, self.memory_y)
				if monster.x == test_x and monster.y == test_y: #this means we didnt move this turn
					self.memory_x = None
					self.memory_y = None
			return

		#check to see if we can heal and if so, is there someone to heal
		if 'cure wounds' in available_spells:
			for ally in allies_in_sight:
				if ally.fighter:
					if ally.fighter.hp <= ally.fighter.max_hp // 4: #25% health
						if ally.distance_to(monster) >= 2:
							path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
							tcod.path_compute(path, monster.x, monster.y, ally.x, ally.y)
							(mx, my) = tcod.path_walk(path, True)
							if mx is not None:
								self.owner.move_towards(mx, my)
							return
						else:
							cast_cure_wounds(monster, ally)
							return


		if self.focus is None:
			if self.memory_x == None or self.memory_y == None: #fake a memory so the monster wanders to location in line of sight
				count = 0
				while True:
					count += 1
					x = random.randint(monster.x - 10, monster.x + 10)
					y = random.randint(monster.y - 10, monster.y + 10)
					if can_walk_between(monster.x, monster.y, x, y) or count > 10: break
				self.broken_los = True
				self.memory_x = x
				self.memory_y = y
		else:
			count = 0
			while True:
				count += 1
				x = random.randint(self.focus[0] - 5, self.focus[0] + 5)
				y = random.randint(self.focus[1] - 5, self.focus[1] + 5)
				if can_walk_between(monster.x, monster.y, x, y) or count > 10: break
			self.broken_los = True
			self.memory_x = x
			self.memory_y = y

class RangedMonster:
	memory_x = None
	memory_y = None
	broken_los = True
	target_monster = None
	focus = None

	def pay_attention(self, x, y):
		(self.memory_x, self.memory_y) = (x, y)
		
	def move_towards_or_swap(self, x, y):
		test_object = None
		if x is None: return
		dx = x - self.owner.x
		dy = y - self.owner.y
		ddx = 0 
		ddy = 0
		if dx > 0:
			ddx = 1
		elif dx < 0:
			ddx = -1
		if dy > 0:
			ddy = 1
		elif dy < 0:
			ddy = -1
		next_step_x = self.owner.x + ddx
		next_step_y = self.owner.y + ddy
		if not is_blocked(next_step_x, next_step_y):
			self.owner.move_towards(next_step_x, next_step_y)
			return
		if is_blocked(next_step_x, next_step_y) and is_openable(next_step_x, next_step_y):
			map[next_step_x][next_step_y].open()
			return
		
		#for actor in actors:
		#	if actor.x == next_step_x and actor.y == next_step_y:
		#		test_object = actor
		
		test_object = lookup_map.get((next_step_x, next_step_y))
		
		if test_object is not None:
			if test_object.fighter:
				if test_object.fighter.faction == self.owner.fighter.faction and test_object != self.owner and not test_object.has_swapped:
					if not (test_object == player and not is_incapacitated(player)): #we don't want to let AI's swap with the player unless the player is out of action
						self.owner.swap_place(test_object)
						self.owner.has_swapped = True #this is to make sure npc's don't just swap places over and over again
						test_object.has_swapped = True
						return
		self.owner.move_towards(x, y)
	
	#AI for a basic monster.
	def take_turn(self):
		#a basic monster takes its turn. if you can see it, it can see you (before taking into account view distances)
		monster = self.owner
		monster.has_swapped = False #reset this variable for each turn
		#first check if unconscious or otherwise incapacitated
		#first check if unconscious or otherwise incapacitated
		if is_incapacitated(monster):
			return #take no action if knocked out
			
		monster.flavour_text_check()
			
		#find closest monster in sight and attack it!
		if self.target_monster:
			if self.target_monster.fighter is None or is_unconscious(self.target_monster):
				self.target_monster = None #don't go after the dead or dying
				
		if self.target_monster:
			if self.target_monster.fighter:
				if not monster.can_see_object(self.target_monster):
					self.target_monster = None #don't pursue a target we can't see
				
		#loop through all available objects looking for a closer target - might need to adjust this to make sneak attacks more viable
		for actor in actors:
			if not is_unconscious(actor):
				if actor.fighter:
					faction_test = True
					if actor.fighter.faction == monster.fighter.faction: 
						faction_test = False #we don't want to attack our own faction
					if actor.fighter.faction == 'player' and monster.fighter.faction == 'neutral': #special case - neutrals should not attack the player
						faction_test = False
					if faction_test:
						if monster.can_see_object(actor) and actor.fighter.hp > 0:
							if self.target_monster == None: 
								self.target_monster = actor
							else:
								if actor.distance_to(monster) < self.target_monster.distance_to(monster):
									self.target_monster = actor
		if self.target_monster is not None and monster.can_see_object(self.target_monster):
			self.pay_attention(self.target_monster.x, self.target_monster.y)
			self.broken_los = False
			#move towards player if far away
			if monster.distance_to(self.target_monster) >= 2:
				monster.move_towards(self.target_monster.x, self.target_monster.y)

			#close enough, attack! (if the target is still alive)
			elif self.target_monster.fighter.hp > 0:
				monster.fighter.attack(self.target_monster)
	
		elif self.memory_x != None and self.memory_y != None and monster.distance(self.memory_x, self.memory_y) > 0: 
			#if can't see target but has a memory of target
			self.broken_los = True
			monster.move_towards(self.memory_x, self.memory_y)
				
		if (monster.x == self.memory_x and monster.y == self.memory_y) or random.randint(0, 100) > AI_INTEREST:
			self.broken_los = True
			self.memory_x = None
			self.memory_y = None

		if self.focus is None:
			if self.memory_x == None or self.memory_y == None: #fake a memory so the monster wanders to location in line of sight
				count = 0
				while True:
					count += 1
					x = random.randint(monster.x - 10, monster.x + 10)
					y = random.randint(monster.y - 10, monster.y + 10)
					if can_walk_between(monster.x, monster.y, x, y) or count > 10: break
				self.broken_los = True
				self.memory_x = x
				self.memory_y = y
		else:
			count = 0
			while True:
				count += 1
				x = random.randint(self.focus[0] - 5, self.focus[0] + 5)
				y = random.randint(self.focus[1] - 5, self.focus[1] + 5)
				if can_walk_between(monster.x, monster.y, x, y) or count > 10: break
			self.broken_los = True
			self.memory_x = x
			self.memory_y = y
			
class ConfusedMonster:
	#AI for a temporarily confused monster (reverts to previous AI after a while).
	def __init__(self, old_ai, num_turns=10):
		self.old_ai = old_ai
		self.num_turns = num_turns
 
	def take_turn(self):
		#first check if unconscious or otherwise incapacitated
		if is_incapacitated(self.owner):
			return #take no action if knocked out
		if self.num_turns > 0:	#still confused...
			#move in a random direction, and decrease the number of turns confused
			self.owner.move(random.randint(-1, 1), random.randint(-1, 1))
			self.num_turns -= 1
 
		else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
			self.owner.ai = self.old_ai
			message(self.owner.name_for_printing() + ' is no longer confused.', 'white')
			
class HeldMonster:
	#AI for a humanoid affected by the hold person spell
	def __init__(self, old_ai, num_turns=20, difficulty=10):
		self.old_ai = old_ai
		self.num_turns = num_turns
		self.difficulty = difficulty
 
	def take_turn(self):
		if self.num_turns > 0:	#still held...
			#do a wisdom check 
			result = self.owner.fighter.saving_throw('wisdom', self.difficulty)
			if result:
				self.num_turns = 0 #end the effect
			else:
				self.num_turns -= 1
 
		if self.num_turns <= 0:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
			self.owner.ai = self.old_ai
			message(self.owner.name_for_printing() + ' is no longer held.', 'white')
			
class ScaredMonster:
	#AI for a temporarily scared monster (reverts to previous AI after a while).
	def __init__(self, old_ai, scared_of, num_turns):
		self.old_ai = old_ai
		self.num_turns = num_turns
		self.scared_of = scared_of
 
	def take_turn(self):
		#first check if unconscious or otherwise incapacitated
		if is_incapacitated(self.owner):
			return #take no action if knocked out
		if self.num_turns > 0:	#still scared...
			#move in a random direction, and decrease the number of turns confused
			self.owner.move_away_from(self.scared_of.x, self.scared_of.y)
			self.num_turns -= 1
 
		else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
			self.owner.ai = self.old_ai
			if player.can_see_object(self.owner):
				message(self.owner.name_for_printing() + ' is no longer scared.', 'white')
			
class CompanionMonster:
	memory_x = None
	memory_y = None
	broken_los = True
	target_monster = None
	current_order = None
	current_order_x = None
	current_order_y = None
	can_talk = True
	can_revive = True
	can_path_find = True
	path_finding_chance = 1
		
	def __init__(self, master, loyalty):
		self.master = master #link it to a master object
		self.loyalty = loyalty #an arbitrary value to determine how close it'll stay to master

	def pay_attention(self, x, y):
		(self.memory_x, self.memory_y) = (x, y)
	
	def move_towards_or_swap(self, x, y):
		test_object = None
		if x is None: return
		dx = x - self.owner.x
		dy = y - self.owner.y
		ddx = 0 
		ddy = 0
		if dx > 0:
			ddx = 1
		elif dx < 0:
			ddx = -1
		if dy > 0:
			ddy = 1
		elif dy < 0:
			ddy = -1
		next_step_x = self.owner.x + ddx
		next_step_y = self.owner.y + ddy
		if not is_blocked(next_step_x, next_step_y):
			self.owner.move_towards(next_step_x, next_step_y)
			return
		if is_blocked(next_step_x, next_step_y) and is_openable(next_step_x, next_step_y):
			map[next_step_x][next_step_y].open()
			return
		
		#for actor in actors:
		#	if actor.x == next_step_x and actor.y == next_step_y:
		#		test_object = actor
		
		test_object = lookup_map.get((next_step_x, next_step_y))
		
		if test_object is not None:
			if test_object.fighter:
				if test_object.fighter.faction == self.owner.fighter.faction and test_object != self.owner and not test_object.has_swapped:
					if not (test_object == player and not is_incapacitated(player)): #we don't want to let AI's swap with the player unless the player is out of action
						self.owner.swap_place(test_object)
						self.owner.has_swapped = True #this is to make sure npc's don't just swap places over and over again
						test_object.has_swapped = True
						return
		self.owner.move_towards(x, y)
	
	#AI for a basic monster.
	def take_turn(self):
		companion = self.owner
		companion.has_swapped = False #reset this variable for each turn
		#first check if unconscious or otherwise incapacitated
		if is_incapacitated(companion):
			return #take no action if knocked out
			
		companion.flavour_text_check()	
			
		#steal the fov for a moment so the companion can look around in a more CPU intensive way than normal monsters
		fov_map.compute_fov(companion.x, companion.y)
		#special case if someone has changed factions - no longer fight them
		if self.target_monster is not None:
			if self.target_monster.fighter:
				if self.target_monster.fighter.faction == companion.fighter.faction:
					self.target_monster = None
				if self.target_monster is not None:
					if not companion.can_see_object(self.target_monster):
						self.target_monster = None #don't pursue a target we can't see	
		if self.target_monster:
			if self.target_monster.fighter is None or is_unconscious(self.target_monster):
				self.target_monster = None #don't go after the dead or dying
				
		#loop through all available objects looking for a closer target - might need to adjust this to make sneak attacks more viable
		for actor in actors:
			if not is_unconscious(actor):
				if actor.fighter:
					faction_test = True
					if actor.fighter.faction == companion.fighter.faction: 
						faction_test = False #we don't want to attack our own faction
					if actor.fighter.faction == 'player' and companion.fighter.faction == 'neutral': #special case - neutrals should not attack the player
						faction_test = False
					if actor.fighter.faction == 'neutral' and companion.fighter.faction == 'player': #special case - player allies should not attack neutrals
						faction_test = False
					if faction_test:
						if companion.can_see_object(actor) and actor.fighter.hp > 0:
							if self.target_monster == None: 
								self.target_monster = actor
							else:
								if actor.distance_to(companion) < self.target_monster.distance_to(companion):
									self.target_monster = actor
		if self.target_monster is not None and self.target_monster.fighter:
			self.pay_attention(self.target_monster.x, self.target_monster.y)
			if self.can_talk:
				if fov_map.fov[self.master.y, self.master.x]:
					talk = random.randint(1, 50)
					if talk == 1:
						message(self.owner.name_for_printing() + ' lets out a war cry.')
					elif talk == 2:
						message(self.owner.name_for_printing() + ' shouts "Stay away from my master you beast!"')
					elif talk == 3:
						message(self.owner.name_for_printing() + ' brandishes his weapon menacingly.')
			if companion.distance_to(self.target_monster) >= 2: 
				if self.current_order == 'defend': #defend means that we don't walk towards enemies but will attack if they are close enough to reach
					return
				else:
					self.move_towards_or_swap(self.target_monster.x, self.target_monster.y)
					return
			elif companion.distance_to(self.target_monster) < 2:
				companion.fighter.attack(self.target_monster)
				return
		if self.current_order_x is not None: #this means we have an order with a location involved so we should focus on that
			companion.move_towards(self.current_order_x, self.current_order_y)
			return
		if self.memory_x is not None: #this should be a memory of an enemy
			if (self.memory_x == companion.x and self.memory_y == companion.y) or random.randint(0, 100) > AI_INTEREST: #reset if we are on the memory or we get bored
				self.memory_x = None
				self.memory_y = None
			else:
				test_x = companion.x
				test_y = companion.y
				companion.move_towards(self.memory_x, self.memory_y)
				if companion.x == test_x and companion.y == test_y: #this means we didnt move this turn
					self.memory_x = None
					self.memory_y = None
			return
		if self.can_talk:
			if fov_map.fov[self.master.y, self.master.x]: #if can see master but no enemies around then maybe say something
				talk = random.randint(1, 1000)
				if talk == 1:
					message(self.owner.name_for_printing() + ' says: ' + self.master.name + ', you are my only friend.')
				elif talk == 2:
					message(self.owner.name_for_printing() + ' says: Be careful, I think I hear something nearby...')
				elif talk == 3:
					message(self.owner.name_for_printing() + ' says: Look after yourself ' + self.master.name + ', I need you.')
		#check to see if there is an ally we need to revive
		if self.can_revive:
			for actor in actors:
				if actor.fighter:
					if actor.fighter.faction == companion.fighter.faction:
						if is_unconscious(actor):
							if companion.can_see_object(actor):
								if actor.distance_to(companion) >= 2:
									#path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
									#tcod.path_compute(path, companion.x, companion.y, actor.x, actor.y)
									#(mx, my) = tcod.path_walk(path, True)
									#self.move_towards_or_swap(mx, my)
									self.move_towards_or_swap(actor.x, actor.y)
								else:
									monster_revive(actor, companion)
		if companion.can_see_object(self.master):
			companion.move_towards(self.master.x, self.master.y)
		else:
			#we are out of sight of the master so pathfind to master
			dx = self.master.x
			dy = self.master.y
			mx = None
			my = None
			if self.can_path_find:
				test = False
				if random.randint(1, self.path_finding_chance) == 1:
					for i in range(10): #find unblocked spot near target
						cx = dx + random.randint(-2, +2)
						cy = dy + random.randint(-2, +2)
						if 2 < cx < MAP_WIDTH-3 and 3 < cy < MAP_HEIGHT-3:
							if not is_blocked(cx, cy):
								test = True
								break
					if test:
						path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
						tcod.path_compute(path, companion.x, companion.y, cx, cy)
						(mx, my) = tcod.path_walk(path, True)
			if mx is not None and my is not None: 
				self.move_towards_or_swap(mx, my)
			
class CompanionRangedMonster:
	memory_x = None
	memory_y = None
	broken_los = True
	target_monster = None
	current_order = None
	current_order_x = None
	current_order_y = None
	can_talk = True
	can_revive = True
	can_path_find = True
	path_finding_chance = 1
		
	def __init__(self, master, loyalty):
		self.master = master #link it to a master object
		self.loyalty = loyalty #an arbitrary value to determine how close it'll stay to master

	def pay_attention(self, x, y):
		(self.memory_x, self.memory_y) = (x, y)
	
	def move_towards_or_swap(self, x, y):
		test_object = None
		if x is None: return
		dx = x - self.owner.x
		dy = y - self.owner.y
		ddx = 0 
		ddy = 0
		if dx > 0:
			ddx = 1
		elif dx < 0:
			ddx = -1
		if dy > 0:
			ddy = 1
		elif dy < 0:
			ddy = -1
		next_step_x = self.owner.x + ddx
		next_step_y = self.owner.y + ddy
		if not is_blocked(next_step_x, next_step_y):
			self.owner.move_towards(next_step_x, next_step_y)
			return
		if is_blocked(next_step_x, next_step_y) and is_openable(next_step_x, next_step_y):
			map[next_step_x][next_step_y].open()
			return
		
		#for actor in actors:
		#	if actor.x == next_step_x and actor.y == next_step_y:
		#		test_object = actor
		
		test_object = lookup_map.get((next_step_x, next_step_y))
		
		if test_object is not None:
			if test_object.fighter:
				if test_object.fighter.faction == self.owner.fighter.faction and test_object != self.owner and not test_object.has_swapped:
					if not (test_object == player and not is_incapacitated(player)): #we don't want to let AI's swap with the player unless the player is out of action
						self.owner.swap_place(test_object)
						self.owner.has_swapped = True #this is to make sure npc's don't just swap places over and over again
						test_object.has_swapped = True
						return
		self.owner.move_towards(x, y)
		
	#AI for a basic monster.
	def take_turn(self):
		companion = self.owner
		companion.has_swapped = False #reset this variable for each turn
		#first check if unconscious or otherwise incapacitated
		if is_incapacitated(companion):
			return #take no action if knocked out
		
		companion.flavour_text_check()
			
		#steal the fov for a moment so the companion can look around in a more CPU intensive way than normal monsters
		fov_map.compute_fov(companion.x, companion.y)
		#special case if someone has changed factions - no longer fight them
		if self.target_monster is not None:
			if self.target_monster.fighter:
				if self.target_monster.fighter.faction == companion.fighter.faction:
					self.target_monster = None
				if self.target_monster is not None:
					if not companion.can_see_object(self.target_monster):
						self.target_monster = None #don't pursue a target we can't see
		if self.target_monster:
			if self.target_monster.fighter is None or is_unconscious(self.target_monster):
				self.target_monster = None #don't go after the dead or dying
				
		#loop through all available objects looking for a closer target - might need to adjust this to make sneak attacks more viable
		for actor in actors:
			if not is_unconscious(actor):
				if actor.fighter:
					faction_test = True
					if actor.fighter.faction == companion.fighter.faction: 
						faction_test = False #we don't want to attack our own faction
					if actor.fighter.faction == 'player' and companion.fighter.faction == 'neutral': #special case - neutrals should not attack the player
						faction_test = False
					if actor.fighter.faction == 'neutral' and companion.fighter.faction == 'player': #special case - player allies should not attack neutrals
						faction_test = False
					if faction_test:
						if companion.can_see_object(actor) and actor.fighter.hp > 0:
							if self.target_monster == None: 
								self.target_monster = actor
							else:
								if actor.distance_to(companion) < self.target_monster.distance_to(companion):
									self.target_monster = actor
		if self.target_monster is not None and self.target_monster.fighter:
			self.pay_attention(self.target_monster.x, self.target_monster.y)
			if self.can_talk:
				if fov_map.fov[self.master.y, self.master.x]:
					talk = random.randint(1, 50)
					if talk == 1:
						message(self.owner.name_for_printing() + ' lets out a war cry.')
					elif talk == 2:
						message(self.owner.name_for_printing() + ' shouts "Stay away from my master you beast!"')
					elif talk == 3:
						message(self.owner.name_for_printing() + ' brandishes his weapon menacingly.')
						
			if companion.distance_to(self.target_monster) < 2: #we are in melee range, so let's fight hand to hand
				companion.fighter.attack(self.target_monster)
				return
			else: #at a distance, so we don't want to close in on them, but we want to use ranged combat to attack
				if random.randint(1, 10) <= 5: #50% chance
					companion.fighter.attack(self.target_monster, use_ranged_stats=True)
				return		
				
		if self.current_order_x is not None: #this means we have an order with a location involved so we should focus on that
			companion.move_towards(self.current_order_x, self.current_order_y)
			return
			
		if self.memory_x is not None: #this should be a memory of an enemy
			if (self.memory_x == companion.x and self.memory_y == companion.y) or random.randint(0, 100) > AI_INTEREST: #reset if we are on the memory or we get bored
				self.memory_x = None
				self.memory_y = None
			else:
				test_x = companion.x
				test_y = companion.y
				companion.move_towards(self.memory_x, self.memory_y)
				if companion.x == test_x and companion.y == test_y: #this means we didnt move this turn
					self.memory_x = None
					self.memory_y = None
			return
		if self.can_talk:
			if fov_map.fov[self.master.y, self.master.x]: #if can see master but no enemies around then maybe say something
				talk = random.randint(1, 1000)
				if talk == 1:
					message(self.owner.name_for_printing() + ' says: ' + self.master.name + ', you are my only friend.')
				elif talk == 2:
					message(self.owner.name_for_printing() + ' says: Be careful, I think I hear something nearby...')
				elif talk == 3:
					message(self.owner.name_for_printing() + ' says: Look after yourself ' + self.master.name + ', I need you.')
		#check to see if there is an ally we need to revive
		if self.can_revive:
			for actor in actors:
				if actor.fighter:
					if actor.fighter.faction == companion.fighter.faction:
						if is_unconscious(actor):
							if companion.can_see_object(actor):
								if actor.distance_to(companion) >= 2:
									#path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
									#tcod.path_compute(path, companion.x, companion.y, actor.x, actor.y)
									#(mx, my) = tcod.path_walk(path, True)
									#self.move_towards_or_swap(mx, my)
									self.move_towards_or_swap(actor.x, actor.y)
								else:
									monster_revive(actor, companion)
		if companion.can_see_object(self.master):
			companion.move_towards(self.master.x, self.master.y)
		else:
			#we are out of sight of the master so pathfind to master
			dx = self.master.x
			dy = self.master.y
			mx = None
			my = None
			if self.can_path_find:
				test = False
				if random.randint(1, self.path_finding_chance) == 1:
					for i in range(10): #find unblocked spot near target
						cx = dx + random.randint(-2, +2)
						cy = dy + random.randint(-2, +2)
						if 2 < cx < MAP_WIDTH-3 and 3 < cy < MAP_HEIGHT-3:
							if not is_blocked(cx, cy):
								test = True
								break
					if test:
						path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
						tcod.path_compute(path, companion.x, companion.y, cx, cy)
						(mx, my) = tcod.path_walk(path, True)
			if mx is not None and my is not None: 
				self.move_towards_or_swap(mx, my)
			
class CompanionMagicMonster:
	memory_x = None
	memory_y = None
	broken_los = True
	target_monster = None
	current_order = None
	current_order_x = None
	current_order_y = None
	can_talk = True
	can_revive = True
	can_path_find = True
	path_finding_chance = 1
		
	def __init__(self, master, loyalty):
		self.master = master #link it to a master object
		self.loyalty = loyalty #an arbitrary value to determine how close it'll stay to master

	def pay_attention(self, x, y):
		(self.memory_x, self.memory_y) = (x, y)
	
	def move_towards_or_swap(self, x, y):
		test_object = None
		if x is None: return
		dx = x - self.owner.x
		dy = y - self.owner.y
		ddx = 0 
		ddy = 0
		if dx > 0:
			ddx = 1
		elif dx < 0:
			ddx = -1
		if dy > 0:
			ddy = 1
		elif dy < 0:
			ddy = -1
		next_step_x = self.owner.x + ddx
		next_step_y = self.owner.y + ddy
		if not is_blocked(next_step_x, next_step_y):
			self.owner.move_towards(next_step_x, next_step_y)
			return
		if is_blocked(next_step_x, next_step_y) and is_openable(next_step_x, next_step_y):
			map[next_step_x][next_step_y].open()
			return
		
		#for actor in actors:
		#	if actor.x == next_step_x and actor.y == next_step_y:
		#		test_object = actor
		
		test_object = lookup_map.get((next_step_x, next_step_y))
		
		if test_object is not None:
			if test_object.fighter:
				if test_object.fighter.faction == self.owner.fighter.faction and test_object != self.owner and not test_object.has_swapped:
					if not (test_object == player and not is_incapacitated(player)): #we don't want to let AI's swap with the player unless the player is out of action
						self.owner.swap_place(test_object)
						self.owner.has_swapped = True #this is to make sure npc's don't just swap places over and over again
						test_object.has_swapped = True
						return
		self.owner.move_towards(x, y)
	
	def available_spells(self):
		#return a list of spells for which there are available spell slots
		companion = self.owner 
		available_spells = []
		for spell in companion.fighter.spells:
			level = None
			if spell in WIZARD_1 or spell in CLERIC_1: level = 1
			if spell in WIZARD_2 or spell in CLERIC_2: level = 2
			if spell in WIZARD_3 or spell in CLERIC_3: level = 3
			if spell in WIZARD_4 or spell in CLERIC_4: level = 4
			if spell in WIZARD_5 or spell in CLERIC_5: level = 5
			if spell in WIZARD_6 or spell in CLERIC_6: level = 6
			if spell in WIZARD_7 or spell in CLERIC_7: level = 7
			if spell in WIZARD_8 or spell in CLERIC_8: level = 8
			if spell in WIZARD_9 or spell in CLERIC_9: level = 9
			if level is None: #either a cantrip or a unique spell without a slot
				available_spells.append(spell)
			if level is not None:
				if companion.fighter.spell_slots[level-1] > 0: #we have an available spell slot
					available_spells.append(spell)
		return available_spells
		
	def allies_in_sight(self):
		#return a list of allies within line of sight including self
		companion = self.owner
		allies = []
		for actor in actors:
			if actor.fighter:
				if actor.fighter.faction == companion.fighter.faction:
					if companion.can_see_object(actor):
						allies.append(actor)
		return allies
	
	#AI for a basic monster.
	def take_turn(self):
		companion = self.owner
		companion.has_swapped = False #reset this variable for each turn
		#first check if unconscious or otherwise incapacitated
		if is_incapacitated(companion):
			return #take no action if knocked out
			
		companion.flavour_text_check()
			
		#steal the fov for a moment so the companion can look around in a more CPU intensive way than normal monsters
		fov_map.compute_fov(companion.x, companion.y)
		#special case if someone has changed factions - no longer fight them
		if self.target_monster is not None:
			if self.target_monster.fighter:
				if self.target_monster.fighter.faction == companion.fighter.faction:
					self.target_monster = None
				if self.target_monster is not None:
					if not companion.can_see_object(self.target_monster):
						self.target_monster = None #don't pursue a target we can't see
		if self.target_monster:
			if self.target_monster.fighter is None or is_unconscious(self.target_monster):
				self.target_monster = None #don't go after the dead or dying
				
		available_spells = self.available_spells()
		allies_in_sight = self.allies_in_sight()
				
		#loop through all available objects looking for a closer target - might need to adjust this to make sneak attacks more viable
		for actor in actors:
			if not is_unconscious(actor):
				if actor.fighter:
					faction_test = True
					if actor.fighter.faction == companion.fighter.faction: 
						faction_test = False #we don't want to attack our own faction
					if actor.fighter.faction == 'player' and companion.fighter.faction == 'neutral': #special case - neutrals should not attack the player
						faction_test = False
					if actor.fighter.faction == 'neutral' and companion.fighter.faction == 'player': #special case - player allies should not attack neutrals
						faction_test = False
					if faction_test:
						if companion.can_see_object(actor) and actor.fighter.hp > 0:
							if self.target_monster == None: 
								self.target_monster = actor
							else:
								if actor.distance_to(companion) < self.target_monster.distance_to(companion):
									self.target_monster = actor
		if self.target_monster is not None and self.target_monster.fighter:
			self.pay_attention(self.target_monster.x, self.target_monster.y)
			if self.can_talk:
				if fov_map.fov[self.master.y, self.master.x]:
					talk = random.randint(1, 50)
					if talk == 1:
						message(self.owner.name_for_printing() + ' lets out a war cry.')
					elif talk == 2:
						message(self.owner.name_for_printing() + ' shouts "Stay away from my master you beast!"')
					elif talk == 3:
						message(self.owner.name_for_printing() + ' brandishes his weapon menacingly.')

			if companion.distance_to(self.target_monster) < 2: #we are in melee range, so let's fight hand to hand - chance to use close range spells if they are options
				if 'shocking grasp' in available_spells:
					if random.randint(1, 10) <= 5: #50% chance
						cast_shocking_grasp(companion, self.target_monster)
						companion.fighter.use_spell_slot('shocking grasp')
						return
				if 'inflict wounds' in available_spells:
					if random.randint(1, 10) <= 5: #50% chance
						cast_inflict_wounds(companion, self.target_monster)
						companion.fighter.use_spell_slot('inflict wounds')
						return
				companion.fighter.attack(self.target_monster)
				return
			else: #at a distance, so we don't want to close in on them, but we want to use long-range spells to attack
				if 'fire bolt' in available_spells:
					if random.randint(1, 10) <= 3: #30% chance
						cast_fire_bolt(companion, self.target_monster)
						return
				if 'sacred flame' in available_spells:
					if random.randint(1, 10) <= 3: #30% chance
						cast_sacred_flame(companion, self.target_monster)
						return
				if 'magic missile' in available_spells:
					if random.randint(1, 10) <= 2: #20% chance
						cast_magic_missile(companion, self.target_monster)
						companion.fighter.use_spell_slot('magic missile')
						return
				if 'fireball' in available_spells:
					if random.randint(1, 10) <= 3: #30% chance
						if companion.distance_to(self.target_monster) > 4: #don't use fireball too close
							test = False #need to check if any allies will get caught in blast
							for ally in allies_in_sight:
								if ally.distance_to(self.target_monster) < 4: test = True
							if not test:
								cast_fireball(companion, self.target_monster)
								companion.fighter.use_spell_slot('fireball')
								return
				elif 'cure wounds' in available_spells:
					target = None
					for ally in allies_in_sight:
						if ally.fighter:
							if ally.distance_to(companion) < 2: #need to be 1 square away
								if ally.fighter.hp <= ally.fighter.max_hp // 4: #25% health
									target = ally
					if target is not None:
						if random.randint(1, 10) <= 5: #50% chance
							cast_cure_wounds(companion, target)
							companion.fighter.use_spell_slot('cure wounds')
							return
				return

		if self.current_order_x is not None: #this means we have an order with a location involved so we should focus on that
			companion.move_towards(self.current_order_x, self.current_order_y)
			return
		if self.memory_x is not None: #this should be a memory of an enemy
			if (self.memory_x == companion.x and self.memory_y == companion.y) or random.randint(0, 100) > AI_INTEREST: #reset if we are on the memory or we get bored
				self.memory_x = None
				self.memory_y = None
			else:
				test_x = companion.x
				test_y = companion.y
				companion.move_towards(self.memory_x, self.memory_y)
				if companion.x == test_x and companion.y == test_y: #this means we didnt move this turn
					self.memory_x = None
					self.memory_y = None
			return
		if self.can_talk:
			if fov_map.fov[self.master.y, self.master.x]: #if can see master but no enemies around then maybe say something
				talk = random.randint(1, 1000)
				if talk == 1:
					message(self.owner.name_for_printing() + ' says: ' + self.master.name + ', you are my only friend.')
				elif talk == 2:
					message(self.owner.name_for_printing() + ' says: Be careful, I think I hear something nearby...')
				elif talk == 3:
					message(self.owner.name_for_printing() + ' says: Look after yourself ' + self.master.name + ', I need you.')
		#check to see if there is an ally we need to revive
		if self.can_revive:
			for ally in allies_in_sight:
				if is_unconscious(ally):
					if ally.distance_to(companion) >= 2:
						#path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
						#tcod.path_compute(path, companion.x, companion.y, ally.x, ally.y)
						#(mx, my) = tcod.path_walk(path, True)
						#self.move_towards_or_swap(mx, my)
						self.move_towards_or_swap(ally.x, ally.y)
						return
					else:
						monster_revive(ally, companion)
						return
		#check to see if we can heal and if so, is there someone to heal
		if 'cure wounds' in available_spells:
			for ally in allies_in_sight:
				if ally.fighter:
					if ally.fighter.hp <= ally.fighter.max_hp // 4: #25% health
						if ally.distance_to(companion) >= 2:
							self.move_towards_or_swap(ally.x, ally.y)
							return
						else:
							cast_cure_wounds(companion, ally)
							return
		if companion.can_see_object(self.master):
			companion.move_towards(self.master.x, self.master.y)
		else:
			#we are out of sight of the master so pathfind to master
			dx = self.master.x
			dy = self.master.y
			mx = None
			my = None
			if self.can_path_find:
				test = False
				if random.randint(1, self.path_finding_chance) == 1:
					for i in range(10): #find unblocked spot near target
						cx = dx + random.randint(-2, +2)
						cy = dy + random.randint(-2, +2)
						if 2 < cx < MAP_WIDTH-3 and 3 < cy < MAP_HEIGHT-3:
							if not is_blocked(cx, cy):
								test = True
								break
					if test:
						path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
						tcod.path_compute(path, companion.x, companion.y, cx, cy)
						(mx, my) = tcod.path_walk(path, True)
			if mx is not None and my is not None: 
				self.move_towards_or_swap(mx, my)
			
class Item:
	#an item that can be picked up and used.
	def __init__(self, use_function=None, max_charges=None):
		self.use_function = use_function
		self.traits = [] #used for permanent effects
		self.conditions = [] #used for temporary effects
		self.max_charges = max_charges
		self.charges = self.max_charges #used to record charges if necessary
		self.recharges = False
		self.special = None #used to record values for exotic effects
 
	def pick_up(self, monster):
		#add to the player's inventory and remove from the map
		if self.owner.name == 'gold coins':
			self.owner.gold += self.owner.quantity
		else:
			monster.inventory.append(self.owner)
		items.remove(self.owner)
		if monster != player: message(monster.name_for_printing() + ' picked up ' + self.owner.name_for_printing() + '.', 'white')

		#special case: automatically equip, if the corresponding equipment slot is unused
		#equipment = self.owner.equipment
		#if equipment and get_equipped_in_slot(monster, equipment.slot) is None and monster != player:
		#	equipment.equip(monster)
			
		#special case: if thrown weapon being recovered, automatically equip it
		if self.owner == player.last_quiver:
			if get_equipped_in_slot(player, 'quiver') is None:
				self.owner.equipment.equip(player)
			
		### special case for lit flammable items like torches on the floor
		if self.owner.equipment:
			if 'flammable' in self.owner.equipment.properties:
				for condition in self.conditions:
					if condition.name == 'illumination': #picking up an illuminated item
						if monster == player:
							message('You extinguish the torch as you stow it in your pack.', 'white')
						condition.remove_from_item(self.owner)
				
		### if the item has a quantity aspect, check the inventory for others and combine them by adding the quantity and destroying the other item
		if self.owner.quantity is not None:
			for item in monster.inventory:
				if item.name == self.owner.name and item != self.owner: #we've found a candidate for merging
					self.owner.quantity += item.quantity
					if item.equipment and self.owner.equipment:
						if item.equipment.is_equipped:
							self.owner.equipment.equip(monster) #this is because if the other item is equipped (such as a quiver of arrows) the merged item should also be equipped automatically
							item.equipment.dequip(monster)
					monster.inventory.remove(item)
 
	def drop(self, monster):
		#special case: if the object has the Equipment component, dequip it before dropping
		#we want to bypass the usual dequip function as a workaround so lit torches don't lose that status when being dropped with another exception for two-handed fighting 
		if self.owner.equipment:
			if self.owner.equipment.is_equipped: 
				if self.owner.name == 'torch':
					self.owner.equipment.is_equipped = None
				else:
					self.owner.equipment.dequip(monster)
 
		#add to the map and remove from the player's inventory. also, place it at the player's coordinates
		items.append(self.owner)
		monster.inventory.remove(self.owner)
		self.owner.x = monster.x
		self.owner.y = monster.y
		if monster != player: message(monster.name_for_printing() + ' dropped a ' + self.owner.name + '.', 'white')
 
	def use(self, monster):
		#special case: if the object has the Equipment component, the "use" action is to equip/dequip
		if self.owner.equipment:
			self.owner.equipment.toggle_equip(monster)
			return
 
		#just call the "use_function" if it is defined
		if self.use_function is None:
			message(self.owner.name_for_printing() + ' cannot be used.')
		else:
			if self.charges is None and self.owner.quantity is None: #this item doesn't need to worry about charges and can only be a single item
				if self.use_function(monster, self.owner) != 'cancelled':
					player.inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
			elif self.charges is not None:
				if self.charges >= 1:
					if self.use_function(monster, self.owner) != 'cancelled':
						self.charges -= 1
				else:
					message(self.owner.name_for_printing() + ' is out of charges.')
			elif self.owner.quantity is not None:
				if self.use_function(monster, self.owner) != 'cancelled':
					self.owner.use_quantity(monster)
				
class Equipment:
	#an object that can be equipped, yielding bonuses. automatically adds the Item component.
	def __init__(self, slot, num_dmg_die, dmg_die, ac, weight, properties, adds_trait=None, adds_proficiency=None, str_bonus=None, dex_bonus=None, con_bonus=None, int_bonus=None, wis_bonus=None, cha_bonus=None):
		self.num_dmg_die = num_dmg_die
		self.dmg_die = dmg_die
		self.ac = ac
		self.weight = weight
		self.properties = properties
		self.adds_trait = adds_trait #add this trait temporarily to the user when equipped - needs to be a list
		self.adds_proficiency = adds_proficiency
		
		self.str_bonus = str_bonus
		self.dex_bonus = dex_bonus
		self.con_bonus = con_bonus
		self.int_bonus = int_bonus
		self.wis_bonus = wis_bonus
		self.cha_bonus = cha_bonus
 
		self.slot = slot
		self.is_equipped = None

	def toggle_equip(self, monster):	 #toggle equip/dequip status
		if self.is_equipped:
			self.dequip(monster)
		else:
			self.equip(monster)
 
	def equip(self, monster):
		#if the slot is already being used, dequip whatever is there first
		slot = self.slot
		if monster == player and game_state == 'playing': #we don't want to do this during character generation
			if slot == 'main hand' and 'thrown' in self.properties: #check for thrown melee weapons and give player a choice as to which to use
				choice = menu('How do you want to use this item:', ['Melee weapon', 'Ammunition in quiver'], 30)
				if choice == 1: slot = 'quiver'
			if slot == 'main hand' and 'versatile' in self.properties: #check for versatile weapons and give player a choice as to how many hands to use
				choice = menu('How do you want to use this item:', ['Wield with one hand', 'Wield with two hands'], 30)
				if choice == 1: monster.versatile_weapon_with_two_hands = True
			if slot == 'main hand' and 'light' in self.properties: #check for light weapons and possible two weapon fighting
				main_hand = get_equipped_in_slot(monster, 'main hand')
				if main_hand is not None:
					if 'light' in main_hand.properties and not monster.two_weapon_fighting:
						choice = menu('How do you want to use this item:', ['Wield with main hand (one-weapon fighting)', 'Wield with off hand (two-weapon fighting)'], 45)
						if choice == 1: 
							monster.two_weapon_fighting = True
							slot = 'off hand'
		old_equipment = get_equipped_in_slot(monster, slot) 
		if old_equipment is not None:
			old_equipment.dequip(monster)
		if 'two-handed' in self.properties or ('versatile' in self.properties and monster.versatile_weapon_with_two_hands):
			off_hand = get_equipped_in_slot(monster, 'off hand')
			if off_hand is not None:
				off_hand.dequip(monster)
		if slot == 'off hand':
			main_hand = get_equipped_in_slot(monster, 'main hand')
			if main_hand is not None:
				if 'two-handed' in main_hand.properties or monster.versatile_weapon_with_two_hands:
					main_hand.dequip(monster)
		main_hand = get_equipped_in_slot(monster, 'main hand')
		off_hand = get_equipped_in_slot(monster, 'off hand')
		if monster.two_weapon_fighting:
			if main_hand is not None and off_hand is not None:
				if not 'light' in main_hand.properties or not 'light' in off_hand.properties: #this deals with wielding a mix of light and heavy weapons
					off_hand.dequip(monster)
			if main_hand is None and off_hand is not None:
				off_hand.is_equipped = 'main hand'

		### special case for flammable items like torches
		if 'flammable' in self.properties:
			#flammable equipment results in illuminated items
			obj = Condition(name='illumination', permanent=True, colour='yellow')
			obj.apply_to_item(self.owner)
 
		#equip object and show a message about it
		self.is_equipped = slot
		if monster != player: message(monster.name_for_printing() + ' equipped ' + self.owner.name + ' on ' + slot + '.', 'white')
		if self.adds_trait is not None:
			for trait in self.adds_trait:
				monster.fighter.traits.append(trait)
		if self.adds_proficiency is not None:
			for proficiency in self.adds_proficiency:
				monster.fighter.proficiencies.append(proficiency)
		if monster.fighter:
			recalc_stats(monster)
		
		# final check to make sure that two-weapon fighting hasn't been messed up due to all the weird permutations of options
		main_hand = get_equipped_in_slot(monster, 'main hand')
		off_hand = get_equipped_in_slot(monster, 'off hand')
		if main_hand is not None and off_hand is not None:
			if 'light' in main_hand.properties and 'light' in off_hand.properties:
				monster.two_weapon_fighting = True
			else:
				monster.two_weapon_fighting = False
		else: 
			monster.two_weapon_fighting = False
 
	def dequip(self, monster):
		#dequip object and show a message about it
		if not self.is_equipped: return
		
		### special case for versatile weapons - do this first so we don't lose the slot information
		if monster.versatile_weapon_with_two_hands:
			if self.is_equipped == 'main hand':
				if 'versatile' in self.properties:
					monster.versatile_weapon_with_two_hands = False
				
		### special case for two-weapon fighting - make sure we update the relevant flag
		if monster.two_weapon_fighting:
			if self.is_equipped == 'main hand':
				other_hand = get_equipped_in_slot(monster, 'off hand')
			elif self.is_equipped == 'off hand':
				other_hand = get_equipped_in_slot(monster, 'main hand')
			else:
				other_hand = None
			if other_hand is not None:
				if other_hand.is_equipped == 'off hand': other_hand.is_equipped = None
				monster.two_weapon_fighting = False
				
		self.is_equipped = None
		if self.adds_trait is not None:
			for trait in self.adds_trait:
				if monster.fighter:
					monster.fighter.traits.remove(trait)
		if self.adds_proficiency is not None:
			for proficiency in self.adds_proficiency:
				if monster.fighter:
					monster.fighter.proficiencies.remove(proficiency)
				
		if monster.fighter:
			recalc_stats(monster)
		
		### special case for flammable items like torches
		if 'flammable' in self.properties:
			for condition in self.owner.item.conditions:
				if condition.name == 'illumination':
					condition.remove_from_item(self.owner)
				
class Condition:
	#an object to be attached to fighters or items to represent a wide range of temporary effects 
	def __init__(self, name, duration=0, causes_damage=0, to_hit_bonus=0, damage_bonus=0, ac_bonus=0, saving_throw_bonus=0, variable_bonus=False, damage_on_hit=False, damage_on_hit_save_type=None, damage_on_hit_save_dc=None, damage_on_hit_save_dmg_modifer=None, num_dmg_die=0, dmg_die=0, dmg_type=None, permanent=False, colour='white', visible=True, remove_on_rest=False, name_prefix=None, name_suffix=None, name_tail=None, name_over_ride=None, colour_over_ride=None, str_bonus=None, dex_bonus=None, con_bonus=None, int_bonus=None, wis_bonus=None, cha_bonus=None):
		self.name = name
		self.name_prefix = name_prefix
		self.name_suffix = name_suffix
		self.name_tail = name_tail
		self.name_over_ride = name_over_ride
		self.colour_over_ride = colour_over_ride
		self.colour = colour
		self.visible = visible
		self.causes_damage = causes_damage
		self.duration = duration
		self.permanent = permanent
		self.saving_throw_bonus = saving_throw_bonus
		self.to_hit_bonus = to_hit_bonus
		self.damage_bonus = damage_bonus
		self.ac_bonus = ac_bonus
		self.variable_bonus = variable_bonus
		self.damage_on_hit = damage_on_hit
		self.damage_on_hit_save_type = damage_on_hit_save_type
		self.damage_on_hit_save_dc = damage_on_hit_save_dc
		self.damage_on_hit_save_dmg_modifer = damage_on_hit_save_dmg_modifer
		self.num_dmg_die = num_dmg_die
		self.dmg_die = dmg_die
		self.dmg_type = dmg_type
		self.remove_on_rest = remove_on_rest
		self.special = None
		
		self.stat_to_override = None
		
		self.str_bonus = str_bonus
		self.dex_bonus = dex_bonus
		self.con_bonus = con_bonus
		self.int_bonus = int_bonus
		self.wis_bonus = wis_bonus
		self.cha_bonus = cha_bonus
		
	def apply_to_actor(self, monster):
		self.owner = monster
		if monster.fighter:
			monster.fighter.conditions.append(self)
			
	def remove_from_actor(self, monster):
		if monster.fighter:
			if self.name == 'charm person':
				monster.fighter.faction = monster.fighter.true_faction
			if self.name == 'aid': 
				monster.fighter.max_hp -= 5
				if monster.fighter.hp > monster.fighter.max_hp:
					monster.fighter.hp = monster.fighter.max_hp
			if self.name == 'summoned':
				if player.can_see_object(monster): message(monster.name_for_printing() + ' disappears from sight.', 'white')
				actors.remove(monster)
			if self.name == 'heroism':
				monster.fighter.temp_hp = 0
			monster.fighter.conditions.remove(self)
			recalc_stats(monster)

	def apply_to_item(self, item):
		self.owner = item
		if item.item:
			item.item.conditions.append(self)
			
	def remove_from_item(self, item):
		if item.item:
			item.item.conditions.remove(self)
			
	def effect_on_hit(self, target, attacker):
		if self.damage_on_hit:
			if target.fighter:
				if not is_incapacitated(target):
					saving_throw = False
					if self.damage_on_hit_save_type is not None:
						if target.fighter.saving_throw(self.damage_on_hit_save_type, self.damage_on_hit_save_dc):
							saving_throw = True
					damage = dice_roll(self.num_dmg_die, self.dmg_die)
					if saving_throw: damage = int(damage * self.damage_on_hit_save_dmg_modifer)
					player_can_see = player.can_see_object(target) 
					if player_can_see: 
						if saving_throw:
							message(target.name_for_printing() + ' resists and takes ' + str(damage) + ' damage from the ' + self.name + ' effect.')
						else:
							message(target.name_for_printing() + ' takes ' + str(damage) + ' damage from the ' + self.name + ' effect.')
					target.fighter.take_damage(damage, attacker, self.dmg_type)
					
	def effect_on_being_hit(self, target, attacker):
		if self.name == 'hellish rebuke':
			process_hellish_rebuke(target, attacker, power=self.special)
			self.remove_from_actor(target)
			
	def take_turn(self):
		monster = self.owner #misleading name, because it can include items
		player_can_see = player.can_see_object(monster)
		
		if self.permanent or self.duration > 0: #deal with effects which happen every turn
			if self.causes_damage > 0:
				if monster.fighter:
					if not is_unconscious(monster):
						damage_inflicted = random.randint(1, self.causes_damage)
						if player_can_see: message(monster.name_for_printing() + ' takes ' + str(damage_inflicted) + ' damage from ' + self.name + '.')
						monster.fighter.take_damage(damage_inflicted, self, self.dmg_type)
		
		if self.duration > 0: #deal with expiring conditions whose duration has worn out
			self.duration -= 1
			if self.duration == 0: #condition has now expired
				if self.name == 'unconscious':
					self.remove_from_actor(monster)
					if monster == player: player_death()
					else: monster_ko_to_death(monster, self.special)
				else:
					if monster.fighter:
						self.remove_from_actor(monster)
						if self.visible and player_can_see: message(monster.name_for_printing() + ' no longer affected by ' + self.name + '.')
					if monster.item:
						self.remove_from_item(monster)
						if self.visible and (monster in player.inventory or player_can_see): message(monster.name_for_printing() + ' no longer affected by ' + self.name + '.')
		
		if self.name == 'unconscious':
			if monster.fighter:
				if monster.fighter.hp > 0: #monster should no longer be unconscious and has picked up some hp from somewhere
					self.remove_from_actor(monster)
		
		if self.name == 'hidden': #deal with hiding and checks to see if has been exposed
			spotted = False #start with the assumption that no one has spotted you 
			for actor in actors:
				if actor != monster:
					if actor.fighter is not None:
						if actor.fighter.faction != monster.fighter.faction:
							if actor.can_see(monster.x, monster.y): #if there is a monster in view, then check to see if that monster spots the hidden actor - don't use the can_see_object function for this because that takes into account the hidden conditon
								roll = random.randint(1, 20)
								bonus = ABILITY_MODIFIER[monster.fighter.dexterity] #dex bonus for stealth
								if 'stealthy' in monster.fighter.traits:
									bonus += PROFICIENCY_BONUS[monster.fighter.clevel]
								for item in monster.inventory:
									if item.equipment:
										if item.equipment.is_equipped:
											if 'unstealthy' in item.equipment.properties:
												bonus -= 2
								roll2 = random.randint(1, 20)
								bonus2 = ABILITY_MODIFIER[actor.fighter.wisdom] #passive check against wisdom to see if spotted
								if 'perception' in actor.fighter.proficiencies: #bonus if that actor has a perception proficiency
									bonus2 += PROFICIENCY_BONUS[actor.fighter.clevel]
								if roll + bonus < roll2 + bonus2: #this means the stealth check has failed vs the passive perception check of the obeserver
									spotted = True
			if spotted:
				message(monster.name_for_printing() + ' has been spotted.')
				self.remove_from_actor(monster)
				
		if self.name == 'mage armour':
			equipped_armour = None
			for item in monster.inventory:
				if item.equipment:
					if item.equipment.is_equipped:
						if item.equipment.is_equipped == 'body':
							equipped_armour = item
			if equipped_armour is not None:
				message(monster.name_for_printing() + ' no longer affected by ' + self.name + '.')
				self.remove_from_actor(monster)
		
class Effect:
	#an object to represent effects like clouds, flames, etc
	def __init__(self, duration=0, visible=True, permanent=False, block_sight=False, illumination=False, trigger=False, display_name=True):
		self.visible=visible
		self.duration = duration
		self.permanent = permanent
		self.block_sight = block_sight
		self.illumination = illumination
		self.dark = False #if true, prevents all light from being emitted to this square
		self.special = None #special variable to be used for special cases like flaming sphere DC check value
		self.num_dmg_die = None
		self.dmg_die = None
		self.creator = None
		
		### trigger and relate variables
		self.trigger=trigger
		self.linked_triggers = []
		self.linked_targets = []
		
		self.display_name = display_name
		
	def take_turn(self):
		global game_state
		#special case for flaming sphere spell
		if self.owner.name == 'flaming sphere':
			for actor in actors:
				if actor.fighter:
					if not is_unconscious(actor):
						if self.owner.distance_to(actor) < 2:
							damage = dice_roll(self.num_dmg_die, self.dmg_die)
							if actor.fighter.saving_throw('dexterity', self.special):
								message(actor.name_for_printing() + ' resists the flaming sphere but still takes ' + str(damage//2) + ' damage.', 'white')
								actor.fighter.take_damage(damage//2, self.creator, 'fire')
							else:
								message(actor.name_for_printing() + ' is struck by the flaming sphere for ' + str(damage) + ' damage.', 'white')
								actor.fighter.take_damage(damage, self.creator, 'fire')
		
		#special case for web spell
		if self.owner.name == 'web':
			for actor in actors:
				if actor.fighter:
					if not is_unconscious(actor):
						if self.owner.x == actor.x and self.owner.y == actor.y:
							test = False
							for condition in actor.fighter.conditions:
								if condition.name == 'stuck': test = True #test to see if already stuck in the web
							if not test: #we are not stuck in the web yet
								if not actor.fighter.saving_throw('dexterity', self.special): #failed saving throw so get caught in the web
									cond = Condition(name='stuck', duration=self.duration, colour='white', visible=True)
									cond.special = self.special #pass the caster's spell DC along
									cond.apply_to_actor(actor)
									if player.can_see_object(actor): message(actor.name_for_printing() + ' gets stuck in the web.', 'white')
							
		if self.trigger:
			if player.x == self.owner.x and player.y == self.owner.y:
				message('You hear a loud grinding sound as the ground shakes.')
				if game_state == 'exploring':
					game_state = 'playing'
				for target in self.linked_targets: #set off the trigger effect
					map[target.x][target.y].flip_wall_status()
					effects.remove(target)
				for trigger in self.linked_triggers: #then remove any redundant linked triggers
					effects.remove(trigger)
				effects.remove(self.owner) #finally remove self from active effects now triggered
			# need to double check wall torches to make sure that we haven't left one floating
			for effect in effects:
				if effect.name == 'torch':
					if not map[effect.x][effect.y].blocked:
						effects.remove(effect)
							
		if not self.permanent:
			if self.duration <= 0:
				effects.remove(self.owner)
			else:
				self.duration -= 1
				
def recalc_stats(monster):
	if monster.fighter:
		#first reset all stats to base value
		
		monster.fighter.strength = monster.fighter.base_strength
		monster.fighter.dexterity = monster.fighter.base_dexterity
		monster.fighter.constitution = monster.fighter.base_constitution
		monster.fighter.intelligence = monster.fighter.base_intelligence
		monster.fighter.wisdom = monster.fighter.base_wisdom
		monster.fighter.charisma = monster.fighter.base_charisma
		
		#then go through all conditions looking for ones that override stats (such as potions of giant strength)
		for condition in monster.fighter.conditions:
			if condition.stat_to_override == 'strength': monster.fighter.strength = condition.special
			if condition.stat_to_override == 'dexterity': monster.fighter.dexterity = condition.special
			if condition.stat_to_override == 'constitution': monster.fighter.constitution = condition.special
			if condition.stat_to_override == 'intelligence': monster.fighter.intelligence = condition.special
			if condition.stat_to_override == 'wisdom': monster.fighter.wisdom = condition.special
			if condition.stat_to_override == 'charisma': monster.fighter.charisma = condition.special
			
		#then go through all conditions which give stat bonuses
		for condition in monster.fighter.conditions:
			if condition.str_bonus: monster.fighter.strength += condition.str_bonus
			if condition.dex_bonus: monster.fighter.dexterity += condition.dex_bonus
			if condition.con_bonus: monster.fighter.constitution += condition.con_bonus
			if condition.int_bonus: monster.fighter.intelligence += condition.int_bonus
			if condition.wis_bonus: monster.fighter.wisdom += condition.wis_bonus
			if condition.cha_bonus: monster.fighter.charisma += condition.cha_bonus 
		
		#and lastly go through all equipment looking for stat bonuses
		for item in monster.inventory:
			if item.equipment:
				if item.equipment.is_equipped:
					if item.equipment.str_bonus: monster.fighter.strength += item.equipment.str_bonus
					if item.equipment.dex_bonus: monster.fighter.dexterity += item.equipment.dex_bonus
					if item.equipment.con_bonus: monster.fighter.constitution += item.equipment.con_bonus
					if item.equipment.int_bonus: monster.fighter.intelligence += item.equipment.int_bonus
					if item.equipment.wis_bonus: monster.fighter.wisdom += item.equipment.wis_bonus
					if item.equipment.cha_bonus: monster.fighter.charisma += item.equipment.cha_bonus
				
def is_unconscious(monster):
	if monster.fighter:
		for condition in monster.fighter.conditions:
			if condition.name == 'unconscious': 
				return True
	return False
	
def is_incapacitated(monster):
	if monster.fighter:
		for condition in monster.fighter.conditions:
			if condition.name == 'unconscious': 
				return True
			if condition.name == 'sleep':
				return True
	return False

				
def get_equipped_in_slot(monster, slot):	 #returns the equipment in a slot, or None if it's empty
	for obj in monster.inventory:
		if obj.equipment and obj.equipment.is_equipped == slot:
			return obj.equipment
	return None
 
def get_all_equipped(obj):	#returns a list of equipped items
	if obj == player:
		equipped_list = []
		for item in obj.inventory:
			if item.equipment and item.equipment.is_equipped:
				equipped_list.append(item.equipment.is_equipped)
		return equipped_list
	else:
		return []  #other objects have no equipment 
		
def merge_items(): #use this function to tidy up items on screen which should be merged into the same pile
	for item in items:
		if item.quantity is not None:
			for item2 in items:
				if item.x == item2.x and item.y == item2.y:
					if item.name == item2.name and item != item2: #we've found a candidate for merging - two distinct items with same name on same square
						item.quantity += item2.quantity
						items.remove(item2)
						
def merge_items_in_inventory(target):
	for item in target.inventory:
		if item.quantity is not None:
			for item2 in target.inventory:
				if item.name == item2.name and item != item2: #we've found a candidate for merging - two distinct items with same name
					item.quantity += item2.quantity
					target.inventory.remove(item2)

def is_blocked(x, y):

	if x < 0 or x > MAP_WIDTH-1: return False
	if y < 0 or y > MAP_HEIGHT-1: return False
	
	#first test the map tile
	if map[x][y].blocked:
		return True
 
	#now check for any blocking objects
	#for actor in actors:
	if (x, y) in lookup_map:
		if lookup_map[(x, y)].blocks:
		#if actor.blocks and actor.x == x and actor.y == y:
			return True
	
	for effect in effects:
		if effect.blocks and effect.x == x and effect.y == y:
			return True
 
	return False
	
def blocks_sight(x, y):
	test = False
	if 0 < x < MAP_WIDTH and 0 < y < MAP_HEIGHT:
		if map[x][y].block_sight: test = True
	for effect in effects:
		if effect.x == x and effect.y == y:
			if effect.effect.block_sight:
				test = True
	return test
	
def is_occupied(x, y):
	#for actor in actors:
		#if actor.x == x and actor.y == y:
	if (x, y) in lookup_map:
		return True
	for item in items:
		if item.x == x and item.y == y:
			return True
	for effect in effects:
		if effect.x == x and effect.y == y:
			return True
	return False
	
def is_occupied_by_ally(x, y):
	if is_occupied(x, y):
		#for actor in actors:
		#	if actor.x == x and actor.y == y and actor != player:
		if (x, y) in lookup_map:
			actor = lookup_map[(x, y)]
			if actor != player:
				if actor.fighter:
					if actor.fighter.faction == player.fighter.faction:
						return True
	return False
	
def is_openable(x, y):
	return map[x][y].openable
	
def can_walk_between(x1, y1, x2, y2):
	tcod.line_init(x1, y1, x2, y2)
	test = True
	while True:
		(x, y) = tcod.line_step()
		if x is None: break
		
		if is_blocked(x, y): 
			test = False
			break
	return test 
	
def distance_between(a, b, x, y):
	#return the distance to some coordinates
	return math.sqrt((x - a) ** 2 + (y - b) ** 2)
	
def knock_back(target, source, power): #function to knock back a target away from the source object - power is how many squares we are trying to knock back but we need to work out the direction and whether it is possible
	distance = source.distance_to(target)
	dx = target.x - source.x
	dy = target.y - source.y
	if dx > 0: dest_x = target.x + power
	elif dx < 0: dest_x = target.x - power
	else: dest_x = target.x
	if dy > 0: dest_y = target.y + power
	elif dy < 0: dest_y = target.y - power
	else: dest_y = target.y
	if not is_blocked(dest_x, dest_y): 
		target.x = dest_x
		target.y = dest_y
	update_lookup_map()
	
def path_func(x1, y1, x2, y2, data):
	global map

	if is_blocked(x2, y2): 
		if is_occupied_by_ally(x2, y2):
			return 0.25
		if is_openable(x2, y2) and is_blocked(x2, y2):
			return 0.5
		else: 
			return 0.0
	return 1.0
	
def send_to_back(object):
	#make this object be drawn first, so all others appear above it if they're in the same tile.
	global actors, items, effects
	if object in actors:
		actors.remove(object)
		actors.insert(0, object)
	if object in effects:
		effects.remove(object)
		effects.insert(0, object)
	if object in items:
		items.remove(object)
		items.insert(0, object)
		 
def draw(object, colour=None):
	global game_state, familiar, fov_map_fam, fov_map
	#only show if it's visible to the player; or it's set to "always visible" and on an explored tile
	
	if object.fighter and object != player and object != familiar:
		for condition in object.fighter.conditions:
			if condition.name == 'invisibility': 
				if 'blindsight' not in player.fighter.traits:
					return #don't draw if invisible and player can't blind see
			if condition.name == 'hidden':
				return #don't draw if hidden
	
	if SHOW_ALL_OBJECTS:
		visible = True
	else:
		visible = (fov_map.fov[object.y, object.x] and light_map[object.x][object.y] > 0)
		if not visible:
			if familiar is not None:
				visible = (fov_map_fam.fov[object.y, object.x]) and light_map[object.x][object.y] > 0
	always_visible = (object.always_visible and map[object.x][object.y].explored)
	if visible or always_visible:
		if object.has_been_seen == False:
			object.has_been_seen = True
			if game_state == 'exploring':
				message('Exploration interrupted by ' + object.name_for_printing() + '.')
				game_state = 'playing'
		clear(object)
		#set the colour and then draw the character that represents this object at its position
		if display_mode == 'graphics':
			vx = (player.x - object.x + (VIEW_WIDTH // 6)) + BAR_WIDTH//3
			vy = (player.y - object.y + (VIEW_HEIGHT // 6))
			blt.layer(1) #graphics are drawn on layer 1
		elif display_mode == 'ascii big':
			vx = (player.x - object.x + (VIEW_WIDTH // 4)) + BAR_WIDTH//2
			vy = (player.y - object.y + (VIEW_HEIGHT // 4))
			blt.composition(False) #ascii is drawn on layer 0 with no composition
		elif display_mode == 'ascii small':
			vx = (player.x - object.x + (VIEW_WIDTH // 2)) + BAR_WIDTH
			vy = (player.y - object.y + (VIEW_HEIGHT // 2))
			blt.composition(False)
		
		if colour is not None: 
			blt.color(colour)
		elif not visible and always_visible:
			blt.color('dark grey')
		elif is_unconscious(object) and visible: 
			blt.color('red')
		elif is_incapacitated(object) and visible: 
			blt.color('sky')
		elif object == player and game_state == 'dead': #special case
			blt.color('red')
		else:
			if display_mode == 'graphics' and object.big_char is not None: blt.color('white')
			else: blt.color(object.colour)
		if display_mode == 'graphics':
			if object.big_char is not None:
				blt.put(vx*3, vy*3, object.big_char)
			else:
				blt.layer(1)
				blt.put(vx*3, vy*3, object.char)
				blt.put(vx*3+1, vy*3, object.char)
				blt.put(vx*3+2, vy*3, object.char)
				blt.put(vx*3, vy*3+1, object.char)
				blt.put(vx*3, vy*3+2, object.char)
				blt.put(vx*3+1, vy*3+1, object.char)
				blt.put(vx*3+2, vy*3+1, object.char)
				blt.put(vx*3+1, vy*3+2, object.char)
				blt.put(vx*3+2, vy*3+2, object.char)
			#display a small token on the upper left of the char for allies and upper left for magic/ranged 
			if object.unique:
				blt.layer(2)
				blt.color('pink')
				blt.put(vx*3, vy*3, chr(249))
				blt.layer(0)
			if object.fighter:
				if object != player and object.fighter.faction == player.fighter.faction:
					blt.layer(2)
					blt.color('red')
					blt.put(vx*3+2, vy*3, chr(3))
					blt.layer(0)
				if object.fighter.ranged:
					blt.layer(2)
					blt.color('yellow')
					blt.put(vx*3, vy*3+2, chr(4))
					blt.layer(0)
				if object.fighter.magic:
					blt.layer(2)
					blt.color('purple')
					blt.put(vx*3, vy*3+2, chr(4))
					blt.layer(0)
		elif display_mode == 'ascii big':
			if object.char == '[':
				blt.puts(vx*2, vy*2, "[font=map]" + "[[") #special case needed to print this character using a font different to the default
			elif object.char == chr(247):
				blt.puts(vx*2, vy*2, "[font=map]~") #special case to fix a weird problem
			else:
				blt.puts(vx*2, vy*2, "[font=map]" + object.char)
		elif display_mode == 'ascii small':
			blt.put(vx, vy, object.char)		
	blt.layer(0) #reset this value
	blt.composition(True)
	
def clear(object):
	#erase the character that represents this object
	if display_mode == 'graphics':
		vx = (player.x - object.x + (VIEW_WIDTH // 6)) + BAR_WIDTH//3
		vy = (player.y - object.y + (VIEW_HEIGHT // 6))
		blt.put(vx*3, vy*3, ' ')
		blt.put(vx*3+1, vy*3, ' ')
		blt.put(vx*3+2, vy*3, ' ')
		blt.put(vx*3, vy*3+1, ' ')
		blt.put(vx*3, vy*3+2, ' ')
		blt.put(vx*3+1, vy*3+1, ' ')
		blt.put(vx*3+2, vy*3+1, ' ')
		blt.put(vx*3+1, vy*3+2, ' ')
		blt.put(vx*3+2, vy*3+2, ' ')
	elif display_mode == 'ascii big':
		vx = (player.x - object.x + (VIEW_WIDTH // 4)) + BAR_WIDTH//2
		vy = (player.y - object.y + (VIEW_HEIGHT // 4))
		blt.puts(vx*2, vy*2, "[font=map] ")
	elif display_mode == 'ascii small':
		vx = (player.x - object.x + (VIEW_WIDTH // 2)) + BAR_WIDTH
		vy = (player.y - object.y + (VIEW_HEIGHT // 2))
		blt.put(vx, vy, ' ')

def create_room(room):
	global map
	#go through the tiles in the rectangle and make them passable
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			map[x][y].blocked = False
			map[x][y].block_sight = False
			
def create_full_map_vault(room, vault_list, vault_actors=None, vault_items=None, vault_exits=None, random_placement=True):
	global map, actors, items, effects
	
	vault_choice = random.choice(vault_list)
	list_of_actor_types = []
	list_of_item_types = []
	list_of_exits = []
	if vault_actors is not None:
		for actor in vault_actors:
			list_of_actor_types.append(actor[0])
	if vault_items is not None:
		for item in vault_items:
			list_of_item_types.append(item[0])
	if list_of_exits is not None:
		for exit in vault_exits:
			list_of_exits.append(exit[0])
	xflip = False
	yflip = False
	if random_placement:
		if random.randint(0,1) == 1: xflip = True
		if random.randint(0,1) == 1: yflip = True
	for x in range(MAP_WIDTH):
		for y in range(MAP_HEIGHT):
			if not xflip and not yflip: char = vault_choice[MAP_HEIGHT - y - 1][MAP_WIDTH - x - 1]
			elif xflip and not yflip: char = vault_choice[y][MAP_WIDTH - x - 1]
			elif not xflip and yflip: char = vault_choice[MAP_HEIGHT - y - 1][x]
			elif xflip and yflip: char = vault_choice[y][x]
			if char == '#':
				map[x][y].blocked = True
				map[x][y].block_sight = True
				map[x][y].char = '#'
			elif char == 't':
				tree_effect = Effect(visible=True, permanent=True, display_name=False)
				tree = Object(x, y, chr(5), 'shrub', 'green', blocks=True, always_visible=True,effect=tree_effect)
				tree.big_char = random.choice(shrub_char)
				tree.small_char = int("0xE610", 16)
				tree.has_been_seen = True
				effects.append(tree)
				map[x][y].blocked = True
				map[x][y].block_sight = False
				map[x][y].char = '.'
			elif char == 'T':
				tree_effect = Effect(visible=True, permanent=True, display_name=False)
				tree = Object(x, y, chr(6), 'tree', 'green', blocks=True, always_visible=True, effect = tree_effect)
				tree.big_char = random.choice(tree_char)
				tree.small_char = int("0xE611", 16)
				tree.has_been_seen = True
				effects.append(tree)
				map[x][y].blocked = True
				map[x][y].block_sight = True
				map[x][y].char = '.'
			elif char == '~':
				water_effect = Effect(visible=True, permanent=True, display_name=False)
				water = Object(x, y, chr(247), 'water', 'blue', blocks=True, always_visible=True,effect=water_effect)
				water.big_char = random.choice(water_char)
				effects.append(water)
				map[x][y].blocked = True
				map[x][y].block_sight = False
				map[x][y].char = '.'
			elif char == ',':
				map[x][y].empty_char = random.choice(indoor_char)
				map[x][y].blocked = False
				map[x][y].block_sight = False
				map[x][y].char = '.'
			elif char == ' ':
				map[x][y].blocked = False
				map[x][y].block_sight = False
				map[x][y].char = '.'
			elif char == '+':
				map[x][y].blocked = True
				map[x][y].block_sight = True
				map[x][y].char = '+'
				map[x][y].openable = True
			elif char == '@':
				player.x = x
				player.y = y
				map[x][y].blocked = False
				map[x][y].block_sight = False
				map[x][y].char = '.'
			elif char in list_of_actor_types:
				town_npc = False
				func_name = vault_actors[char][0]
				if func_name[:5] == 'town_':
					func_name = func_name[5:]
					town_npc = True 
				func_name = 'create_' + func_name
				mon = eval(func_name)(x, y)
				mon.ai.focus = (x, y)
				if dungeon_branch.is_safe:
					mon.fighter.faction = 'neutral'
					mon.fighter.true_faction = 'neutral'
				if not dungeon_branch.can_recruit:
					mon.fighter.can_join = False
				if town_npc: mon.fighter.can_join = False
				actors.append(mon)
				map[x][y].blocked = False
				map[x][y].block_sight = False
				map[x][y].char = '.'
				if vault_actors[char][1] == 'indoors':
					map[x][y].empty_char = random.choice(indoor_char)
				elif vault_actors[char][1] == 'grass':
					map[x][y].empty_char = random.choice(grass_char)
				elif vault_actors[char][1] == 'ground':
					map[x][y].empty_char = random.choice(ground_char)
			elif char in list_of_item_types:
				func_name = 'create_' + vault_items[char]
				item = eval(func_name)(x, y)
				items.append(item)
				map[x][y].blocked = False
				map[x][y].block_sight = False
				map[x][y].char = '.'
			elif char in list_of_exits:
				test = None
				for branch in dungeon:
					if vault_exits[char][0] == branch.name:
						test = branch.name
				if test is not None:
					stairs = Object(room.x1 + x, room.y1 + y, '>', test, 'white', always_visible=True)
					stairs.proper_noun = True
					stairs.links_to = (vault_exits[char][0], vault_exits[char][1]) #create a tuple with the branch name and the level to which it should lead
					stairs.big_char = stairs_down_char
					stairs.small_char = int("0xE507", 16)
					if len(vault_exits[char]) > 2: #override with a char for upstairs
						if vault_exits[char][2] == '<':
							stairs.char = '<'
							stairs.big_char = stairs_up_char
							stairs.small_char = int("0xE508", 16)
						elif vault_exits[char][2] == 'castle':
							stairs.big_char = castle_char
							stairs.small_char = int("0xE566", 16)
						elif vault_exits[char][2] == 'village':
							stairs.big_char = village_char
							stairs.small_char = int("0xE567", 16)
						elif vault_exits[char][2] == 'cave':
							stairs.big_char = cave_char
							stairs.small_char = int("0xE568", 16)
					items.append(stairs)
					map[x][y].blocked = False
					map[x][y].block_sight = False
					map[x][y].char = '.'
			else: #deal with any unrecognised characters
				map[x][y].blocked = False
				map[x][y].block_sight = False
				map[x][y].char = '.'
	
def create_vault(room, vault_list, make_down_stairs=False, make_up_stairs=False, links_to=None):
	global map, actors, items, effects
	
	special_x = None
	special_y = None
	
	vault_choice = random.randint(0, len(vault_list)-1)
	xflip = False
	yflip = False
	rotate = False
	if random.randint(0,3) != 0: #75% chance of flipping, 25% chance of rotating
		if random.randint(0,1) == 1: xflip = True
		if random.randint(0,1) == 1: yflip = True
	else:
		rotate = True
		if random.randint(0,1) == 1: xflip = True #50% chance of flipping the rotated vault
	for x in range(room.x2 - room.x1):
		for y in range(room.y2 - room.y1):
			if rotate and not xflip: char = vault_list[vault_choice][x][y]
			elif rotate and xflip: char = vault_list[vault_choice][x][VAULT_SIZE - y - 1]
			elif not xflip and not yflip: char = vault_list[vault_choice][x][y]
			elif xflip and not yflip: char = vault_list[vault_choice][x][VAULT_SIZE - y - 1]
			elif not xflip and yflip: char = vault_list[vault_choice][VAULT_SIZE - x - 1][y]
			elif xflip and yflip: char = vault_list[vault_choice][VAULT_SIZE - x - 1][VAULT_SIZE - y - 1]
			if char == '#':
				map[room.x1 + x][room.y1 + y].blocked = True
				map[room.x1 + x][room.y1 + y].block_sight = True
				map[room.x1 + x][room.y1 + y].char = '#'
			elif char == 't':
				tree_effect = Effect(visible=True, permanent=True, display_name=False)
				tree = Object(room.x1 + x, room.y1 + y, chr(6), 'shrub', 'green', blocks=True, always_visible=True, effect=tree_effect)
				tree.big_char = random.choice(shrub_char)
				tree.small_char = int("0xE610", 16)
				tree.has_been_seen = True
				effects.append(tree)
				map[room.x1 + x][room.y1 + y].blocked = True
				map[room.x1 + x][room.y1 + y].block_sight = False
				map[room.x1 + x][room.y1 + y].char = '.'
			elif char == 'T':
				tree_effect = Effect(visible=True, permanent=True, display_name=False)
				tree = Object(room.x1 + x, room.y1 + y, chr(5), 'tree', 'green', blocks=True, always_visible=True, effect = tree_effect)
				tree.big_char = random.choice(tree_char)
				tree.small_char = int("0xE611", 16)
				tree.has_been_seen = True
				effects.append(tree)
				map[room.x1 + x][room.y1 + y].blocked = True
				map[room.x1 + x][room.y1 + y].block_sight = True
				map[room.x1 + x][room.y1 + y].char = '.'
			elif char == ' ':
				map[room.x1 + x][room.y1 + y].blocked = False
				map[room.x1 + x][room.y1 + y].block_sight = False
				map[room.x1 + x][room.y1 + y].char = '.'
			elif char == '+':
				map[room.x1 + x][room.y1 + y].blocked = True
				map[room.x1 + x][room.y1 + y].block_sight = True
				map[room.x1 + x][room.y1 + y].char = '+'
				map[room.x1 + x][room.y1 + y].openable = True
			elif char == 'X':
				if make_down_stairs:
					down_stairs = Object(room.x1 + x, room.y1 + y, '>', 'stairs', 'white', always_visible=True)
					down_stairs.big_char = stairs_down_char
					down_stairs.small_char = int("0xE507", 16)
					if links_to is not None:
						down_stairs.proper_noun = True
						down_stairs.name = links_to[0]
						down_stairs.links_to = (links_to[0], links_to[1])
					else:
						down_stairs.links_to = (dungeon_branch.name, dungeon_level+1) #create a tuple with the branch name and the level to which it should lead
					items.append(down_stairs)
				if make_up_stairs:
					up_stairs = Object(room.x1 + x, room.y1 + y, '<', 'stairs', 'white', always_visible=True)
					up_stairs.big_char = stairs_up_char
					up_stairs.small_char = int("0xE508", 16)
					if links_to is not None:
						up_stairs.proper_noun = True
						up_stairs.name = links_to[0]
						up_stairs.links_to = (links_to[0], links_to[1])
					else:
						up_stairs.links_to = (dungeon_branch.name, dungeon_level-1) #create a tuple with the branch name and the level to which it should lead
					items.append(up_stairs)
				map[room.x1 + x][room.y1 + y].blocked = False
				map[room.x1 + x][room.y1 + y].block_sight = False
				map[room.x1 + x][room.y1 + y].char = '.'
			else: #deal with all random monster and item spots
				map[room.x1 + x][room.y1 + y].blocked = False
				map[room.x1 + x][room.y1 + y].block_sight = False
				map[room.x1 + x][room.y1 + y].char = '.'
					
def create_special_vault(room, vault_list):
	global map, actors, items, effects
	
	features = []
	
	vault_choice = random.randint(0, len(vault_list)-1)
	xflip = False
	yflip = False
	rotate = False
	if random.randint(0,3) != 0: #75% chance of flipping, 25% chance of rotating
		if random.randint(0,1) == 1: xflip = True
		if random.randint(0,1) == 1: yflip = True
	else:
		rotate = True
		if random.randint(0,1) == 1: xflip = True #50% chance of flipping the rotated vault
	for x in range(room.x2 - room.x1):
		for y in range(room.y2 - room.y1):
			if rotate and not xflip: char = vault_list[vault_choice][x][y]
			elif rotate and xflip: char = vault_list[vault_choice][x][VAULT_SIZE - y - 1]
			elif not xflip and not yflip: char = vault_list[vault_choice][y][x]
			elif xflip and not yflip: char = vault_list[vault_choice][y][VAULT_SIZE - x - 1]
			elif not xflip and yflip: char = vault_list[vault_choice][VAULT_SIZE - y - 1][x]
			elif xflip and yflip: char = vault_list[vault_choice][VAULT_SIZE - y - 1][VAULT_SIZE - x - 1]
			if char == '#':
				map[room.x1 + x][room.y1 + y].blocked = True
				map[room.x1 + x][room.y1 + y].block_sight = True
				map[room.x1 + x][room.y1 + y].char = '#'
				map[room.x1 + x][room.y1 + y].diggable = False
			elif char == ' ':
				map[room.x1 + x][room.y1 + y].blocked = False
				map[room.x1 + x][room.y1 + y].block_sight = False
				map[room.x1 + x][room.y1 + y].char = '.'
			elif char == '+':
				map[room.x1 + x][room.y1 + y].blocked = True
				map[room.x1 + x][room.y1 + y].block_sight = True
				map[room.x1 + x][room.y1 + y].char = '+'
				map[room.x1 + x][room.y1 + y].openable = True
				map[room.x1 + x][room.y1 + y].diggable = False
			else: #deal with all random monster and item spots
				features.append((char, (room.x1 + x, room.y1 + y))) #create a tuple with the character followed by an x,y tuple and add it to the list
				map[room.x1 + x][room.y1 + y].blocked = False
				map[room.x1 + x][room.y1 + y].block_sight = False
				map[room.x1 + x][room.y1 + y].char = '.'
	return features

					
def create_h_tunnel(x1, x2, y):
	global map
	#horizontal tunnel. min() and max() are used in case x1>x2
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False
 
def create_v_tunnel(y1, y2, x):
	global map
	#vertical tunnel
	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False
		
def make_map(old_branch=None, old_level=None):
	global player, map, light_map, actors, items, effects, rooms, monster_func_list, weapon_func_list, armour_func_list, misc_func_list, common_magic_func_list, rare_magic_func_list, common_func_list, npc_func_list, mob_func_list, dungeon_level, dungeon_branch, quests
 
	light_map = [[0 for i in range(MAP_HEIGHT)] for j in range(MAP_WIDTH)]
	
	if dungeon_branch.full_map:
	
		branch = eval(dungeon_branch.name) #convert the branch name from a string to the object which contains the various full map branch features
	
		#initialise all the relevant variables
		actors = [player]
		items = []
		effects = []
		map = [[ Tile(blocked = True, block_sight = True, openable = False)
			for y in range(MAP_HEIGHT) ]
				for x in range(MAP_WIDTH) ]
	
		new_room = Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
		create_full_map_vault(new_room, branch.vault_layouts, vault_actors=branch.actors, vault_items=branch.items, vault_exits = branch.exits, random_placement=dungeon_branch.random_placement)
	
	else:
	
		# ### first calculate the number of 'vaults' to design the dungeon around. two of these will be special vaults which will contain the up and down stairs. if there is a live quest on this level, then some of those vaults might need to be allocated to that. otherwise, they'll all be ordinary vaults - the way it will work is that we will determine where these special features will go by reference to a simplified x,y which refers to how many vaults along and up and down
		
		vaults_x = MAP_WIDTH // VAULT_SIZE
		vaults_y = MAP_HEIGHT // VAULT_SIZE
		available_vaults = []
		
		### create a list of vaults so we can track what we have done and have yet to do
		
		for x in range(vaults_x):
			for y in range(vaults_y):
				available_vaults.append((x, y))
				
		#print('Number of available vaults: ' + str(len(available_vaults)))
		
		### determine where stair vaults will go
		upstairs_xy = random.choice(available_vaults)
		available_vaults.remove(upstairs_xy)
		if dungeon_level < dungeon_branch.depth:
			downstairs_xy = random.choice(available_vaults)
			available_vaults.remove(downstairs_xy)
		else:
			downstairs_xy = None
		
		### figure out if we need to place mandatory monsters or items, if so, put them in the same special vault

		monsters_to_make = []
		items_to_make = []
		encounters_to_make = []
		vaults_to_make = [] #will contain a tuple, the vault_xy and then the content
			
		if dungeon_level in dungeon_branch.must_generate_monster:
			for type_of_monster in dungeon_branch.must_generate_monster[dungeon_level]:
				vault_xy = random.choice(available_vaults)
				available_vaults.remove(vault_xy)
				monsters_to_make.append((vault_xy, type_of_monster))
				
		if dungeon_level in dungeon_branch.must_generate_encounter:
			for type_of_encounter in dungeon_branch.must_generate_encounter[dungeon_level]:
				vault_xy = random.choice(available_vaults)
				available_vaults.remove(vault_xy)
				encounters_to_make.append((vault_xy, type_of_encounter))
				
		if dungeon_level in dungeon_branch.must_generate_item:
			for type_of_item in dungeon_branch.must_generate_item[dungeon_level]:
				vault_xy = random.choice(available_vaults)
				available_vaults.remove(vault_xy)
				items_to_make.append((vault_xy, type_of_item))
				
		#print('Before: ' + str(len(available_vaults)))
		#for vault in available_vaults:
			#print(str(vault[0]) + ', ' + str(vault[1]))
		
		map_is_connected = False
		while not map_is_connected:
		
			#initialise all the relevant variables
			actors = [player]
			items = []
			effects = []

			#fill map with "blocked" tiles
			map = [[ Tile(blocked = True, block_sight = True, openable = False)
				for y in range(MAP_HEIGHT) ]
					for x in range(MAP_WIDTH) ]

			count = 1
			features = []
			special_features = []
			overall_features = []
			
			### first deal with the two stair vaults
			new_room = Rect(upstairs_xy[0] * VAULT_SIZE, upstairs_xy[1] * VAULT_SIZE, VAULT_SIZE, VAULT_SIZE)
			create_vault(new_room, stair_vaults, make_up_stairs=True, links_to=(old_branch.name, old_level))
#			if dungeon_branch.random_populate:
#				place_objects(new_room)
			
			if downstairs_xy is not None:
				new_room = Rect(downstairs_xy[0] * VAULT_SIZE, downstairs_xy[1] * VAULT_SIZE, VAULT_SIZE, VAULT_SIZE)
				create_vault(new_room, stair_vaults, make_down_stairs=True)
				if dungeon_branch.random_populate:
					place_objects(new_room)
			else:
				down_stairs = Object(0, 0, '>', 'stairs', 'white', always_visible=True) #dummy stairs which will never be visible
		
			for monster_to_make in monsters_to_make:
				temp_x = monster_to_make[0][0] * VAULT_SIZE
				temp_y = monster_to_make[0][1] * VAULT_SIZE
				new_room = Rect(temp_x, temp_y, VAULT_SIZE, VAULT_SIZE)
				create_vault(new_room, quest_vaults)
				func_name = 'create_' + monster_to_make[1]
				(x, y) = random_unblocked_spot_near(temp_x + (VAULT_SIZE//2), temp_y + (VAULT_SIZE//2)) #should pick a spot near the centre of the room
				obj = eval(func_name)(x, y)
				obj.ai.focus = (x, y)
				actors.append(obj)
				
			for item_to_make in items_to_make:
				temp_x = item_to_make[0][0] * VAULT_SIZE
				temp_y = item_to_make[0][1] * VAULT_SIZE
				new_room = Rect(temp_x, temp_y, VAULT_SIZE, VAULT_SIZE)
				create_vault(new_room, quest_vaults)				
				if item_to_make[1] in ['weapon', 'armour', 'misc', 'common', 'common_magic', 'rare_magic']:
					func_name = random.choice(eval(item_to_make[1] + '_func_list'))
					obj = func_name()
				else:
					func_name = 'create_' + item_to_make[1]
					obj = eval(func_name)()
				(x, y) = random_unblocked_spot_near(temp_x + (VAULT_SIZE//2), temp_y + (VAULT_SIZE//2)) #should pick a spot near the centre of the room
				obj.x = x
				obj.y = y
				items.append(obj)
				place_objects(new_room)
				
			for encounter_to_make in encounters_to_make:
				temp_x = encounter_to_make[0][0] * VAULT_SIZE
				temp_y = encounter_to_make[0][1] * VAULT_SIZE
				new_room = Rect(temp_x, temp_y, VAULT_SIZE, VAULT_SIZE)
				create_vault(new_room, quest_vaults)
				for enc in encounters:
					if enc.name == encounter_to_make[1]:
						encounter = enc
						break
				make_encounter(encounter, new_room)

			### take care of the remaining vaults
		
			for vault in available_vaults:
				if random.randint(1, 5) != 5 or dungeon_branch.special_vaults == False: #20% chance of special vault vs normal vault OR we aren't using those vaults here
					new_room = Rect(vault[0] * VAULT_SIZE, vault[1] * VAULT_SIZE, VAULT_SIZE, VAULT_SIZE)
					create_vault(new_room, eval(dungeon_branch.vault_type))
					if dungeon_branch.random_populate:
						place_objects(new_room)
				else:
					new_room = Rect(vault[0] * VAULT_SIZE, vault[1] * VAULT_SIZE, VAULT_SIZE, VAULT_SIZE)
					features = create_special_vault(new_room, special_vaults)
					if dungeon_branch.random_populate:
						place_objects(new_room)
					special_features = []
					if features is not None:
						for feature in features:
							(x, y) = feature[1]
							if feature[0] == 'x': #trigger square
								trigger = Effect(visible=False, permanent=True, trigger=True)
								obj = Object(x, y, 'x', 'trigger', 'grey', effect=trigger)
								trigger.owner = obj
								special_features.append(obj)
							elif feature[0] == 'a': #square which will shut when triggered
								door = Effect(visible=False, permanent=True)
								obj = Object(x, y, 'a', 'door', 'grey', effect=door)
								door.owner = obj
								special_features.append(obj)
							elif feature[0] == 'b': #square which will open when triggered
								door = Effect(visible=False, permanent=True)
								obj = Object(x, y, 'b', 'door', 'grey', effect=door)
								door.owner = obj
								special_features.append(obj)
						
					for a in special_features: #run through list and add linked triggers and other squares
						for b in special_features:
							if a is not b:
								if b.effect.trigger:
									a.effect.linked_triggers.append(b)
								else:
									a.effect.linked_targets.append(b)
				for feature in special_features:
					overall_features.append(feature)
			#randomise the dungeon a bit with some wear and tear through a drunken walk starting in locations next to open spaces
			if dungeon_branch.roughen_map: 
				for i in range(random.randint(10, 15)): 
					roughen_map()
			#create border to cut off loose ends and make solid
			for x in range(MAP_WIDTH):
				map[x][0].blocked = True
				map[x][MAP_HEIGHT - 1].blocked = True
				map[x][0].block_sight = True
				map[x][MAP_HEIGHT - 1].block_sight = True
				map[x][0].openable = False
				map[x][MAP_HEIGHT - 1].openable = False
				map[x][0].char = '#'
				map[x][MAP_HEIGHT - 1].char = '#'
			for y in range(MAP_HEIGHT):
				map[0][y].blocked = True
				map[MAP_WIDTH - 1][y].blocked = True
				map[0][y].block_sight = True
				map[MAP_WIDTH - 1][y].block_sight = True
				map[0][y].openable = False
				map[MAP_WIDTH - 1][y].openable = False
				map[0][y].char = '#'
				map[MAP_WIDTH - 1][y].char = '#'
			special_blocked_squares = []
			for feature in overall_features:
				special_blocked_squares.append((feature.x, feature.y))
			map_is_connected = check_map(special_blocked_squares)
		
		for feature in overall_features:
			effects.append(feature)
			if feature.char == 'b':
				map[feature.x][feature.y].make_wall()

		#place torches in random wall spots
		if dungeon_branch.random_torches:
			for x in range(MAP_WIDTH):
				for y in range(MAP_HEIGHT):
					if map[x][y].char == '#':
						if random.randint(1, 50) == 50: #1 in 50 chance of a torch
							torch = Effect(duration=0, permanent=True, block_sight=False, illumination=True, display_name=False)
							obj = Object(x, y, '#', 'torch', 'red', effect=torch, big_char=torch_wall_char, always_visible=True)
							obj.has_been_seen = True
							torch.owner = obj
							effects.append(obj)
							
		#print('After: ' + str(len(available_vaults)))
		#for vault in available_vaults:
			#print(str(vault[0]) + ', ' + str(vault[1]))
			
def roughen_map():
	global map

	while True:
		x = random.randint(2, MAP_WIDTH - 2)
		y = random.randint(2, MAP_HEIGHT - 2)
		#only act if the square targetted is blocked and has an open square adjacent in a cardinal direction	
		if (map[x][y].blocked == True) and ((map[x+1][y].blocked == False) or (map[x-1][y].blocked == False) or (map[x][y+1].blocked == False) or (map[x][y-1].blocked == False)):
			drunk_walk(x, y)
			break
				
def drunk_walk(x, y):
	global map

	if map[x][y].diggable:
		map[x][y].blocked = False
		map[x][y].block_sight = False
	steps = random.randint(10, 20)
	for i in range(steps):
		if map[x][y].diggable:
			map[x][y].blocked = False
			map[x][y].block_sight = False
			map[x][y].char = '.'
		walk_direction = random.randint(1, 4)
		if walk_direction == 1: #up
			if y > 1: y = y - 1
		elif walk_direction == 2: #down
			if y < MAP_HEIGHT - 1: y = y + 1
		elif walk_direction == 3: #left
			if x > 1: x = x - 1
		elif walk_direction == 4: #right
			if x < MAP_WIDTH - 1: x = x + 1
		
def check_map(special_blocked_squares=None):
	global map
	
	(start_x, start_y) = (1, 1)
	checked_squares = []
	#firstly find a random spot on the map which is an open square to start with
	while map[start_x][start_y].blocked:
		start_x = random.randint(1, MAP_WIDTH - 1)
		start_y = random.randint(1, MAP_HEIGHT - 1)
	#create 2d array of booleans to work with
	check_map = [[ False
		for dy in range(MAP_HEIGHT) ]
			for dx in range(MAP_WIDTH) ]
	check_map[start_x][start_y] = True
	map_checked = False
	while not map_checked:
		change_made = False #create a boolean to use to see if we've identified a change during this sweep
		for dy in range(1, MAP_HEIGHT - 1): #iterate through whole map
			for dx in range(1, MAP_WIDTH - 1):
				if check_map[dx][dy] == True: #for every square which has already been marked clear
					if not map[dx+1][dy].blocked or map[dx+1][dy].openable: #check each of the directions possible
						if check_map[dx+1][dy] == False: #check to see if we've already checked this location
							check_map[dx+1][dy] = True #note that we've checked the location
							change_made = True #note that we've made a change this iteration
					if not map[dx+1][dy+1].blocked or map[dx+1][dy+1].openable:
						if check_map[dx+1][dy+1] == False:
							check_map[dx+1][dy+1] = True
							change_made = True
					if not map[dx][dy+1].blocked or map[dx][dy+1].openable:
						if check_map[dx][dy+1] == False:
							check_map[dx][dy+1] = True
							change_made = True
					if not map[dx-1][dy+1].blocked or map[dx-1][dy+1].openable:
						if check_map[dx-1][dy+1] == False:
							check_map[dx-1][dy+1] = True
							change_made = True
					if not map[dx-1][dy].blocked or map[dx-1][dy].openable:
						if check_map[dx-1][dy] == False:
							check_map[dx-1][dy] = True
							change_made = True
					if not map[dx-1][dy-1].blocked or map[dx-1][dy-1].openable:
						if check_map[dx-1][dy-1] == False:
							check_map[dx-1][dy-1] = True
							change_made = True
					if not map[dx][dy-1].blocked or map[dx][dy-1].openable:
						if check_map[dx][dy-1] == False:
							check_map[dx][dy-1] = True
							change_made = True
					if not map[dx+1][dy-1].blocked or map[dx+1][dy-1].openable:
						if check_map[dx+1][dy-1] == False:
							check_map[dx+1][dy-1] = True
							change_made = True
		if not change_made: #if we've gone through with no changes, then we're done
			map_checked = True
	test_result = True
	for dy in range(MAP_HEIGHT): #iterate through whole map
		for dx in range(MAP_WIDTH):
			if not map[dx][dy].blocked and check_map[dx][dy] == False:
				test_result = False
	return test_result
  
def random_choice_index(chances):  #choose one option from list of chances, returning its index
	#the dice will land on some number between 1 and the sum of the chances
	dice = random.randint(1, sum(chances))
 
	#go through all chances, keeping the sum so far
	running_sum = 0
	choice = 0
	for w in chances:
		running_sum += w
 
		#see if the dice landed in the part that corresponds to this choice
		if dice <= running_sum:
			return choice
		choice += 1
 
def random_choice(chances_dict):
	#choose one option from dictionary of chances, returning its key
	chances = chances_dict.values()
	strings = chances_dict.keys()
 
	return strings[random_choice_index(chances)]
	
def random_unblocked_spot():
	test = False
	while test == False:
		x = random.randint(1, MAP_WIDTH-1)
		y = random.randint(1, MAP_HEIGHT-1)
		if not is_blocked(x, y):
			test = True 
	return(x, y)
	
def random_unblocked_spot_near(x, y):
	if x < 5: x = 10
	if y < 5: y = 10
	if x > MAP_WIDTH-5: x = MAP_WIDTH-10
	if y > MAP_HEIGHT-5: y = MAP_HEIGHT-10
	test = False
	while test == False:
		a = random.randint(x-5, x+5)
		b = random.randint(y-5, y+5)
		
		if not is_blocked(a, b):
			test = True 
	return(a, b)
	
def d20_roll(advantage=False, disadvantage=False, lucky=False):
	#lucky rerolls 1's but you're stuck with the next roll
	if advantage and not disadvantage:
		first_roll = random.randint(1, 20)
		if lucky and first_roll == 1: first_roll = random.randint(1, 20) 
		second_roll = random.randint(1, 20)
		if lucky and second_roll == 1: second_roll = random.randint(1, 20)
		result = max(first_roll, second_roll) #higher of two rolls
	elif disadvantage and not advantage:
		first_roll = random.randint(1, 20)
		if lucky and first_roll == 1: first_roll = random.randint(1, 20)
		second_roll = random.randint(1, 20)
		if lucky and second_roll == 1: second_roll = random.randint(1, 20)
		result = min(first_roll, second_roll) #lower of two rolls
	else:
		result = random.randint(1, 20) #just the single roll
		if lucky and result == 1: result = random.randint(1, 20)
	return result
 
def dice_roll(number_of_die=1, type_of_die=6):
	total = 0
	for i in range(number_of_die):
		total += random.randint(1, type_of_die)
	return total

def place_objects(room):
	#this is where we decide the chance of each monster or item appearing.
  
### MONSTER GENERATION

	if dungeon_branch.monsters[dungeon_level-1] is not None and random.randint(1, RANDOM_MONSTER_GEN_CHANCE) != 1:
		list_of_monsters = dungeon_branch.monsters[dungeon_level-1].items() #this will create a tuple containing a monster name at 0 and a probability of spawning at 1
		list_of_encounters = dungeon_branch.encounters[dungeon_level-1].items()
		monster_total = 0
		encounter_total = 0
		for monster_type in list_of_monsters:
			monster_total += monster_type[1]
		for encounter_type in list_of_encounters:
			encounter_total += encounter_type[1]
		total_chance = monster_total + encounter_total
		roll = random.randint(1, total_chance)
		if roll <= monster_total: #this means we have picked a monster, not an encounter
			for monster_type in list_of_monsters:
				roll -= monster_type[1] #reduce the roll down by each successive probability until we hit 0 and that's the selection
				if roll <= 0:
					selection = monster_type[0]
					break
			func_name = 'create_' + selection
			(x, y) = random_unblocked_spot_near(room.x1 + (VAULT_SIZE//2), room.y1 + (VAULT_SIZE//2))
			mon = eval(func_name)(x, y)
			mon.ai.focus = (x, y)
			if dungeon_branch.is_safe:
				mon.fighter.faction = 'neutral'
				mon.fighter.true_faction = 'neutral'
			if not dungeon_branch.can_recruit:
				mon.fighter.can_join = False
			actors.append(mon)
		else: #this means we have picked an encounter
			roll = roll - monster_total
			for encounter_type in list_of_encounters:
				roll -= encounter_type[1] #reduce the roll down by each successive probability until we hit 0 and that's the selection
				if roll <= 0:
					selection = encounter_type[0]
					break
			for enc in encounters:
				if enc.name == selection:
					encounter = enc
					break
			make_encounter(enc, room)
	
	else: #this is the default monster generation including all types of monsters and encounters
	
		if random.randint(1, 5) == 5: #1 in 5 chance of placing a mob instead of individuals on levels beyond the first
			count = 0
			while True:
				count += 1
				encounter = random.choice(encounters)
				if not encounter.special_encounter:
					if encounter.cr <= dungeon_level * 2 or count > 10: 
						break
			make_encounter(encounter, room)
		else:
			for i in range(random.randint(1, RANDOM_MONSTERS_PER_VAULT)): 
				if random.randint(1, CHANCE_OF_NPC) == 1:
					npc = True
				else:
					npc = False
				while True:
					if npc: func = random.choice(npc_func_list)
					else: func = random.choice(monster_func_list)
					test = func.__name__
					test = test[7:] #this converts that function name into a string to be compared against the CR tables
					if npc:
						if NPC_CR[test] <= float(dungeon_level) // NPC_LEVEL_TO_CR: break
					elif dungeon_level == 1:
						if MONSTER_CR[test] <= float(dungeon_level) // STARTING_LEVEL_TO_CR: break
					else:
						if MONSTER_CR[test] <= float(dungeon_level) // DUNGEON_LEVEL_TO_CR: break
				count = 0
				while True:
					x = random.randint(room.x1+1, room.x2-1)
					y = random.randint(room.y1+1, room.y2-1)
					if map[x][y].char == '.': 
						monster = func(x, y)
						monster.ai.focus = (x, y)
						if npc or dungeon_branch.is_safe: 
							monster.fighter.faction = 'neutral'
							monster.fighter.true_faction = 'neutral'
						if not dungeon_branch.can_recruit:
							monster.fighter.can_join = False
						break
					count += 1
					if count > 10: break
				#we don't want to spawn water monsters in the normal dungeon
				if 'water' not in monster.fighter.traits: actors.append(monster)
 
### ITEM GENERATION 

	#one item per vault 
	choice = random.randint(1, 48)
	if choice <= 15:
		func = random.choice(weapon_func_list)
	elif choice <= 30:
		func = random.choice(armour_func_list)
	elif choice <= 40:
		func = random.choice(misc_func_list)
	elif choice <= 43:
		func = random.choice(common_func_list)
	elif choice <= 47:
		func = random.choice(common_magic_func_list)
	elif choice <= 48:
		func = random.choice(rare_magic_func_list)
		
	#choose random spot for this item
	while True:
		x = random.randint(room.x1+2, room.x2-2)
		y = random.randint(room.y1+2, room.y2-2)
		#only place it if the tile is not blocked
		if map[x][y].char == '.': break
	item = func()
	item.x, item.y = x, y
	if random.randint(1, 10) == 10: #10% chance
		if item.equipment:
			roll = random.randint(1, 100)
			if roll >= 95: #5% chance
				modifier = 3
			elif roll >= 75: #further 20% chance
				modifier = 2
			else: #remaining 75% chance
				modifier = 1
			if item.equipment.dmg_die != 0: #this is a weapon presumably
				add_weapon_enchantment(item, modifier)
				roll = random.randint(1, 10)
				if roll == 1: add_weapon_flaming(item)
				if roll == 2: add_weapon_frost(item)
				if roll == 3: add_weapon_venom(item)
			elif item.equipment.ac != 0: #this is armour presumably
				add_armour_enchantment(item, modifier)
				roll = random.randint(1, 4)
				if roll == 1: add_armour_resistance(item)

	items.append(item)
	send_to_back(item)	 #items appear below other objects

def make_encounter(encounter, room):

	mob = []
	for monster in encounter.monsters:
		func_name = 'create_' + monster.type
		for i in range(random.randint(monster.min, monster.max)):
			(x, y) = random_unblocked_spot_near(room.x1 + (VAULT_SIZE//2), room.y1 + (VAULT_SIZE//2)) #random spot near middle of the room
			mon = eval(func_name)(x, y)
			mon.ai.focus = (x, y)
			if monster.name is not None: mon.name = monster.name
			if monster.hp is not None: 
				mon.fighter.max_hp = monster.hp
				mon.fighter.hp = monster.hp
			if monster.str is not None: mon.fighter.strength = monster.str
			if monster.dex is not None: mon.fighter.dexterity = monster.dex
			if monster.con is not None: mon.fighter.constitution = monster.con
			if monster.int is not None: mon.fighter.intelligence = monster.int
			if monster.wis is not None: mon.fighter.wisdom = monster.wis
			if monster.cha is not None: mon.fighter.charisma = monster.cha
			if monster.clvl is not None: mon.fighter.clvl = monster.clvl
			if monster.magic: 
				mon.fighter.proficiencies.append('magic')
				mon.fighter.magic = True
				if monster.spells is not None:
					for spell in monster.spells:
						mon.fighter.spells.append(spell)
			if monster.ranged:
				mon.fighter.traits.append('ranged')
				mon.fighter.ranged = True
			if random.randint(0, 100) < monster.illumination_chance:
				mon.fighter.traits.append('illumination')
			if dungeon_branch.is_safe:
				mon.fighter.faction = 'neutral'
				mon.fighter.true_faction = 'neutral'
			if not dungeon_branch.can_recruit:
				mon.fighter.can_join = False
			mob.append(mon)
	if len(mob) > 0: leader = mob[0]
	for mon in mob:
		#monster.fighter.faction = encounter.faction
		#monster.fighter.true_faction = encounter.faction
		mon.old_ai = mon.ai
		if 'magic' in mon.fighter.proficiencies:
			companion_ai_component = CompanionMagicMonster(leader, 5)
		elif 'ranged' in mon.fighter.traits:
			companion_ai_component = CompanionRangedMonster(leader, 5)
		else:
			companion_ai_component = CompanionMonster(leader, 5)
		companion_ai_component.can_talk = False
		companion_ai_component.can_revive = False
		companion_ai_component.can_path_find = False
		companion_ai_component.path_finding_chance = 5
		mon.ai = companion_ai_component
		companion_ai_component.owner = mon
		if mon != leader: leader.followers.append(mon)
		if dungeon_branch.is_safe:
			mon.fighter.faction = 'neutral'
			mon.fighter.true_faction = 'neutral'
		if not dungeon_branch.can_recruit:
			mon.fighter.can_join = False
		actors.append(mon)
		
def create_reward(reward):
	if reward[-4:] == 'gold':
		item = create_gold(quantity=int(reward.strip(' gold')))
	elif reward in ['weapon', 'armour', 'misc', 'common', 'common_magic', 'rare_magic']:
		func_name = random.choice(eval(reward + '_func_list'))
		item = func_name()
	else:
		func_name = eval('create_' + reward)
		item = func_name()
	item.x = player.x
	item.y = player.y
	items.append(item)
	
def get_attack_stats(target):
	
	weapon_in_main_hand = None
	weapon_in_off_hand = None
	to_hit_bonus = 0
	finesse = None
	proficient = None
	base_num_dmg_die = None
	base_dmg_die = None
	dmg_bonus = 0
	base_dmg_type = None
	off_to_hit_bonus = 0
	off_finesse = None
	off_proficient = None
	off_base_num_dmg_die = None
	off_base_dmg_die = None
	off_dmg_bonus = 0
	off_base_dmg_type = None
	
	for item in target.inventory:
		if item.equipment:
			if item.equipment.is_equipped:
				if item.equipment.is_equipped == 'main hand':
					weapon_in_main_hand = item
					break

	two_weapon_fighting = False
	if target.two_weapon_fighting:
		two_weapon_fighting = True
		for item in target.inventory:
			if item.equipment:
				if item.equipment.is_equipped:
					if item.equipment.is_equipped == 'off hand':
						weapon_in_off_hand = item
						break
					
	two_handed = False
	if weapon_in_main_hand is not None:
		if 'two-handed' in weapon_in_main_hand.equipment.properties or ('versatile' in weapon_in_main_hand.equipment.properties and target.versatile_weapon_with_two_hands):
			two_handed = True
			
	ranged = False
	if weapon_in_main_hand is not None:
		if 'launcher' in weapon_in_main_hand.equipment.properties:
			ranged = True

	reach = False
	if weapon_in_main_hand is not None:
		if 'reach' in weapon_in_main_hand.equipment.properties:
			reach = True

	### main weapon
			
	finesse = False
	if weapon_in_main_hand is not None:
		if 'finesse' in weapon_in_main_hand.equipment.properties and ABILITY_MODIFIER[target.fighter.dexterity] > ABILITY_MODIFIER[target.fighter.strength]:
			finesse = True
			to_hit_bonus = ABILITY_MODIFIER[target.fighter.dexterity]
		elif ranged:
			to_hit_bonus = ABILITY_MODIFIER[target.fighter.dexterity]
		else:
			to_hit_bonus = ABILITY_MODIFIER[target.fighter.strength]
	else:
		to_hit_bonus = target.fighter.base_to_hit
		
	proficient = False
	if weapon_in_main_hand is not None:
		if weapon_in_main_hand.name in target.fighter.proficiencies:
			proficient = True
		else:
			if 'simple weapon' in weapon_in_main_hand.equipment.properties:
				if 'simple weapons' in target.fighter.proficiencies:
					proficient = True
			if 'martial weapon' in weapon_in_main_hand.equipment.properties:
				if 'martial weapons' in target.fighter.proficiencies:
					proficient = True
	if proficient: to_hit_bonus += PROFICIENCY_BONUS[target.fighter.clevel]
	
	#off hand weapon
	
	off_finesse = False
	if weapon_in_off_hand is not None:
		if 'finesse' in weapon_in_off_hand.equipment.properties and ABILITY_MODIFIER[target.fighter.dexterity] > ABILITY_MODIFIER[target.fighter.strength]:
			off_finesse = True
			off_to_hit_bonus = ABILITY_MODIFIER[target.fighter.dexterity]
		else:
			off_to_hit_bonus = ABILITY_MODIFIER[target.fighter.strength]
		
	off_proficient = False
	if weapon_in_off_hand is not None:
		if weapon_in_off_hand.name in target.fighter.proficiencies:
			off_proficient = True
		else:
			if 'simple weapon' in weapon_in_off_hand.equipment.properties:
				if 'simple weapons' in target.fighter.proficiencies:
					off_proficient = True
			if 'martial weapon' in weapon_in_off_hand.equipment.properties:
				if 'martial weapons' in target.fighter.proficiencies:
					off_proficient = True
	if off_proficient: off_to_hit_bonus += PROFICIENCY_BONUS[target.fighter.clevel]
	
	### main weapon damage
	
	if weapon_in_main_hand:
		base_num_dmg_die = weapon_in_main_hand.equipment.num_dmg_die
		base_dmg_die = weapon_in_main_hand.equipment.dmg_die
		if (finesse and ABILITY_MODIFIER[target.fighter.dexterity] > ABILITY_MODIFIER[target.fighter.strength]) or ranged: dmg_bonus = ABILITY_MODIFIER[target.fighter.dexterity]
		else: dmg_bonus = ABILITY_MODIFIER[target.fighter.strength]
		if 'bludgeoning' in weapon_in_main_hand.equipment.properties: base_dmg_type = 'bludgeoning'
		elif 'piercing' in weapon_in_main_hand.equipment.properties: base_dmg_type = 'piercing'
		elif 'slashing' in weapon_in_main_hand.equipment.properties: base_dmg_type = 'slashing'
	else: #unarmed or natural attack for monsters
		base_num_dmg_die = target.fighter.base_num_dmg_die
		base_dmg_die = target.fighter.base_dmg_die
		if target.fighter.monster:
			#don't apply a standard strength bonus because it's built into the stat block
			dmg_bonus = target.fighter.base_dmg_bonus
		else:
			dmg_bonus = ABILITY_MODIFIER[target.fighter.strength]
		if target.fighter.base_dmg_type is None:
			base_dmg_type = 'bludgeoning'
		else:
			base_dmg_type = target.fighter.base_dmg_type
		
	### off weapon damage
	
	if weapon_in_off_hand:
		off_base_num_dmg_die = weapon_in_off_hand.equipment.num_dmg_die
		off_base_dmg_die = weapon_in_off_hand.equipment.dmg_die
		if (off_finesse and ABILITY_MODIFIER[target.fighter.dexterity] > ABILITY_MODIFIER[target.fighter.strength]): off_dmg_bonus = ABILITY_MODIFIER[target.fighter.dexterity]
		else: off_dmg_bonus = ABILITY_MODIFIER[target.fighter.strength]
		if 'bludgeoning' in weapon_in_off_hand.equipment.properties: off_base_dmg_type = 'bludgeoning'
		elif 'piercing' in weapon_in_off_hand.equipment.properties: off_base_dmg_type = 'piercing'
		elif 'slashing' in weapon_in_off_hand.equipment.properties: off_base_dmg_type = 'slashing'
		
	#work out if versatile weapon and if so, give a +2 to the base_dmg_die
	if weapon_in_main_hand:
		if 'versatile' in weapon_in_main_hand.equipment.properties:
			if target.versatile_weapon_with_two_hands:
				base_dmg_die += 2
		
	#work out if using a one-handed weapon in main hand with the dueling fighting style - this gives a +2 bonus to damage
	if 'dueling' in target.fighter.proficiencies:
		if weapon_in_main_hand is not None and not two_weapon_fighting:
			if not ranged:
				if 'two-handed' not in weapon_in_main_hand.equipment.properties and not target.versatile_weapon_with_two_hands:
					dmg_bonus += 2
					
	### give bonus if using ranged and have that fighting style
	if ranged:
		if 'archery' in target.fighter.proficiencies: to_hit_bonus += 2
		
	for condition in target.fighter.conditions:
		if condition.to_hit_bonus != 0:
			to_hit_bonus += condition.to_hit_bonus
			off_to_hit_bonus += condition.to_hit_bonus
		if condition.damage_bonus != 0:
			dmg_bonus += condition.dmg_bonus
			off_dmg_bonus += condition.dmg_bonus
			
	for item in target.inventory:
		if item.equipment:
			if item.equipment.is_equipped:
				if item.equipment.is_equipped != 'quiver': #this shouldn't give you a bonus
					if item.equipment.is_equipped == 'main hand':
						for condition in item.item.conditions:
							if condition.to_hit_bonus != 0:
								to_hit_bonus += condition.to_hit_bonus
							if condition.damage_bonus != 0:
								dmg_bonus += condition.damage_bonus
					if item.equipment.is_equipped == 'off hand':
						for condition in item.item.conditions:
							if condition.to_hit_bonus != 0:
								off_to_hit_bonus += condition.to_hit_bonus
							if condition.damage_bonus != 0:
								off_dmg_bonus += condition.damage_bonus
								
	### take into account two-weapon fighting style
	if two_weapon_fighting:
		if not 'two-weapon fighting' in target.fighter.proficiencies:
			if off_dmg_bonus > 0: off_dmg_bonus = 0
					
	if not two_weapon_fighting:
		weapon_in_off_hand = None
		off_to_hit_bonus = 0
		off_finesse = None
		off_proficient = None
		off_base_num_dmg_die = 0
		off_base_dmg_die = 0
		off_dmg_bonus = 0
		off_base_dmg_type = None

	return to_hit_bonus, weapon_in_main_hand, finesse, proficient, two_handed, ranged, reach, base_num_dmg_die, base_dmg_die, dmg_bonus, base_dmg_type, two_weapon_fighting, weapon_in_off_hand, off_to_hit_bonus, off_finesse, off_proficient, off_base_num_dmg_die, off_base_dmg_die, off_dmg_bonus, off_base_dmg_type

def get_defence_stats(target):
	#first of all get the defender's ac
	#start by finding out what armour and shields are being used
	equipped_armour = None
	equipped_shield = None
	for item in target.inventory:
		if item.equipment:
			if item.equipment.is_equipped:
				if item.equipment.is_equipped == 'body':
					equipped_armour = item
				elif 'shield' in item.equipment.properties:
					equipped_shield = item
	
	#now apply any dexterity modifier based on the weight of the armour (if any)
	if target.fighter.monster and equipped_armour is None:
		#don't apply a dex bonus because it's built into the stat block
		dex_modifier = 0 
	else:
		dex_modifier = ABILITY_MODIFIER[target.fighter.dexterity]
	if equipped_armour is not None:
		defender_ac = equipped_armour.equipment.ac
		if 'light armour' in equipped_armour.equipment.properties:
			if dex_modifier > 0:
				defender_ac += dex_modifier
		elif 'medium armour' in equipped_armour.equipment.properties:
			if dex_modifier > 0:
				if dex_modifier > 2: dex_modifier = 2 #cap the modifier at 2
				defender_ac += dex_modifier
		elif 'heavy armour' in equipped_armour.equipment.properties:
			pass #no dex modifier for heavy armour
	else:  
		defender_ac = target.fighter.base_ac
		if dex_modifier > 0: 
			defender_ac += dex_modifier #full benefit for dexterity while unarmoured
			
	#deal with equipped shields
	if equipped_shield:
		defender_ac += equipped_shield.equipment.ac
		
	#deal with bonus for fighting style of defence
	if equipped_armour is not None:
		if 'defence' in target.fighter.proficiencies:
			defender_ac += 1
		
	for condition in target.fighter.conditions:
		if condition.ac_bonus != 0:
			defender_ac += condition.ac_bonus
				
	for item in target.inventory:
		if item.equipment:
			if item.equipment.is_equipped:
				for condition in item.item.conditions:
					if condition.ac_bonus != 0:
						defender_ac += condition.ac_bonus

	armour_proficient = False
	shield_proficient = False
	for item in target.inventory:
		if item.equipment:
			if item.equipment.is_equipped:
				if item.equipment.is_equipped == 'body':
					if 'light armour' in item.equipment.properties:
						if 'light armour' in target.fighter.proficiencies:
							armour_proficient = True
					if 'medium armour' in item.equipment.properties:
						if 'medium armour' in target.fighter.proficiencies:
							armour_proficient = True
					if 'heavy armour' in item.equipment.properties:
						if 'heavy armour' in target.fighter.proficiencies:
							armour_proficient = True
				if item.equipment.is_equipped == 'off hand':
					if 'shield' in item.equipment.properties:
						if 'shields' in target.fighter.proficiencies:
							shield_proficient = True
						
	return defender_ac, equipped_armour, equipped_shield, dex_modifier, armour_proficient, shield_proficient
	
def get_speed_stats(target):
	if target.move_cost is None:
		move_cost = BASE_MOVEMENT_COST
	else:
		move_cost = target.move_cost
		
	for condition in target.fighter.conditions: 
		if condition.name == 'hidden':
			move_cost = int(move_cost * 1.5)
			
	if target.fighter.race != 'Mountain Dwarf' and target.fighter.race != 'Hill Dwarf':
		for item in target.inventory:
			if item.equipment:
				if item.equipment.is_equipped == 'body':
					if 'heavy armour' in item.equipment.properties:
						test = None
						if 'str 13' in item.equipment.properties: test = 13
						if 'str 15' in item.equipment.properties: test = 15
						if test is not None:
							if target.fighter.strength < test:
								move_cost = int(move_cost * 1.5)
		
	if target.action_cost is None:
		action_cost = BASE_ACTION_COST
	else:
		action_cost = target.action_cost
		
	return move_cost, action_cost
	
def calc_light_map():
	global light_map
	
	if dungeon_branch.always_lit == True: #above ground, everything is lit
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				light_map[x][y] = 2
	
	else:
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				light_map[x][y] = 0
				
		if 'darkvision' in player.fighter.traits or 'blindsight' in player.fighter.traits: 
			darkvision = True
		else: 
			darkvision = False
			
		if darkvision: 
			sight_range = 4
		else:
			sight_range = 2
			
		illumination_range = 6
		
		if familiar:
		
			if 'darkvision' in familiar.fighter.traits or 'blindsight' in familiar.fighter.traits: 
				fam_darkvision = True
			else: 
				fam_darkvision = False
				
			if fam_darkvision: 
				fam_sight_range = 4
			else:
				fam_sight_range = 2
		
		#do area around player first 
		for x in range(player.x - sight_range - 2, player.x + sight_range + 2):
			for y in range(player.y - sight_range - 2, player.y + sight_range + 2):
				if x >= 0 and y >= 0 and x < MAP_WIDTH and y < MAP_HEIGHT:
					if player.distance(x, y) <= sight_range:
						light_map[x][y] = 1 #this value means player can see but not lit
						
		#do area around familiar if there is one
		if familiar:
			for x in range(familiar.x - fam_sight_range - 2, familiar.x + fam_sight_range + 2):
				for y in range(familiar.y - fam_sight_range - 2, familiar.y + fam_sight_range + 2):
					if x >= 0 and y >= 0 and x < MAP_WIDTH and y < MAP_HEIGHT:
						if familiar.distance(x, y) <= fam_sight_range:
							light_map[x][y] = 1 #this value means player can see but not lit
						
		list_of_lit_objects = []
		list_of_dark_objects = [] #special case for darkness effect
		for actor in actors:
			test = False
			if actor.fighter:
				for condition in actor.fighter.conditions:
					if condition.name == 'illumination': #check if has the illuminated condition
						test = True
						break
			for obj in actor.inventory: #check each item in inventory to see if illuminated
				if obj.equipment:
					if obj.equipment.is_equipped is not None:
						for condition in obj.item.conditions:
							if condition.name == 'illumination':
								test = True 
								break
			if test: 
				list_of_lit_objects.append(actor)
			if actor.fighter:
				if 'illumination' in actor.fighter.traits:
					list_of_lit_objects.append(actor)
				
		for item in items:
			if item.x is not None and item.y is not None:
				test = False
				if item.item:
					for condition in item.item.conditions:
						if condition.name == 'illumination':
							test = True
							break
				if test:
					list_of_lit_objects.append(item)
					
		for effect in effects:
			if effect.effect:
				if effect.effect.illumination:
					list_of_lit_objects.append(effect)
				if effect.effect.dark:
					list_of_dark_objects.append(effect)
				
		for object in list_of_lit_objects:
			fov_map.compute_fov(object.x, object.y)
			for x in range(object.x - illumination_range - 2, object.x + illumination_range + 2):
				for y in range(object.y - illumination_range - 2, object.y + illumination_range + 2):
					if x >= 0 and y >= 0 and x < MAP_WIDTH and y < MAP_HEIGHT:
						if object.distance(x, y) <= illumination_range:
							if fov_map.fov[y, x]:
								light_map[x][y] = 2 #this value means that it is lit
							if familiar:
								if fov_map_fam.fov[y, x]:
									light_map[x][y] = 2 #this value means that it is lit
								
		for object in list_of_dark_objects:
			if player.distance(object.x, object.y) <= sight_range:
				light_map[object.x][object.y] = 1 #this value means player can see but not lit
			elif familiar and familiar.distance(object.x, object.y) <= sight_range:
				light_map[object.x][object.y] = 1 #this value means player can see but not lit
			else:
				light_map[object.x][object.y] = 0
		fov_map.compute_fov(player.x, player.y)
		
def get_wall_lighting(x, y): #function to return light value for wall based on visible floor squares - this deals with the issue of torch light being visible through walls
	fov_map.compute_fov(player.x, player.y)
	list_of_adjacent_tiles = []
	if x > 0 and y > 0:
		if not map[x-1][y-1].block_sight:
			if fov_map.fov[y-1, x-1]:
				list_of_adjacent_tiles.append((x-1, y-1))
	if y > 0:
		if not map[x][y-1].block_sight: 
			if fov_map.fov[y-1, x]:
				list_of_adjacent_tiles.append((x, y-1))
	if x < MAP_WIDTH-1 and y > 0:
		if not map[x+1][y-1].block_sight: 
			if fov_map.fov[y-1, x+1]:
				list_of_adjacent_tiles.append((x+1, y-1))
	if x > 0:
		if not map[x-1][y].block_sight:
			if fov_map.fov[y, x-1]:
				list_of_adjacent_tiles.append((x-1, y))
	if x < MAP_WIDTH-1:
		if not map[x+1][y].block_sight: 
			if fov_map.fov[y, x+1]:
				list_of_adjacent_tiles.append((x+1, y))
	if x > 0 and y < MAP_HEIGHT-1:
		if not map[x-1][y+1].block_sight: 
			if fov_map.fov[y+1, x-1]:
				list_of_adjacent_tiles.append((x-1, y+1))
	if y < MAP_HEIGHT-1:
		if not map[x][y+1].block_sight:
			if fov_map.fov[y+1, x]:
				list_of_adjacent_tiles.append((x, y+1))
	if x < MAP_WIDTH-1 and y < MAP_HEIGHT-1:
		if not map[x+1][y+1].block_sight: 
			if fov_map.fov[y+1, x+1]:
				list_of_adjacent_tiles.append((x+1, y+1))
	#we should end up with a list of visible, walkable tiles surrounding the target tile
	number_of_lit_squares = 0
	number_of_darkvision_squares = 0
	for i in list_of_adjacent_tiles: #now we want to count how many of those tiles are lit
		(a, b) = i
		if light_map[a][b] == 1: number_of_darkvision_squares += 1
		if light_map[a][b] == 2: number_of_lit_squares += 1
	if number_of_lit_squares > 0:
		return 2 #most surrounding squares are lit so light the wall too
	else:
		return 1 #most surrounding squares aren't lit so don't light the wall
	
def render_all(tiles_to_redraw=None):
	if display_mode == 'graphics':
		render_map_graphics(tiles_to_redraw)
	if display_mode == 'ascii big':
		render_map_ascii_big(tiles_to_redraw)
	if display_mode == 'ascii small':
		render_map_ascii_small(tiles_to_redraw)
	render_game_info()
	
def render_map_graphics(tiles_to_redraw=None): #tiles_to_redraw is a list of elements with the format (x, y, colour)
	global fov_map, colour_dark_wall, colour_light_wall
	global colour_dark_ground, colour_light_ground
	global fov_recompute, light_map, display_mode
	global fov_map_fam, familiar
	
	if 'darkvision' in player.fighter.traits or 'blindsight' in player.fighter.traits:
		player_darkvision_range = 4
	else:
		player_darkvision_range = 2
 
	blt.color('white')
	create_window(1, 1, BAR_WIDTH-4, VIEW_HEIGHT-1) #sidebar window
	create_window(1, BAR_HEIGHT+3, SCREEN_WIDTH-25, PANEL_HEIGHT-4) #message log window
	create_window(SCREEN_WIDTH-22, MAP_HEIGHT+13, 21, 16) #minimap window
		
	if fov_recompute:
		#recompute FOV if needed (the player moved or something)
		fov_recompute = True
		fov_map.compute_fov(player.x, player.y)
		if familiar:
			fov_map_fam.compute_fov(familiar.x, familiar.y)
 
		low_view_x = player.x - (VIEW_WIDTH//2)
		if low_view_x < 0: low_view_x = 0
		high_view_x = player.x + (VIEW_WIDTH//2)
		if high_view_x > MAP_WIDTH: high_view_x = MAP_WIDTH
		low_view_y = player.y - (VIEW_HEIGHT//2)
		if low_view_y < 0: low_view_y = 0
		high_view_y = player.y + (VIEW_HEIGHT//2)
		if high_view_y > MAP_HEIGHT: high_view_y = MAP_HEIGHT
		
		#go through all tiles, and set their background colour according to the FOV
		for y in range(low_view_y, high_view_y):
			for x in range(low_view_x, high_view_x):
				vx = player.x - x + (VIEW_WIDTH // 6) + BAR_WIDTH//3
				vy = player.y - y + (VIEW_HEIGHT // 6)
				visible = fov_map.fov[y, x]
				if not visible:
					if familiar:
						visible = fov_map_fam.fov[y, x]
				wall = map[x][y].block_sight and (map[x][y].char == '#' or map[x][y].char == '+')
				if vx in range(BAR_WIDTH//3, SCREEN_WIDTH//3-1) and vy in range(1, VIEW_HEIGHT//3):
					if not visible:
						#if it's not visible right now, the player can only see it if it's explored
						if map[x][y].explored:
							if wall:
								blt.color('dark grey')
								if map[x][y].char == '#':
									blt.put(vx*3, vy*3, map[x][y].dark_char)
								elif map[x][y].char == '+':
									blt.put(vx*3, vy*3, closed_door_char)
							else:
								#blt.put(vx*2, vy*2, dark_ground_char)
								if map[x][y].char == '=':
									blt.color('dark grey')
									blt.put(vx*3, vy*3, open_door_char)
								else:
									blt.color(colour_dark_ground)
									blt.put(vx*3, vy*3, map[x][y].empty_char)
									#blt.put(vx*3, vy*3, map[x][y].char)
									#blt.put(vx*3+1, vy*3, map[x][y].char)
									#blt.put(vx*3+2, vy*3, map[x][y].char)
									#blt.put(vx*3, vy*3+1, map[x][y].char)
									#blt.put(vx*3, vy*3+2, map[x][y].char)
									#blt.put(vx*3+1, vy*3+1, map[x][y].char)
									#blt.put(vx*3+2, vy*3+1, map[x][y].char)
									#blt.put(vx*3+1, vy*3+2, map[x][y].char)
									#blt.put(vx*3+2, vy*3+2, map[x][y].char)

									
					#it ought to be visible but it's not lit
					elif light_map[x][y] == 0:
						if map[x][y].explored:
							if wall:
								blt.color('dark grey')
								if map[x][y].char == '#':
									blt.put(vx*3, vy*3, map[x][y].dark_char)
								elif map[x][y].char == '+':
									blt.put(vx*3, vy*3, closed_door_char)
							else:
								#blt.put(vx*2, vy*2, dark_ground_char)
								if map[x][y].char == '=':
									blt.color('dark grey')
									blt.put(vx*3, vy*3, open_door_char)
								else:
									blt.color(colour_dark_ground)
									blt.put(vx*3, vy*3, map[x][y].empty_char)
									#blt.put(vx*3, vy*3, map[x][y].char)
									#blt.put(vx*3+1, vy*3, map[x][y].char)
									#blt.put(vx*3+2, vy*3, map[x][y].char)
									#blt.put(vx*3, vy*3+1, map[x][y].char)
									#blt.put(vx*3, vy*3+2, map[x][y].char)
									#blt.put(vx*3+1, vy*3+1, map[x][y].char)
									#blt.put(vx*3+2, vy*3+1, map[x][y].char)
									#blt.put(vx*3+1, vy*3+2, map[x][y].char)
									#blt.put(vx*3+2, vy*3+2, map[x][y].char)
					#it's visible
					else:
						if wall:
							lighting = get_wall_lighting(x, y) #special function to deal with quirks with wall squares being lit
							if lighting == 2: #fully lit
								#blt.color(colour_light_wall)
								blt.color('white')
								if map[x][y].char == '#':
									blt.put(vx*3, vy*3, map[x][y].light_char)
								elif map[x][y].char == '+':
									blt.put(vx*3, vy*3, closed_door_char)
							elif lighting == 1 and player.distance(x, y) < player_darkvision_range: #darkvision
								#blt.color(colour_darkvision_wall)
								blt.color('dark grey')
								if map[x][y].char == '#':
									blt.put(vx*3, vy*3, map[x][y].dark_char)
								elif map[x][y].char == '+':
									blt.put(vx*3, vy*3, closed_door_char)
							else: 
								#blt.color(colour_dark_wall)
								blt.color('dark grey')
								if map[x][y].char == '#':
									blt.put(vx*3, vy*3, map[x][y].dark_char)
								elif map[x][y].char == '+':
									blt.put(vx*3, vy*3, closed_door_char)
						else:
							if light_map[x][y] == 1: #darkvision
								#blt.put(vx*2, vy*2, dark_ground_char)
								if map[x][y].char == '=':
									blt.color('dark grey')
									blt.put(vx*3, vy*3, open_door_char)
								else:
									blt.color(colour_darkvision_ground)
									blt.put(vx*3, vy*3, map[x][y].empty_char)
									#blt.put(vx*3, vy*3, map[x][y].char)
									#blt.put(vx*3+1, vy*3, map[x][y].char)
									#blt.put(vx*3+2, vy*3, map[x][y].char)
									#blt.put(vx*3, vy*3+1, map[x][y].char)
									#blt.put(vx*3, vy*3+2, map[x][y].char)
									#blt.put(vx*3+1, vy*3+1, map[x][y].char)
									#blt.put(vx*3+2, vy*3+1, map[x][y].char)
									#blt.put(vx*3+1, vy*3+2, map[x][y].char)
									#blt.put(vx*3+2, vy*3+2, map[x][y].char)
							if light_map[x][y] == 2: #fully lit
								if map[x][y].char == '=':
									blt.color('white')
									blt.put(vx*3, vy*3, open_door_char)
								else:
									blt.color(colour_light_ground)
									blt.put(vx*3, vy*3, map[x][y].empty_char)
									#blt.put(vx*3, vy*3, map[x][y].char)
									#blt.put(vx*3+1, vy*3, map[x][y].char)
									#blt.put(vx*3+2, vy*3, map[x][y].char)
									#blt.put(vx*3, vy*3+1, map[x][y].char)
									#blt.put(vx*3, vy*3+2, map[x][y].char)
									#blt.put(vx*3+1, vy*3+1, map[x][y].char)
									#blt.put(vx*3+2, vy*3+1, map[x][y].char)
									#blt.put(vx*3+1, vy*3+2, map[x][y].char)
									#blt.put(vx*3+2, vy*3+2, map[x][y].char)
						#since it's visible, explore it
						map[x][y].explored = True
 
	#draw all objects in the list, except the player. we want it to
	#always appear over all other objects! so it's drawn later.
	for effect in effects:
		if effect.effect.visible:
			vx = player.x - effect.x + (VIEW_WIDTH // 6) + BAR_WIDTH//3
			vy = player.y - effect.y + (VIEW_HEIGHT // 6)
			if vx in range(BAR_WIDTH//3, SCREEN_WIDTH//3-1) and vy in range(1, VIEW_HEIGHT//3):
				draw(effect)
	for item in items:
		vx = player.x - item.x + (VIEW_WIDTH // 6) + BAR_WIDTH//3
		vy = player.y - item.y + (VIEW_HEIGHT // 6)
		if vx in range(BAR_WIDTH//3, SCREEN_WIDTH//3-1) and vy in range(1, VIEW_HEIGHT//3):
			draw(item)
	for actor in actors:
		if actor != player:
			vx = player.x - actor.x + (VIEW_WIDTH // 6) + BAR_WIDTH//3
			vy = player.y - actor.y + (VIEW_HEIGHT // 6)
			if vx in range(BAR_WIDTH//3, SCREEN_WIDTH//3-1) and vy in range(1, VIEW_HEIGHT//3):
				draw(actor)			
	if familiar: 
		vx = player.x - familiar.x + (VIEW_WIDTH // 6) + BAR_WIDTH//3
		vy = player.y - familiar.y + (VIEW_HEIGHT // 6)
		if vx in range(BAR_WIDTH//3, SCREEN_WIDTH//3-1) and vy in range(1, VIEW_HEIGHT//3):
			draw(familiar)
	draw(player)
 
	if tiles_to_redraw is not None:
		for element in tiles_to_redraw:
			x = None
			y = None
			colour = None
			(x, y, colour) = element
			if 0 < x < MAP_WIDTH and 0 < y < MAP_HEIGHT:
				if not map[x][y].blocked and player.can_see(x, y) and map[x][y].explored:
					vx = player.x - x + (VIEW_WIDTH // 6) + BAR_WIDTH//3
					vy = player.y - y + (VIEW_HEIGHT // 6)
					blt.bkcolor(colour)
					blt.color('black')
					if map[x][y].char == '=':
					#need to do this separately becuase it's the only scenario where a special char is needed for an unblocked square
						blt.color(colour)
						blt.put(vx*3, vy*3, open_door_char)
					else:
						blt.color(colour)
						blt.put(vx*3, vy*3, map[x][y].empty_char)
						#blt.put(vx*3+1, vy*3, map[x][y].char)
						#blt.put(vx*3+2, vy*3, map[x][y].char)
						#blt.put(vx*3, vy*3+1, map[x][y].char)
						#blt.put(vx*3, vy*3+2, map[x][y].char)
						#blt.put(vx*3+1, vy*3+1, map[x][y].char)
						#blt.put(vx*3+2, vy*3+1, map[x][y].char)
						#blt.put(vx*3+1, vy*3+2, map[x][y].char)
						#blt.put(vx*3+2, vy*3+2, map[x][y].char)
						#blt.put(vx*3, vy*3, map[x][y].char)#do this one last to fix up any big chars
					#messy but if there is an object there, need to redraw
					for effect in effects:
						if effect.effect.visible:
							if effect.x == x and effect.y == y:
								draw(effect, colour)
					for item in items:
						if item.x == x and item.y == y:
							draw(item, colour)
					#for actor in actors:
					#	if actor.x == x and actor.y == y:
					#		draw(actor, colour)
					if (x, y) in lookup_map:
						draw(lookup_map[(x, y)], colour)
					blt.bkcolor('black')

def render_map_ascii_big(tiles_to_redraw=None): #tiles_to_redraw is a list of elements with the format (x, y, colour)
	global fov_map, colour_dark_wall, colour_light_wall
	global colour_dark_ground, colour_light_ground
	global fov_recompute, light_map, display_mode
	global fov_map_fam, familiar
	
	if 'darkvision' in player.fighter.traits or 'blindsight' in player.fighter.traits:
		player_darkvision_range = 4
	else:
		player_darkvision_range = 2
 
	blt.color('white')
	create_window(1, 1, BAR_WIDTH-4, VIEW_HEIGHT-1) #sidebar window
	create_window(1, BAR_HEIGHT+3, SCREEN_WIDTH-25, PANEL_HEIGHT-4) #message log window
	create_window(SCREEN_WIDTH-22, MAP_HEIGHT+13, 21, 16) #minimap window
		
	if fov_recompute:
		#recompute FOV if needed (the player moved or something)
		fov_recompute = True
		fov_map.compute_fov(player.x, player.y)
		if familiar:
			fov_map_fam.compute_fov(familiar.x, familiar.y)
 
		low_view_x = player.x - (VIEW_WIDTH//2)
		if low_view_x < 0: low_view_x = 0
		high_view_x = player.x + (VIEW_WIDTH//2)
		if high_view_x > MAP_WIDTH: high_view_x = MAP_WIDTH
		low_view_y = player.y - (VIEW_HEIGHT//2)
		if low_view_y < 0: low_view_y = 0
		high_view_y = player.y + (VIEW_HEIGHT//2)
		if high_view_y > MAP_HEIGHT: high_view_y = MAP_HEIGHT
		
		#go through all tiles, and set their background colour according to the FOV
		for y in range(low_view_y, high_view_y):
			for x in range(low_view_x, high_view_x):
				vx = player.x - x + (VIEW_WIDTH // 4) + BAR_WIDTH//2
				vy = player.y - y + (VIEW_HEIGHT // 4)
				visible = fov_map.fov[y, x]
				if not visible:
					if familiar:
						visible = fov_map_fam.fov[y, x]
				wall = map[x][y].block_sight and (map[x][y].char == '#' or map[x][y].char == '+')
				if vx in range(BAR_WIDTH//2, SCREEN_WIDTH//2-1) and vy in range(1, VIEW_HEIGHT//2):
					if not visible:
						#if it's not visible right now, the player can only see it if it's explored
						if map[x][y].explored:
							if wall:
								blt.color('dark grey')
								blt.puts(vx*2, vy*2, "[font=map]" + map[x][y].char)
					#it ought to be visible but it's not lit
					elif light_map[x][y] == 0:
						if map[x][y].explored:
							if wall:
								blt.color('dark grey')
								blt.puts(vx*2, vy*2, "[font=map]" + map[x][y].char)
					#it's visible
					else:
						if wall:
							lighting = get_wall_lighting(x, y) #special function to deal with quirks with wall squares being lit
							if lighting == 2: #fully lit
								blt.color(colour_light_wall)
								blt.puts(vx*2, vy*2, "[font=map]" + map[x][y].char)
							elif lighting == 1 and player.distance(x, y) < player_darkvision_range: #darkvision
								blt.color(colour_darkvision_wall)
								blt.puts(vx*2, vy*2, "[font=map]" + map[x][y].char)
							else: 
								blt.color(colour_dark_wall)
								blt.puts(vx*2, vy*2, "[font=map]" + map[x][y].char)
						else:
							if light_map[x][y] == 1: #darkvision
								blt.color(colour_darkvision_ground)
								blt.puts(vx*2, vy*2, "[font=map]" + map[x][y].char)
							if light_map[x][y] == 2: #fully lit
								blt.color(colour_light_ground)
								blt.puts(vx*2, vy*2, "[font=map]" + map[x][y].char)
						#since it's visible, explore it
						map[x][y].explored = True
 
	#draw all objects in the list, except the player. we want it to
	#always appear over all other objects! so it's drawn later.
	for effect in effects:
		if effect.effect.visible:
			vx = player.x - effect.x + (VIEW_WIDTH // 4) + BAR_WIDTH//2
			vy = player.y - effect.y + (VIEW_HEIGHT // 4)
			if vx in range(BAR_WIDTH//2, SCREEN_WIDTH//2-1) and vy in range(1, VIEW_HEIGHT//2):
				draw(effect)
	for item in items:
		vx = player.x - item.x + (VIEW_WIDTH // 4) + BAR_WIDTH//2
		vy = player.y - item.y + (VIEW_HEIGHT // 4)
		if vx in range(BAR_WIDTH//2, SCREEN_WIDTH//2-1) and vy in range(1, VIEW_HEIGHT//2):
			draw(item)
	for actor in actors:
		if actor != player:
			vx = player.x - actor.x + (VIEW_WIDTH // 4) + BAR_WIDTH//2
			vy = player.y - actor.y + (VIEW_HEIGHT // 4)
			if vx in range(BAR_WIDTH//2, SCREEN_WIDTH//2-1) and vy in range(1, VIEW_HEIGHT//2):
				draw(actor)
	if familiar: 
		vx = player.x - familiar.x + (VIEW_WIDTH // 4) + BAR_WIDTH//2
		vy = player.y - familiar.y + (VIEW_HEIGHT // 4)
		if vx in range(BAR_WIDTH//2, SCREEN_WIDTH//2-1) and vy in range(1, VIEW_HEIGHT//2):
			draw(familiar)
	draw(player)
 
	if tiles_to_redraw is not None:
		for element in tiles_to_redraw:
			x = None
			y = None
			colour = None
			(x, y, colour) = element
			blt.composition(True)
			if 0 < x < MAP_WIDTH and 0 < y < MAP_HEIGHT:
				if not map[x][y].blocked and player.can_see(x, y) and map[x][y].explored:
					vx = player.x - x + (VIEW_WIDTH // 4) + BAR_WIDTH//2
					vy = player.y - y + (VIEW_HEIGHT // 4)
					blt.color(colour)
					#blt.puts(vx*2, vy*2, "[font=map]" + chr(178))
					#blt.color('black')
					blt.puts(vx*2, vy*2, "[font=map]" + map[x][y].char)
					for effect in effects:
						if effect.effect.visible:
							if effect.x == x and effect.y == y:
								draw(effect, colour)
					for item in items:
						if item.x == x and item.y == y:
							draw(item, colour)
					#for actor in actors:
					#	if actor.x == x and actor.y == y:
					#		draw(actor, colour)
					if (x, y) in lookup_map:
						draw(lookup_map[(x, y)], colour)
					blt.bkcolor('black')
			blt.composition(False)

def render_map_ascii_small(tiles_to_redraw=None): #tiles_to_redraw is a list of elements with the format (x, y, colour)
	global fov_map, colour_dark_wall, colour_light_wall
	global colour_dark_ground, colour_light_ground
	global fov_recompute, light_map, display_mode
	global fov_map_fam, familiar
	
	if 'darkvision' in player.fighter.traits or 'blindsight' in player.fighter.traits:
		player_darkvision_range = 4
	else:
		player_darkvision_range = 2
 
	blt.color('white')
	create_window(1, 1, BAR_WIDTH-4, VIEW_HEIGHT-1) #sidebar window
	create_window(1, BAR_HEIGHT+3, SCREEN_WIDTH-25, PANEL_HEIGHT-4) #message log window
	create_window(SCREEN_WIDTH-22, MAP_HEIGHT+13, 21, 16) #minimap window
		
	if fov_recompute:
		#recompute FOV if needed (the player moved or something)
		fov_recompute = True
		fov_map.compute_fov(player.x, player.y)
		if familiar:
			fov_map_fam.compute_fov(familiar.x, familiar.y)
 
		low_view_x = player.x - (VIEW_WIDTH//2)
		if low_view_x < 0: low_view_x = 0
		high_view_x = player.x + (VIEW_WIDTH//2)
		if high_view_x > MAP_WIDTH: high_view_x = MAP_WIDTH
		low_view_y = player.y - (VIEW_HEIGHT//2)
		if low_view_y < 0: low_view_y = 0
		high_view_y = player.y + (VIEW_HEIGHT//2)
		if high_view_y > MAP_HEIGHT: high_view_y = MAP_HEIGHT
		
		#go through all tiles, and set their background colour according to the FOV
		for y in range(low_view_y, high_view_y):
			for x in range(low_view_x, high_view_x):
				vx = player.x - x + (VIEW_WIDTH // 2) + BAR_WIDTH
				vy = player.y - y + (VIEW_HEIGHT // 2)
				visible = fov_map.fov[y, x]
				if not visible:
					if familiar:
						visible = fov_map_fam.fov[y, x]
				wall = map[x][y].block_sight and (map[x][y].char == '#' or map[x][y].char == '+')
				if vx in range(BAR_WIDTH, SCREEN_WIDTH-1) and vy in range(1, VIEW_HEIGHT):
					if not visible:
						#if it's not visible right now, the player can only see it if it's explored
						if map[x][y].explored:
							if wall:
								blt.color('dark grey')
								blt.puts(vx, vy, map[x][y].char)
					#it ought to be visible but it's not lit
					elif light_map[x][y] == 0:
						if map[x][y].explored:
							if wall:
								blt.color('dark grey')
								blt.puts(vx, vy, map[x][y].char)
					#it's visible
					else:
						if wall:
							lighting = get_wall_lighting(x, y) #special function to deal with quirks with wall squares being lit
							if lighting == 2: #fully lit
								blt.color(colour_light_wall)
								blt.puts(vx, vy, map[x][y].char)
							elif lighting == 1 and player.distance(x, y) < player_darkvision_range: #darkvision
								blt.color(colour_darkvision_wall)
								blt.puts(vx, vy, map[x][y].char)
							else: 
								blt.color(colour_dark_wall)
								blt.puts(vx, vy, map[x][y].char)
						else:
							if light_map[x][y] == 1: #darkvision
								blt.color(colour_darkvision_ground)
								blt.puts(vx, vy, map[x][y].char)
							if light_map[x][y] == 2: #fully lit
								blt.color(colour_light_ground)
								blt.puts(vx, vy, map[x][y].char)
						#since it's visible, explore it
						map[x][y].explored = True
 
	#draw all objects in the list, except the player. we want it to
	#always appear over all other objects! so it's drawn later.
	for effect in effects:
		if effect.effect.visible:
			vx = player.x - effect.x + (VIEW_WIDTH // 2) + BAR_WIDTH
			vy = player.y - effect.y + (VIEW_HEIGHT // 2)
			if vx in range(BAR_WIDTH, SCREEN_WIDTH-1) and vy in range(1, VIEW_HEIGHT):
				draw(effect)
	for item in items:
		vx = player.x - item.x + (VIEW_WIDTH // 2) + BAR_WIDTH
		vy = player.y - item.y + (VIEW_HEIGHT // 2)
		if vx in range(BAR_WIDTH, SCREEN_WIDTH-1) and vy in range(1, VIEW_HEIGHT):
			draw(item)
	for actor in actors:
		if actor != player:
			vx = player.x - actor.x + (VIEW_WIDTH // 2) + BAR_WIDTH
			vy = player.y - actor.y + (VIEW_HEIGHT // 2)
			if vx in range(BAR_WIDTH, SCREEN_WIDTH-1) and vy in range(1, VIEW_HEIGHT):
				draw(actor)			
	if familiar: 
		vx = player.x - familiar.x + (VIEW_WIDTH // 2) + BAR_WIDTH
		vy = player.y - familiar.y + (VIEW_HEIGHT // 2)
		if vx in range(BAR_WIDTH, SCREEN_WIDTH-1) and vy in range(1, VIEW_HEIGHT):
			draw(familiar)
	draw(player)
 
	if tiles_to_redraw is not None:
		for element in tiles_to_redraw:
			x = None
			y = None
			colour = None
			(x, y, colour) = element
			if 0 < x < MAP_WIDTH and 0 < y < MAP_HEIGHT:
				if not map[x][y].blocked and player.can_see(x, y) and map[x][y].explored:
					vx = player.x - x + (VIEW_WIDTH // 2) + BAR_WIDTH
					vy = player.y - y + (VIEW_HEIGHT // 2)
					blt.bkcolor(colour)
					blt.color('black')
					blt.puts(vx, vy, map[x][y].char)
					for effect in effects:
						if effect.effect.visible:
							if effect.x == x and effect.y == y:
								draw(effect, colour)
					for item in items:
						if item.x == x and item.y == y:
							draw(item, colour)
					#for actor in actors:
					#	if actor.x == x and actor.y == y:
					#		draw(actor, colour)
					if (x, y) in lookup_map:
						draw(lookup_map[(x, y)], colour)
					blt.bkcolor('black')
					
def update_lookup_map():
	global map, lookup_map
	
	lookup_map = {}
	for actor in actors:
		lookup_map[(actor.x, actor.y)] = actor
					
def update_minimap():
	global minimap
	
	blocked_colour = (96,96,96)
	player_colour = (255,255,255)
	ally_colour = (0,255,0)
	neutral_colour = (255,255,0)
	enemy_colour = (255,0,0)
	stairs_colour = (255,255,255)
	
	temp_minimap = [[ (0,0,0)
		for dy in range(MAP_HEIGHT*2 + MINIMAP_OFFSET) ]
			for dx in range(MAP_WIDTH*2 + MINIMAP_OFFSET) ]
	
	# draw the expored map first
	for x in range(MAP_WIDTH):
		for y in range(MAP_HEIGHT):
			if map[x][y].explored:
				if map[x][y].blocked: 
					a = MAP_WIDTH - x - 1
					b = MAP_HEIGHT - y - 1
					temp_minimap[a*2 + MINIMAP_OFFSET][b*2 + MINIMAP_OFFSET] = blocked_colour
					temp_minimap[a*2 + MINIMAP_OFFSET][b*2+1 + MINIMAP_OFFSET] = blocked_colour
					temp_minimap[a*2+1 + MINIMAP_OFFSET][b*2 + MINIMAP_OFFSET] = blocked_colour
					temp_minimap[a*2+1 + MINIMAP_OFFSET][b*2+1 + MINIMAP_OFFSET] = blocked_colour
					
	# draw stairs if found - only two pixels for each to hopefully denote whether they go up or down
	
	for item in items:
		if item.links_to is not None:
			if map[item.x][item.y].explored:
				if item.links_to[1] > dungeon_level:
					a = MAP_WIDTH - item.x - 1
					b = MAP_HEIGHT - item.y - 1
					temp_minimap[a*2 + MINIMAP_OFFSET][b*2 + MINIMAP_OFFSET] = stairs_colour
					temp_minimap[a*2+1 + MINIMAP_OFFSET][b*2+1 + MINIMAP_OFFSET] = stairs_colour
				else:
					a = MAP_WIDTH - item.x - 1
					b = MAP_HEIGHT - item.y - 1
					temp_minimap[a*2 + MINIMAP_OFFSET][b*2+1 + MINIMAP_OFFSET] = stairs_colour
					temp_minimap[a*2+1 + MINIMAP_OFFSET][b*2 + MINIMAP_OFFSET] = stairs_colour
	
	# draw the player
	a = MAP_WIDTH - player.x - 1
	b = MAP_HEIGHT - player.y - 1
	temp_minimap[a*2 + MINIMAP_OFFSET][b*2 + MINIMAP_OFFSET] = player_colour
	temp_minimap[a*2 + MINIMAP_OFFSET][b*2+1 + MINIMAP_OFFSET] = player_colour
	temp_minimap[a*2+1 + MINIMAP_OFFSET][b*2 + MINIMAP_OFFSET] = player_colour
	temp_minimap[a*2+1 + MINIMAP_OFFSET][b*2+1 + MINIMAP_OFFSET] = player_colour
	
	# draw any monsters in sight
	for actor in actors:
		if player != actor and light_map[actor.x][actor.y] > 0 and fov_map.fov[actor.y, actor.x]:
			if actor.fighter:
				a = MAP_WIDTH - actor.x - 1
				b = MAP_HEIGHT - actor.y - 1
				if actor.fighter.faction == player.fighter.faction:
					temp_colour = ally_colour
				elif actor.fighter.faction == 'neutral':
					temp_colour = neutral_colour
				else:
					temp_colour = enemy_colour
				temp_minimap[a*2 + MINIMAP_OFFSET][b*2 + MINIMAP_OFFSET] = temp_colour
				temp_minimap[a*2 + MINIMAP_OFFSET][b*2+1 + MINIMAP_OFFSET] = temp_colour
				temp_minimap[a*2+1 + MINIMAP_OFFSET][b*2 + MINIMAP_OFFSET] = temp_colour
				temp_minimap[a*2+1 + MINIMAP_OFFSET][b*2+1 + MINIMAP_OFFSET] = temp_colour
	
	#flatten 2d array into 1d
	flat_pixels = []
	for dy in range(MAP_HEIGHT*2 + MINIMAP_OFFSET):
		for dx in range(MAP_WIDTH*2 + MINIMAP_OFFSET):
			flat_pixels.append(temp_minimap[dx][dy])
	
	#convert data to image
	minimap.putdata(flat_pixels)
	
	#save the result to be displayed
	minimap.save('save/minimap.png')
					
def render_game_info():
	global minimap
	
	#print the game messages, one line at a time
	y = 1
	for (line, colour) in game_msgs:
		blt.color(colour)
		blt.puts(MSG_X, (y*2)+VIEW_HEIGHT+1, "[font=log]" + line)
		y += 1
 
	blt.color('white')
	
	#show the player's stats
	to_hit_bonus, weapon_in_main_hand, finesse, proficient, two_handed, ranged, reach, base_num_dmg_die, base_dmg_die, dmg_bonus, base_dmg_type, two_weapon_fighting, weapon_in_off_hand, off_to_hit_bonus, off_finesse, off_proficient, off_base_num_dmg_die, off_base_dmg_die, off_dmg_bonus, off_base_dmg_type = get_attack_stats(player)
	
	defender_ac, equipped_armour, equipped_shield, dex_modifier, armour_proficient,shield_proficient = get_defence_stats(player)
	
	move_cost, action_cost = get_speed_stats(player)
	
	stats = [] #empty list to populate with relevant stats to display

	if weapon_in_main_hand is None: weapon_in_main_hand = player.fighter.natural_weapon
	else: weapon_in_main_hand = weapon_in_main_hand.name_for_printing(definite_article=False)
	if dmg_bonus >= 0: dmg_bonus = '+' + str(dmg_bonus)
	else: dmg_bonus = str(dmg_bonus)
	
	if weapon_in_off_hand is None: weapon_in_off_hand = 'None'
	else: weapon_in_off_hand = weapon_in_off_hand.name_for_printing(definite_article=False)
	if off_dmg_bonus >= 0: off_dmg_bonus = '+' + str(off_dmg_bonus)
	else: off_dmg_bonus = str(off_dmg_bonus)	
	
	if equipped_armour is not None: equipped_armour = equipped_armour.name_for_printing(definite_article=False)
	if equipped_shield is not None: equipped_shield = equipped_shield.name_for_printing(definite_article=False)
	
	stats.append(player.name_for_printing(definite_article=False, capitalise=True))
	if player.fighter.race and player.fighter.role: stats.append(player.fighter.race.title() + ' ' + player.fighter.role.capitalize())
	stats.append('')
	stats.append('Str: ' + str(player.fighter.strength) + '  Int: ' + str(player.fighter.intelligence))
	stats.append('Dex: ' + str(player.fighter.dexterity) + '  Wis: ' + str(player.fighter.wisdom))
	stats.append('Con: ' + str(player.fighter.constitution) + '  Cha: ' + str(player.fighter.charisma))
	stats.append('')
	stats.append('Level: ' + str(player.fighter.clevel) + ' (' + str(player.fighter.xp) + '/' + str(XP_TO_LEVEL[player.fighter.clevel+1]) + ')')
	stats.append((dungeon_branch.name.title().replace('_', ' ') + ':' + str(dungeon_level)))
	stats.append(' ')
	stats.append('HP: ' + str(player.fighter.hp + player.fighter.temp_hp) + '/' + str(player.fighter.max_hp) + '  Gold: ' + str(round(player.gold, 2)))
	stats.append('Movement speed: ' + str(int(1/float(move_cost)*3000)) + "'")
	stats.append(' ')
	stats.append('Main: ' + str(weapon_in_main_hand.capitalize()))
	stats.append('To hit bonus: ' + str(to_hit_bonus))
	stats.append('Damage: ' + str(base_num_dmg_die) + 'd' + str(base_dmg_die) + dmg_bonus)
	stats.append('- ' + base_dmg_type.capitalize())
	if proficient: stats.append('- Proficient')
	if finesse: stats.append('- Finesse')
	if two_handed: stats.append('- Two-handed')
	if ranged: stats.append('- Ranged')
	if reach: stats.append('- Reach')
	if two_weapon_fighting:
		stats.append(' ')
		stats.append('Off: ' + str(weapon_in_off_hand.capitalize()))
		stats.append('To hit bonus: ' + str(off_to_hit_bonus))
		stats.append('Damage: ' + str(off_base_num_dmg_die) + 'd' + str(off_base_dmg_die) + off_dmg_bonus)
		stats.append('- ' + off_base_dmg_type.capitalize())
		if off_proficient: stats.append('- Proficient')
		if off_finesse: stats.append('- Finesse')
	stats.append(' ')
	stats.append('Armour class: ' + str(defender_ac))
	if equipped_armour is not None: 
		stats.append(str(equipped_armour.capitalize()))
		if armour_proficient:
			stats.append('- Proficient')
		else:
			stats.append('- Not proficient')
	if equipped_shield is not None: 
		stats.append(' ')
		stats.append(str(equipped_shield.capitalize()))
		if shield_proficient:
			stats.append('- Proficient')
		else:
			stats.append('- Not proficient')
	
	count = 1
	for line in stats:
		blt.puts(1, count, ("[font=log]" + line)[:36])
		count += 2
		
	illumination = False
	conditions_buffer_line = False
	for condition in player.fighter.conditions:
		if condition.visible:
			count += 2
			conditions_buffer_line = True
			break
	for condition in player.fighter.conditions:
		if condition.visible:
			blt.color(condition.colour)
			blt.puts(1, count, ("[font=log]" + condition.name.capitalize())[:36])
			count += 2
			if condition.name == 'illumination': illumination = True #special case to deal with double ups between torches and spell effects being displayed - we only want one instance to appear
	
	if not illumination:
		for obj in player.inventory:
			if obj.equipment:
				if obj.equipment.is_equipped is not None:
					for condition in obj.item.conditions:
						if condition.name == 'illumination':
							illumination = True #this will be true if the player is carrying something which is illuminated - such as a lit torch
		if illumination: #this will occur if no illuminated conditions but illuminated items found
			if not conditions_buffer_line: count += 2
			blt.color('yellow')
			blt.puts(1, count, "[font=log]" + 'Illumination')
			count += 2
			
	blt.color('white')
	count +=1 #list out all the monsters in sight with their names
	for actor in actors:
		if count >= VIEW_HEIGHT: break
		if fov_map.fov[actor.y, actor.x] and actor != player and light_map[actor.x][actor.y] > 0:
			if actor.fighter:
				if actor.small_char is not None and display_mode == 'graphics':
					blt.color('white')
					blt.put(2, count, actor.small_char)
				else:
					blt.color(actor.colour)
					blt.put(2, count, actor.char)
				if actor in player.followers:
					blt.color('green')
					blt.puts(5, count, ("[font=log]" + actor.name_for_printing(definite_article=False, capitalise=True) + ' (' + str(actor.fighter.hp + player.fighter.temp_hp) + '/' + str(actor.fighter.max_hp) + ')')[:32])
				elif actor.unique and actor.fighter.faction == 'neutral':
					blt.color('purple')
					blt.puts(5, count, ("[font=log]" + actor.name_for_printing(definite_article=False, capitalise=True) + ' (' + str(actor.fighter.max_hp) + ')')[:32])
				elif actor.merchant and actor.fighter.faction == 'neutral':
					blt.color('yellow')
					blt.puts(5, count, ("[font=log]" + actor.name_for_printing(definite_article=False, capitalise=True) + ' (' + str(actor.fighter.max_hp) + ')')[:32])
				elif actor.fighter.faction == 'neutral':
					blt.color('white')
					blt.puts(5, count, ("[font=log]" + actor.name_for_printing(definite_article=False, capitalise=True) + ' (' + str(actor.fighter.max_hp) + ')')[:32])
				else:
					blt.color('red')
					blt.puts(5, count, ("[font=log]" + actor.name_for_printing(definite_article=False, capitalise=True) + ' (' + str(actor.fighter.max_hp) + ')')[:32])

				count += 2
			
	#and then the same for items
	#tcod.console_set_default_foreground(bar, 'white')
	for item in items:
		if count >= VIEW_HEIGHT: break
		if fov_map.fov[item.y, item.x] and light_map[item.x][item.y] > 0:
			if item.small_char is not None and display_mode == 'graphics':
				blt.color('white')
				blt.put(2, count, item.small_char)
			else:
				blt.color(item.colour)
				blt.put(2, count, item.char)
			colour_over_ride = None
			if item.item:
				for condition in item.item.conditions: #check for over ride colour
					if condition.colour_over_ride is not None:
						colour_over_ride = condition.colour_over_ride
			if colour_over_ride is not None:
				blt.color(colour_over_ride)
				blt.puts(5, count, ("[font=log]" + item.name_for_printing(definite_article=False, capitalise=True))[:32])
			elif item.char == '%' and item.colour == 'red':
				blt.color('white')
				blt.puts(5, count, ("[font=log]" + item.name_for_printing(definite_article=False, capitalise=True))[:32])
			else:
				blt.color('white')
				blt.puts(5, count, ("[font=log]" + item.name_for_printing(definite_article=False, capitalise=True))[:32])
			count += 2
			
	#and then the same for effects
	#tcod.console_set_default_foreground(bar, 'white')
	for effect in effects:
		if count >= VIEW_HEIGHT: break
		if fov_map.fov[effect.y, effect.x] and light_map[effect.x][effect.y] > 0:
			if effect.effect.visible:
				if effect.effect.display_name:
					if effect.small_char is not None and display_mode == 'graphics':
						blt.color('white')
						blt.put(2, count, effect.small_char)
					else:
						blt.color(effect.colour)
						blt.put(2, count, effect.char)
					blt.color('white')
					blt.puts(5, count, ("[font=log]" + effect.name_for_printing(definite_article=False, capitalise=True))[:36])
					count += 2
	
	blt.color('white')
	if 'magic' in player.fighter.proficiencies:
		if player.fighter.role == 'Warlock':
			blt.puts(SCREEN_WIDTH//2+7, VIEW_HEIGHT, '[font=log]Spell slots: ' + str(player.fighter.warlock_spell_slots))
		else:
			blt.puts(SCREEN_WIDTH//2-8, VIEW_HEIGHT, '[font=log]Spell slots: 1:' + str(player.fighter.spell_slots[0]) + ' 2:' + str(player.fighter.spell_slots[1]) + ' 3:' + str(player.fighter.spell_slots[2]) + ' 4:' + str(player.fighter.spell_slots[3]) + ' 5:' + str(player.fighter.spell_slots[4]) + ' 6:' + str(player.fighter.spell_slots[5]) + ' 7:' + str(player.fighter.spell_slots[6]) + ' 8:' + str(player.fighter.spell_slots[7]) + ' 9:' + str(player.fighter.spell_slots[8]) + ' ')
	
	if MINIMAP_FLAG == True:
		update_minimap()
		blt.set("0xF0000: save/minimap.png, spacing=1x1;")
		blt.put(SCREEN_WIDTH-22, MAP_HEIGHT+13, 0xF0000)

def projectile_effect(x1, y1, x2, y2, colour, char=None):
	#shows a ray animation as a fuzzy line between 2 tiles.
	blt.clear()
	render_all()  #first, re-render the screen (erase inventory, etc)
	blt.refresh()
	if char==None: char = '*'
	red = colour[0]
	green = colour[1]
	blue = colour[2]
	alpha = 255
	list_of_tiles = []
	colour_to_use = blt.color_from_argb(alpha, red, green, blue) 
	blt.color(colour_to_use)
	#for each frame of the animation, start a line between the tiles
	tcod.line_init(x1, y1, x2, y2)
	while True:	 #step through all tiles in the line
		(x, y) = tcod.line_step()
		if x is None: break
		if fov_map.fov[y, x]:
			if display_mode == 'graphics':
				vx = (player.x - x + (VIEW_WIDTH // 6)) + BAR_WIDTH//3
				vy = (player.y - y + (VIEW_HEIGHT // 6))
			elif display_mode == 'ascii big':
				vx = (player.x - x + (VIEW_WIDTH // 4)) + BAR_WIDTH//2
				vy = (player.y - y + (VIEW_HEIGHT // 4))
			elif display_mode == 'ascii small':
				vx = (player.x - x + (VIEW_WIDTH // 2)) + BAR_WIDTH
				vy = (player.y - y + (VIEW_HEIGHT // 2))
			blt.composition(False)
			blt.layer(2)
			if display_mode == 'graphics':
				blt.put(vx*3+1, vy*3+1, char)
			elif display_mode == 'ascii big':
				blt.puts(vx*2, vy*2, "[font=map]" + char)
			elif display_mode == 'ascii small':
				blt.put(vx, vy, char)
			blt.refresh() #show result
			if display_mode == 'graphics':
				blt.clear_area(vx*3+1, vy*3+1, vx*3+1, vy*3+1)
			elif display_mode == 'ascii big':
				blt.clear_area(vx*2, vy*2, vx*2+1, vy*2+1)
			elif display_mode == 'ascii small':
				blt.clear_area(vx, vy, vx, vy)
			blt.composition(True)
			blt.layer(0)
	render_all() 
	blt.refresh()
	
def bolt_effect(x1, y1, x2, y2, colour):
	#shows a ray animation as a fuzzy line between 2 tiles.
	blt.clear()
	render_all()  #first, re-render the screen (erase inventory, etc)
	blt.refresh()
	char_list = [chr(219), chr(178), chr(177), chr(176), ' ']
	red = colour[0]
	green = colour[1]
	blue = colour[2]
	alpha = 255
	list_of_tiles = []
	colour_to_use = blt.color_from_argb(alpha, red, green, blue) 
	blt.color(colour_to_use)
	#for each frame of the animation, start a line between the tiles
	tcod.line_init(x1, y1, x2, y2)
	while True:	 #step through all tiles in the line
		(x, y) = tcod.line_step()
		if x is None: break
		if fov_map.fov[y, x]:
			list_of_tiles.insert(0, [x, y])
			if len(list_of_tiles) > 5:
				list_of_tiles.pop(5)
			for tile in list_of_tiles:
				dx = tile[0]
				dy = tile[1]
				if dx is not None:
					index = list_of_tiles.index(tile)
					if display_mode == 'graphics':
						vx = (player.x - dx + (VIEW_WIDTH // 6)) + BAR_WIDTH//3
						vy = (player.y - dy + (VIEW_HEIGHT // 6))
					elif display_mode == 'ascii big':
						vx = (player.x - dx + (VIEW_WIDTH // 4)) + BAR_WIDTH//2
						vy = (player.y - dy + (VIEW_HEIGHT // 4))
					elif display_mode == 'ascii small':
						vx = (player.x - dx + (VIEW_WIDTH // 2)) + BAR_WIDTH
						vy = (player.y - dy + (VIEW_HEIGHT // 2))
					blt.composition(False)
					blt.layer(2)
					if display_mode == 'graphics':
						blt.put(vx*3, vy*3, char_list[index])
						blt.put(vx*3+1, vy*3, char_list[index])
						blt.put(vx*3+2, vy*3, char_list[index])
						blt.put(vx*3, vy*3+1, char_list[index])
						blt.put(vx*3, vy*3+2, char_list[index])
						blt.put(vx*3+1, vy*3+1, char_list[index])
						blt.put(vx*3+2, vy*3+1, char_list[index])
						blt.put(vx*3+1, vy*3+2, char_list[index])
						blt.put(vx*3+2, vy*3+2, char_list[index])
					elif display_mode == 'ascii big':
						blt.puts(vx*2, vy*2, "[font=map]" + char_list[index])
					elif display_mode == 'ascii small':
						blt.put(vx, vy, char_list[index])
					blt.composition(True)
					blt.layer(0)
			blt.refresh() #show result
	render_all()
	blt.refresh()
	
def ray_effect(x1, y1, x2, y2, colour):
	#shows a ray animation as a fuzzy line between 2 tiles.
	blt.clear()
	render_all()  #first, re-render the screen (erase inventory, etc)
	blt.refresh()
	char_list = [chr(176), chr(177), chr(178)]
	red = colour[0]
	green = colour[1]
	blue = colour[2]
	alpha_max = 255
	alpha = 0
	alpha_diff = ((alpha_max - alpha) // ANIMATION_FRAMES) * 2
	alpha_increase = True
	for frame in range(ANIMATION_FRAMES):
		if alpha >= alpha_max: alpha_increase = False
		if alpha <= 0: alpha_increase = True
		if alpha_increase:
			alpha += alpha_diff
		else:
			alpha -= alpha_diff
		colour_to_use = blt.color_from_argb(alpha, red, green, blue) 
		blt.color(colour_to_use)
		#for each frame of the animation, start a line between the tiles
		tcod.line_init(x1, y1, x2, y2)
		while True:	 #step through all tiles in the line
			(x, y) = tcod.line_step()
			if x is None: break
			if fov_map.fov[y, x]:
				if display_mode == 'graphics':
					vx = (player.x - x + (VIEW_WIDTH // 6)) + BAR_WIDTH//3
					vy = (player.y - y + (VIEW_HEIGHT // 6))
				elif display_mode == 'ascii big':
					vx = (player.x - x + (VIEW_WIDTH // 4)) + BAR_WIDTH//2
					vy = (player.y - y + (VIEW_HEIGHT // 4))
				elif display_mode == 'ascii small':
					vx = (player.x - x + (VIEW_WIDTH // 2)) + BAR_WIDTH
					vy = (player.y - y + (VIEW_HEIGHT // 2))
				blt.composition(False)
				blt.layer(2)
				if display_mode == 'graphics':
					blt.put(vx*3, vy*3, random.choice(char_list))
					blt.put(vx*3+1, vy*3, random.choice(char_list))
					blt.put(vx*3+2, vy*3, random.choice(char_list))
					blt.put(vx*3, vy*3+1, random.choice(char_list))
					blt.put(vx*3, vy*3+2, random.choice(char_list))
					blt.put(vx*3+1, vy*3+1, random.choice(char_list))
					blt.put(vx*3+2, vy*3+1, random.choice(char_list))
					blt.put(vx*3+1, vy*3+2, random.choice(char_list))
					blt.put(vx*3+2, vy*3+2, random.choice(char_list))
				elif display_mode == 'ascii big':
					blt.puts(vx*2, vy*2, "[font=map]" + random.choice(char_list))
				elif display_mode == 'ascii small':
					blt.put(vx, vy, random.choice(char_list))
				blt.composition(True)
				blt.layer(0)
		blt.refresh() #show result
	render_all()
	blt.refresh()

def explosion_effect(cx, cy, radius, colour): 
	blt.clear()
	render_all()  #first, re-render the screen
	blt.refresh()
	num_frames = float(ANIMATION_FRAMES)  #number of frames as a float, so dividing an int by it doesn't yield an int
	char_list = [chr(176), chr(177), chr(178)]
	red = colour[0]
	green = colour[1]
	blue = colour[2]
	alpha_max = 255
	alpha = 0
	alpha_diff = ((alpha_max - alpha) // ANIMATION_FRAMES) * 2
	alpha_increase = True
	for frame in range(ANIMATION_FRAMES):
		#loop through all tiles in a square around the center. min and max make sure it doesn't go out of the map.
		if alpha >= alpha_max: alpha_increase = False
		if alpha <= 0: alpha_increase = True
		if alpha_increase:
			alpha += alpha_diff
		else:
			alpha -= alpha_diff
		for x in range(0, MAP_WIDTH):
			for y in range(0, MAP_HEIGHT):
				if fov_map.fov[y, x]:
					distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
					if distance < radius + 1:
					#only draw on visible floor tile
						if not map[x][y].blocked and fov_map.fov[y, x]:
							if display_mode == 'graphics':
								vx = (player.x - x + (VIEW_WIDTH // 6)) + BAR_WIDTH//3
								vy = (player.y - y + (VIEW_HEIGHT // 6))
							elif display_mode == 'ascii big':
								vx = (player.x - x + (VIEW_WIDTH // 4)) + BAR_WIDTH//2
								vy = (player.y - y + (VIEW_HEIGHT // 4))
							elif display_mode == 'ascii small':
								vx = (player.x - x + (VIEW_WIDTH // 2)) + BAR_WIDTH
								vy = (player.y - y + (VIEW_HEIGHT // 2))
							colour_to_use = blt.color_from_argb(alpha, red, green, blue) 
							blt.color(colour_to_use)
							blt.composition(False)
							blt.layer(2)
							if display_mode == 'graphics':
								blt.put(vx*3, vy*3, random.choice(char_list))
								blt.put(vx*3+1, vy*3, random.choice(char_list))
								blt.put(vx*3+2, vy*3, random.choice(char_list))
								blt.put(vx*3, vy*3+1, random.choice(char_list))
								blt.put(vx*3, vy*3+2, random.choice(char_list))
								blt.put(vx*3+1, vy*3+1, random.choice(char_list))
								blt.put(vx*3+2, vy*3+1, random.choice(char_list))
								blt.put(vx*3+1, vy*3+2, random.choice(char_list))
								blt.put(vx*3+2, vy*3+2, random.choice(char_list))
							elif display_mode == 'ascii big':
								blt.puts(vx*2, vy*2, "[font=map]" + random.choice(char_list))
							elif display_mode == 'ascii small':
								blt.put(vx, vy, random.choice(char_list))
							blt.composition(True)
							blt.layer(0)
		blt.refresh() #show result
	render_all()
	blt.refresh()
 
def area_effect(target_squares, inner_colour, outer_colour): 
	#target_squares ought to be a list of tuples with x,y coordinates, colours should be a list with r,g,b values
	blt.clear()
	render_all()  #first, re-render the screen
	blt.refresh()
	num_frames = float(ANIMATION_FRAMES)  #number of frames as a float, so dividing an int by it doesn't yield an int
	char_list = [chr(176), chr(177), chr(178)]
	red_diff = (inner_colour[0] - outer_colour[0]) // ANIMATION_FRAMES
	green_diff = (inner_colour[1] - outer_colour[1]) // ANIMATION_FRAMES
	blue_diff = (inner_colour[2] - outer_colour[2]) // ANIMATION_FRAMES
	alpha_max = 255
	alpha = 0
	alpha_diff = ((alpha_max - alpha) // ANIMATION_FRAMES) * 2
	alpha_increase = True
	for frame in range(ANIMATION_FRAMES):
		#loop through all tiles in a square around the center. min and max make sure it doesn't go out of the map.
		if alpha >= alpha_max: alpha_increase = False
		if alpha <= 0: alpha_increase = True
		if alpha_increase:
			alpha += alpha_diff
		else:
			alpha -= alpha_diff
		for square in target_squares:
			x = square[0]
			y = square[1]
			if 0 < x < MAP_WIDTH-1 and 0 < y < MAP_HEIGHT-1:
				if not map[x][y].blocked and fov_map.fov[y, x]:
					if display_mode == 'graphics':
						vx = (player.x - x + (VIEW_WIDTH // 6)) + BAR_WIDTH//3
						vy = (player.y - y + (VIEW_HEIGHT // 6))
					elif display_mode == 'ascii big':
						vx = (player.x - x + (VIEW_WIDTH // 4)) + BAR_WIDTH//2
						vy = (player.y - y + (VIEW_HEIGHT // 4))
					elif display_mode == 'ascii small':
						vx = (player.x - x + (VIEW_WIDTH // 2)) + BAR_WIDTH
						vy = (player.y - y + (VIEW_HEIGHT // 2))
					red = inner_colour[0] + (red_diff * frame)
					green = inner_colour[1] + (green_diff * frame)
					blue = inner_colour[2] + (blue_diff * frame)
					colour_to_use = blt.color_from_argb(alpha, red, green, blue)
					blt.color(colour_to_use)
					blt.composition(False)
					blt.layer(2)
					if display_mode == 'graphics':
						blt.put(vx*3, vy*3, random.choice(char_list))
						blt.put(vx*3+1, vy*3, random.choice(char_list))
						blt.put(vx*3+2, vy*3, random.choice(char_list))
						blt.put(vx*3, vy*3+1, random.choice(char_list))
						blt.put(vx*3, vy*3+2, random.choice(char_list))
						blt.put(vx*3+1, vy*3+1, random.choice(char_list))
						blt.put(vx*3+2, vy*3+1, random.choice(char_list))
						blt.put(vx*3+1, vy*3+2, random.choice(char_list))
						blt.put(vx*3+2, vy*3+2, random.choice(char_list))
					elif display_mode == 'ascii big':
						blt.puts(vx*2, vy*2, "[font=map]" + random.choice(char_list))
					elif display_mode == 'ascii small':
						blt.put(vx, vy, random.choice(char_list))
					blt.composition(True)
					blt.layer(0)
		blt.refresh() #show result
	render_all()
	blt.refresh()
 
def message(new_msg, colour = 'white'):
	#split the message if necessary, among multiple lines
	new_msg = new_msg[:1].upper() + new_msg[1:]
	new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
 
	for line in new_msg_lines:
		#if the buffer is full, remove the first line to make room for the new one
		if len(game_msgs) == MSG_HEIGHT//2:
			del game_msgs[0]
 
		#add the new line as a tuple, with the text and the colour
		game_msgs.append((line, colour))
 
def player_open_door(dx, dy):
	global fov_recompute, game_state
	if player.true_self is not None: #we are wild shaped
		if game_state == 'exploring':
			game_state = 'playing'
			message('Exploration cancelled because you can not open doors in your present form.')
		else:
			message('You can not do that in your present form.')
		return 'didnt-take-turn'
	player.record_last_action('door')
	if is_incapacitated(player): return
	fov_recompute = True
	map[player.x + dx][player.y + dy].open()

def player_close_door(dx, dy):
	global fov_recompute
	if player.true_self is not None: #we are wild shaped
		message('You can not do that in your present form.')
		return 'didnt-take-turn'
	player.record_last_action('door')
	if is_incapacitated(player): return
	fov_recompute = True
	if not is_occupied(player.x + dx, player.y + dy):
		map[player.x + dx][player.y + dy].close()
	
def player_talk(dx, dy):
	global quests, journal

	player.record_last_action('talk')
	if is_incapacitated(player): return
	for actor in actors:
		if actor.x == dx and actor.y == dy:
			if actor.fighter is not None:
				if not is_incapacitated(actor):
					quest_test = None
					for quest in quests:
						if actor.name == quest.quest_giver:
							quest_test = actor
					if quest_test is not None:
						quest_talk(actor)
						return
					elif actor.merchant:
						merchant_talk(actor)
						return
					elif actor.guildmaster is not None:
						guildmaster_talk(actor)
						return
					elif actor.fighter.faction == player.fighter.faction:
						give_order(actor)
						return
					elif actor.fighter.can_join:
						if hasattr(actor.ai, 'master'): #ie, they already follow someone else
							if actor.ai.master is not None:
								message('You fail to convince ' + str(actor.name_for_printing()) + ' to join your cause.', 'white')
								return
						if actor.fighter.asked_to_join is False and actor.fighter.can_join is True:
							if 'lucky' in player.fighter.traits: lucky = True
							else: lucky = False
							cha_roll = d20_roll(lucky=lucky)
							cha_bonus = ABILITY_MODIFIER[player.fighter.charisma]
							if (cha_roll + cha_bonus > 10 + actor.fighter.challenge_rating) or actor.fighter.always_join: #DC 10 + monster CR
								actor.fighter.faction = player.fighter.faction
								actor.fighter.true_faction = player.fighter.faction
								actor.old_ai = actor.ai #store the old ai for later use
								if 'magic' in actor.fighter.proficiencies:
									companion_ai_component = CompanionMagicMonster(player, 5)
								elif 'ranged' in actor.fighter.traits:
									companion_ai_component = CompanionRangedMonster(player, 5)
								else:
									companion_ai_component = CompanionMonster(player, 5)
								actor.ai = companion_ai_component
								companion_ai_component.owner = actor
								player.followers.append(actor)
								message('You convince ' + str(actor.name_for_printing()) + ' to join your cause.', 'green')
							else:
								actor.fighter.asked_to_join = True
								message('You fail to convince ' + str(actor.name_for_printing()) + ' to join your cause.', 'white')
							return
						else:
							if actor.fighter.can_join:
								message('You have already failed to convince ' + str(actor.name_for_printing()) + ' to join you.', 'white')
							else:
								message('You fail to communicate with ' + str(actor.name_for_printing()) + '.', 'white')
							return
					elif actor.flavour_text:
						message(actor.name_for_printing() + ' says: ' + random.choice(actor.flavour_text))
						return
	message('There is no one there to talk to.', 'white')

def quest_talk(actor):
	global quests, journal
	
	### find the quest with this quest giver and with the lowest priority number
	
	active_quest = None
	for quest in quests:
		if actor.name.lower() == quest.quest_giver.lower():
			if active_quest == None or active_quest.priority > quest.priority:
				active_quest = quest
				
	if active_quest is None: return #this should never happen but probably safe to check
	
	### check to see if the quest has been completed, if so, give the completed quest text, give reward, remove quest from list, and then add completed quest name to the journal 
	
	for entry in journal:
		if entry.lower() == active_quest.finish_condition.lower():
			longmsgbox(actor.name_for_printing() + ' says: ' + active_quest.complete_text)
			create_reward(active_quest.reward)
			journal.append(active_quest.name)
			quests.remove(active_quest)
			return
	
	### if not completed, check if there are any prereqs for the quest and if so, check the journal to see if they have been completed, if prereqs are fulfilled then give the quest text 
	
	for prereq in active_quest.prereqs:
		if prereq not in journal:
			if actor.flavour_text:
				message(actor.name_for_printing() + ' says: ' + random.choice(actor.flavour_text)) #just use this dummy text rather than discuss the quest
			return
				
	longmsgbox(actor.name_for_printing() + ' says: ' + active_quest.incomplete_text)
	
def merchant_talk(actor):
	choice = menu('Do you want to purchase or sell items?', ['Purchase items', 'Sell items'], 50)
	if choice == 0:
		merchant_buy(actor)
	elif choice == 1:
		merchant_sell(actor)
		
def guildmaster_talk(actor):
	if actor.guildmaster is None:
		options = ['Guildmaster has no hirelings available.']
		return
		
	price_modifier = 1.0 - (ABILITY_MODIFIER[player.fighter.charisma] / 10)
	list_of_hirelings = []
	
	for hireling in actor.guildmaster:
		list_of_hirelings.append(hireling.name + ' (' + str(round(hireling.value * price_modifier, 2)) + ' gold)')
		
	if len(actor.guildmaster) == 0:
		options = ['Guildmaster has no hirelings available.']
		return
	else:
		choice = menu('Who do you wish to hire?', list_of_hirelings, 24)
	
	if choice is not None:
	
		hireling = actor.guildmaster[choice]
		hireling_cost = round(hireling.value * price_modifier, 2)
		
		if player.gold > hireling_cost:
			player.gold -= hireling_cost
		else:
			message(player.name_for_printing() + ' does not have enough money!')
			return
		
		actor.guildmaster.remove(hireling)
		(hireling.x, hireling.y) = random_unblocked_spot_near(player.x, player.y)
		hireling.fighter.faction = player.fighter.faction
		hireling.fighter.true_faction = player.fighter.faction
		hireling.old_ai = hireling.ai #store the old ai for later use
		if 'magic' in hireling.fighter.proficiencies:
			companion_ai_component = CompanionMagicMonster(player, 5)
		elif 'ranged' in hireling.fighter.traits:
			companion_ai_component = CompanionRangedMonster(player, 5)
		else:
			companion_ai_component = CompanionMonster(player, 5)
		hireling.ai = companion_ai_component
		companion_ai_component.owner = hireling
		player.followers.append(hireling)
		actors.append(hireling)
	
def merchant_sell(actor):
	global player
	
	price_modifier = 0.5 + (ABILITY_MODIFIER[player.fighter.charisma] / 20)
	
	#show a menu with each item of the player's inventory as an option
	if len(player.inventory) == 0:
		options = ['You do not have any items to sell!']
	else:
		options = []
		for item in player.inventory:
			text = item.name_for_printing(definite_article=False)
			if item.quantity is not None:
				text = text + ' (' + str(item.quantity) + ')'
			if item.item:
				if item.item.charges is not None:
					text = text + ' (' + str(item.item.charges) + ')'
			if item.quantity is not None:
				text = text + ' (' + str(round(item.value * price_modifier, 2)) + ' gold each)'
			else:
				text = text + ' (' + str(round(item.value * price_modifier, 2)) + ' gold)'
			options.append(text)
 
	index = menu('Choose an item to sell:', options, INVENTORY_WIDTH + 10)
	if len(player.inventory) == 0 or index == None:
		return
	else:
		sold_item = player.inventory[index]
		
		if sold_item.quantity is not None:
			sold_quantity = text_input('How many do you want to sell?')
			if not sold_quantity.isdigit():
				message('That is not a valid number!')
				return
			else:
				sold_quantity = int(sold_quantity)
			if sold_quantity < 1:
				message('That is not a valid number!')
				return
			elif sold_quantity > sold_item.quantity:
				message('That is more than you have to sell!')
				return
		
		if sold_item.quantity is None:
			item_cost = round(sold_item.value * price_modifier, 2)
		else:
			item_cost = round(sold_item.value * sold_quantity * price_modifier, 2)
		
		player.gold += item_cost 
		
		if sold_item.quantity is None:
			if sold_item.equipment: sold_item.equipment.dequip(player)
			actor.inventory.append(sold_item)
			player.inventory.remove(sold_item)
		else:
			working_item = None
			for item in actor.inventory:
				if item.name == sold_item.name and item != sold_item: #we've found a candidate for merging
					working_item = item
			if working_item == None: #we can't find a merging candidate so create a dummy item of the same type with zero quantity
				working_item = copy.deepcopy(sold_item)
				working_item.quantity = 0
				actor.inventory.append(working_item)
			working_item.quantity += sold_quantity
			sold_item.quantity -= sold_quantity
			if sold_item.quantity == 0:
				if sold_item.equipment: sold_item.equipment.dequip(player)
				player.inventory.remove(sold_item)
		message(player.name_for_printing() + ' sells ' + sold_item.name + ' to ' + actor.name_for_printing() + '.')

def merchant_buy(actor):
	global player
	
	price_modifier = 1.0 - (ABILITY_MODIFIER[player.fighter.charisma] / 20)
	
	#show a menu with each item of the merchant's inventory as an option
	if len(actor.inventory) == 0:
		options = ['Merchant has nothing for sale.']
	else:
		options = []
		for item in actor.inventory:
			text = item.name_for_printing(definite_article=False)
			if item.quantity is not None:
				text = text + ' (' + str(item.quantity) + ')'
			if item.item:
				if item.item.charges is not None:
					text = text + ' (' + str(item.item.charges) + ')'
			if item.quantity is not None:
				text = text + ' (' + str(round(item.value * price_modifier, 2)) + ' gold each' + ')'
			else:
				text = text + ' (' + str(round(item.value * price_modifier, 2)) + ' gold' + ')'
			options.append(text)
 
	index = menu('Choose an item to purchase:', options, INVENTORY_WIDTH + 10)
	if len(actor.inventory) == 0 or index == None:
		return
	else:
		bought_item = actor.inventory[index]
		
		if bought_item.quantity is not None:
			if bought_item.quantity == 1:
				bought_quantity = 1
			else:
				bought_quantity = text_input('How many do you want to buy?')
				if not bought_quantity.isdigit():
					message('That is not a valid number!')
					return
				else:
					bought_quantity = int(bought_quantity)
				if bought_quantity < 1:
					message('That is not a valid number!')
					return
				elif bought_quantity > bought_item.quantity:
					message('That is more than there is for sale!')
					return
		
		if bought_item.quantity is None:
			item_cost = round(bought_item.value * price_modifier, 2)
		else:
			item_cost = round(bought_item.value * bought_quantity * price_modifier, 2)
		
		if player.gold > item_cost:
			player.gold -= item_cost
		else:
			message(player.name_for_printing() + ' does not have enough money!')
			return
		
		if bought_item.quantity is None:
			player.inventory.append(bought_item)
			actor.inventory.remove(bought_item)
		else:
			working_item = None
			for item in player.inventory:
				if item.name == bought_item.name and item != bought_item: #we've found a candidate for merging
					working_item = item
			if working_item == None: #we can't find a merging candidate so create a dummy item of the same type with zero quantity
				working_item = copy.deepcopy(bought_item)
				working_item.quantity = 0
				player.inventory.append(working_item)
			working_item.quantity += bought_quantity
			bought_item.quantity -= bought_quantity
			if bought_item.quantity == 0:
				actor.inventory.remove(bought_item)
		message(player.name_for_printing() + ' buys ' + bought_item.name + ' from ' + actor.name_for_printing() + '.')
	
def give_order(actor, order_all=False):
	player.record_last_action('talk')
	if is_incapacitated(player): return
	if order_all: #dont allow give new name for bulk orders - also applies to describe self
		choice = menu('Choose an order to give:', ['Light torch', 'Put out torch', 'Defend only', 'Move to location', 'Clear previous orders'], 24)
	else:
		choice = menu('Choose an order to give:', ['Light torch', 'Put out torch', 'Defend only', 'Move to location', 'Clear previous orders', 'Inventory management', 'Give new name', 'Dismiss'], 24)
	followers = []
	if actor is not None:
		followers.append(actor)
	if order_all:
		followers = player.followers
	if choice == 0: #torch interactions
		for follower in followers:
			illumination_condition = None
			if follower.fighter:
				for condition in follower.fighter.conditions:
					if condition.name == 'illumination':
						illumination_condition = condition
				if illumination_condition is None: 
					obj = Condition(name='illumination', permanent=True, colour='yellow')
					follower.fighter.conditions.append(obj)
					obj.owner = follower
	if choice == 1: #torch interactions
		for follower in followers:
			illumination_condition = None
			if follower.fighter:
				for condition in follower.fighter.conditions:
					if condition.name == 'illumination':
						illumination_condition = condition
				if illumination_condition is not None: 
					follower.fighter.conditions.remove(illumination_condition)
	if choice == 2: #defend only
		for follower in followers:
			if follower.ai:
				follower.ai.current_order = 'defend'
				follower.ai.current_order_x = None
				follower.ai.current_order_y = None
	if choice == 3: #move to location
		message('Choose a location to move to.', 'white')
		(x, y) = target_tile(can_target_anywhere=True)
		if x is not None:
			for follower in followers:
				if follower.ai:
					follower.ai.current_order = 'guard'
					follower.ai.current_order_x = x
					follower.ai.current_order_y = y
	if choice == 4: #clear orders
		for follower in followers:
			if follower.ai:
				follower.ai.current_order = None
				follower.ai.current_order_x = None
				follower.ai.current_order_y = None
	if choice == 5: #access the menu to control follower's inventory
		inventory_management_menu(actor)
	if choice == 6: #give new name
		name = text_input('Enter the new name:')
		if len(name) > 0: 
			actor.name = name
			actor.custom_name = True
	if choice == 7: #dismiss from party
		actor.ai = actor.old_ai
		actor.fighter.faction = 'neutral'
		actor.fighter.true_faction = 'neutral'
		actor.fighter.always_join = True #make sure that the follower will always rejoin in future
		player.followers.remove(actor)
		choices = ('I will wait here for you', 'Please do not leave me behind', 'Keep yourself safe', 'I hope you know what you are doing', 'I will surely perish if left alone in this place')
		choice = random.choice(choices)
		message(actor.name_for_printing() + ' says: ' + choice + '.', 'white') 
		
def make_hostile(target):
	if target.fighter is not None:
		if target.fighter.faction == 'neutral':
			message(target.name_for_printing() + ' becomes hostile!')
			target.fighter.faction = 'hostile' #note: this is different to the normal monster faction because i still want neutrals to fight monsters even if they turn on the player
	
	### deal with any of the followers of this creature
	
	for follower in target.followers:
		if follower.fighter is not None:
			if follower.fighter.faction == 'neutral':
				message(follower.name_for_printing() + ' becomes hostile!')
				follower.fighter.faction = 'hostile' 
			
	### now we need to make sure that any allied creatures for which the target is not the leader also become hostile - the best way to do this is to search for lists of creatures which contain this target as a follower and then use recursion to ensure that we capture anyone else we need to
	
	for actor in actors:
		if target in actor.followers:
			make_hostile(actor)
		 
def player_move_or_attack(dx, dy):
	global fov_recompute
  
	if is_incapacitated(player): 
		return
	#the coordinates the player is moving to/attacking
	x = player.x + dx
	y = player.y + dy
	
	#try to find an attackable object there
	target = None
	
	#for actor in actors:
	#	if actor.fighter and actor.x == x and actor.y == y:
	#		target = actor
	#		break
	
	if (x, y) in lookup_map:
		if lookup_map[(x, y)].fighter:
			target = lookup_map[(x, y)]
	
	#attack if target found, move otherwise
	if target is not None:
		if player.fighter.faction == target.fighter.faction:
			if is_unconscious(target):
				monster_revive(target, player)
			else:
				player.swap_place(target)
		elif target.fighter.faction == 'neutral':
			if not is_unconscious(target):
				if are_you_sure_prompt() is True:
					make_hostile(target)
					player.fighter.attack(target)
		else:
			if not is_unconscious(target):
				player.fighter.attack(target)
	else:
		if is_blocked(x, y) and is_openable(x, y):
			player_open_door(dx, dy)
		else:
			player.move(dx, dy)
		fov_recompute = True
 
def player_do_nothing():
	player.record_last_action('rest')
 
def player_hide():
	player.record_last_action('action')
	if is_incapacitated(player): 
		return
	for condition in player.fighter.conditions: #find if the player is already hidden and if so, stop hiding
		if condition.name == 'hidden':
			condition.remove_from_actor(player)
			message(player.name_for_printing() + ' steps out from the shadows.')
			return
	#if player was not hidden, then create that new condition and apply it
	for actor in actors:
		if actor != player and actor.fighter.faction != player.fighter.faction:
			if actor.can_see_object(player):
				message('You cannot hide while someone is watching.')
				return
	hide = Condition(name='hidden', permanent=True, colour='white')
	hide.apply_to_actor(player)
	message(player.name_for_printing() + ' slips into the shadows.')
 
def move_followers(monster):
	for actor in monster.followers:
		count = 0
		while True:
			count += 1
			a = random.randint(monster.x - 5, monster.x + 5)
			b = random.randint(monster.y - 5, monster.y + 5)
			if 0 < a < MAP_WIDTH-1 and 0 < b < MAP_HEIGHT-1:
				if not is_blocked(a, b):
					if count < 10:
						if can_walk_between(monster.x, monster.y, a, b):
							actor.x = a
							actor.y = b
							break
					else:
						actor.x = a
						actor.y = b
						break
	update_lookup_map()
		
def menu(header, options, width, can_exit_without_option=True, return_option=False, y_adjust=0, header_colour=None, magic_menu=False, capitalise=True):
	global game_state

	if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

	blt.color('white')
	if game_state == 'playing': 
		blt.clear()
		render_all()
	
	
	if header == '':
		header_height = 0
	else:
		header_height = 1
	menu_h = len(options) + header_height + 2
	width = width + 4 

	menu_x = SCREEN_WIDTH // 2 - width // 2
	menu_y = SCREEN_HEIGHT // 2 - menu_h // 2 + y_adjust
	create_window(menu_x, menu_y + y_adjust, width, menu_h*2-3, header, header_colour)
	
	if magic_menu: #special case to deal with using higher power spell slots when casting
		increased_spell_slot = 0
		
	#print all the options
	y = menu_y + header_height + 1 + y_adjust
	letter_index = ord('a')
	blt.layer(3)
	blt.composition(False)
	for option_text in options:
		if capitalise:
			text = '(' + chr(letter_index) + ') ' + option_text.capitalize()
		else:
			text = '(' + chr(letter_index) + ') ' + option_text
		blt.puts(menu_x+1, y, "[font=log]" + text)
		y += 2
		letter_index += 1
	if magic_menu:
		blt.puts(menu_x+5, y+1, "[font=log]Press number to change level of spell slot: " + str(increased_spell_slot)) 
	blt.refresh()
	while True:
		key = blt.read()
		if key == blt.TK_CLOSE:
			if game_state == 'playing': save_game()
			blt.close()
			sys.exit()
		if blt.check(blt.TK_CHAR):
			key_char = blt.state(blt.TK_CHAR)
		else: 
			key_char = None
		if can_exit_without_option and key == blt.TK_ESCAPE:
			blt.clear_area(BAR_WIDTH,0,VIEW_WIDTH,VIEW_HEIGHT)
			blt.refresh()
			blt.layer(0)
			blt.composition(True)
			return None
		if key_char is not None:
			if magic_menu:
				if chr(key_char) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
					increased_spell_slot = int(chr(key_char))
					blt.puts(menu_x+5, y+1, "[font=log]Press number to change level of spell slot: " + str(increased_spell_slot)) 
					blt.refresh()
			index = key_char - ord('a')
			if index >= 0 and index < len(options): 
				if return_option: 
					blt.clear_area(BAR_WIDTH,0,VIEW_WIDTH,VIEW_HEIGHT)
					blt.refresh()
					blt.layer(0)
					blt.composition(True)
					if magic_menu:
						return options[index], increased_spell_slot
					else: 
						return options[index]
				else: 
					blt.clear_area(BAR_WIDTH,0,VIEW_WIDTH,VIEW_HEIGHT)
					blt.refresh()
					blt.layer(0)
					blt.composition(True)
					if magic_menu:
						return index, increased_spell_slot
					else:
						return index
 
def inventory_menu(header, actor=None, equipped=None):
	global player
	
	if actor is None: actor = player
	#show a menu with each item of the inventory as an option
	if len(actor.inventory) == 0:
		options = ['Inventory is empty.']
	else:
		options = []
		for item in actor.inventory:
			test = False
			if equipped is not None:
				if equipped is True:
					if item.equipment:
						if item.equipment.is_equipped is not None:
							test = True
				if equipped is False:
					if item.equipment:
						if item.equipment.is_equipped is None:
							test = True
			else:
				test = True
			if test:
				text = item.name_for_printing(definite_article=False)
				#show additional information, in case it's equipped
				if item.equipment:
					if item.equipment.is_equipped:
						text = text + ' (' + item.equipment.is_equipped + ')'
				if item.quantity is not None:
					text = text + ' (' + str(item.quantity) + ')'
				if item.item:
					if item.item.charges is not None:
						text = text + ' (' + str(item.item.charges) + ')'
				options.append(text)
 
	if len(options) == 0:
		options = ['No available items.']
	index = menu(header, options, INVENTORY_WIDTH)
 
	#if an item was chosen, return it
	if index is None or len(actor.inventory) == 0: return None
	return actor.inventory[index].item
	
def inventory_management_menu(actor):
	choice = menu('Choose an order to give:', ['Give item to equip', 'Give item to carry', 'Return item', 'Equip item', 'Dequip item', 'Drop item'], 24)
	if choice == 0:
		follower_equip_item(actor)
	if choice == 1:
		follower_carry_item(actor)
	if choice == 2:
		follower_return_item(actor)
	if choice == 3:
		follower_equip_item_from_inventory(actor)
	if choice == 4:
		follower_dequip_item_from_inventory(actor)
	if choice == 5:
		follower_drop_item(actor)
	
def follower_equip_item(actor):
	chosen_item = inventory_menu('Choose an item for your follower to equip.')
	if chosen_item is not None:
		chosen_item = chosen_item.owner
		if chosen_item.equipment:
			chosen_item.equipment.dequip(player)
			player.inventory.remove(chosen_item)
			actor.inventory.append(chosen_item)
			chosen_item.equipment.equip(actor)
		else:
			message('That item can not be equipped.')
			
def follower_carry_item(actor):
	chosen_item = inventory_menu('Choose an item for your follower to carry.')
	if chosen_item is not None:
		chosen_item = chosen_item.owner
		if chosen_item.equipment:
			chosen_item.equipment.dequip(player)
		player.inventory.remove(chosen_item)
		actor.inventory.append(chosen_item)
		
def follower_return_item(actor):
	chosen_item = inventory_menu('Choose an item for your follower to return.', actor)
	if chosen_item is not None:
		chosen_item = chosen_item.owner
		if chosen_item.equipment:
			chosen_item.equipment.dequip(actor)
		actor.inventory.remove(chosen_item)
		player.inventory.append(chosen_item)
		
def follower_equip_item_from_inventory(actor):
	chosen_item = inventory_menu('Choose an item for your follower to equip.', actor, equipped=False)
	if chosen_item is not None:
		chosen_item = chosen_item.owner
		if chosen_item.equipment:
			chosen_item.equipment.equip(actor)

def follower_dequip_item_from_inventory(actor):
	chosen_item = inventory_menu('Choose an item for your follower to dequip.', actor, equipped=True)
	if chosen_item is not None:
		chosen_item = chosen_item.owner
		if chosen_item.equipment:
			chosen_item.equipment.dequip(actor)

def follower_drop_item(actor):
	chosen_item = inventory_menu('Choose an item for your follower to drop.', actor)
	if chosen_item is not None:
		chosen_item = chosen_item.owner
		if chosen_item.equipment:
			chosen_item.item.drop(actor)
	
def magic_menu(header):
	#show a menu with each item of the inventory as an option
	player.record_last_action('action')
	if is_incapacitated(player): return
	if len(player.fighter.spells) == 0:
		options = ['No spells known']
	else:
		can, one, two, three, four, five, six, seven, eight, nine = [], [], [], [], [], [], [], [], [], []
		options = []
		for spell in player.fighter.spells:
			text = spell
			if spell in WIZARD_CANTRIP or spell in CLERIC_CANTRIP or spell in DRUID_CANTRIP or spell in WARLOCK_CANTRIP: 
				text = text + ' (0)'
				can.append(text)
			if spell in WIZARD_1 or spell in CLERIC_1 or spell in DRUID_1 or spell in WARLOCK_1: 
				text = text + ' (1)'
				one.append(text)
			if spell in WIZARD_2 or spell in CLERIC_2 or spell in DRUID_2 or spell in WARLOCK_2: 
				text = text + ' (2)'
				two.append(text)
			if spell in WIZARD_3 or spell in CLERIC_3 or spell in DRUID_3 or spell in WARLOCK_3: 
				text = text + ' (3)'
				three.append(text)
			if spell in WIZARD_4 or spell in CLERIC_4 or spell in DRUID_4 or spell in WARLOCK_4: 
				text = text + ' (4)'
				four.append(text)
			if spell in WIZARD_5 or spell in CLERIC_5 or spell in DRUID_5 or spell in WARLOCK_5: 
				text = text + ' (5)'
				five.append(text)
			if spell in WIZARD_6 or spell in CLERIC_6 or spell in DRUID_6 or spell in WARLOCK_6: 
				text = text + ' (6)'
				six.append(text)
			if spell in WIZARD_7 or spell in CLERIC_7 or spell in DRUID_7 or spell in WARLOCK_7: 
				text = text + ' (7)'
				seven.append(text)
			if spell in WIZARD_8 or spell in CLERIC_8 or spell in DRUID_8 or spell in WARLOCK_8: 
				text = text + ' (8)'
				eight.append(text)
			if spell in WIZARD_9 or spell in CLERIC_9 or spell in DRUID_9 or spell in WARLOCK_9: 
				text = text + ' (9)'
				nine.append(text)
				
		for spell in can:
			options.append(spell)
		for spell in one:
			options.append(spell)
		for spell in two:
			options.append(spell)
		for spell in three:
			options.append(spell)
		for spell in four:
			options.append(spell)
		for spell in five:
			options.append(spell)
		for spell in six:
			options.append(spell)
		for spell in seven:
			options.append(spell)
		for spell in eight:
			options.append(spell)
		for spell in nine:
			options.append(spell)
 
	if player.fighter.role == 'Warlock':
		index = menu(header, options, 50)
		increased_spell_slot = None
	else:
		result = menu(header, options, 50, magic_menu=True)
		if result is not None:
			index = result[0]
			increased_spell_slot = result[1]
		else:
			index = None
	
	if index is None or len(player.fighter.spells) == 0: return None
	
	#if a spell was chosen, return it along with a check to see if we need to use a higher spell slot
	return options[index][:-4], increased_spell_slot
	
def ability_menu(header):
	#show a menu with each item of the inventory as an option
	player.record_last_action('action')
	if is_incapacitated(player): return
	
	possible_abilities = ['arcane recovery', 'turn undead', 'preserve life', 'destroy undead', 'divine intervention', 'divine strike', 'second wind', 'action surge', 'uncanny dodge', 'healing hands', 'wild shape', 'use invisibility', 'hellish rebuke', 'darkness', 'pact of the chain']
	
	abilities = []
	for trait in player.fighter.traits:
		if trait in possible_abilities: abilities.append(trait)
	if len(abilities) == 0:
		abilities = ['No abilities available.']
	index = menu(header, abilities, INVENTORY_WIDTH)
	
	if index is None or len(abilities) == 0: return None
	
	#if a spell was chosen, return it
	return abilities[index]
 
def msgbox(text): #text needs to be a list of strings
	global game_state

	blt.color('white')
	if game_state == 'playing': 
		blt.clear()
		render_all()
		
	width = 0
	height = 0
	
	for line in text: 
		if len(line) > width: 
			width = len(line) # find the longest line and adjust the width to that
	height = len(text) # use the number of lines as the height 
	
	height += 2
	width += 2
	
	menu_x = SCREEN_WIDTH // 2 - width // 2
	menu_y = SCREEN_HEIGHT // 2 - height
	create_window(menu_x, menu_y, width, height*2-3)
		
	#print the text
	blt.layer(3)
	blt.composition(False)
	count = 0
	for line in text:
		blt.puts(menu_x+1, menu_y+1 + count, "[font=log]" + line)
		count += 2
	blt.refresh()
	key = blt.read()
	if key == blt.TK_CLOSE:
		if game_state == 'playing': save_game()
		blt.close()
		sys.exit()
	blt.clear_area(BAR_WIDTH,0,VIEW_WIDTH,VIEW_HEIGHT)
	blt.layer(0)
	blt.composition(True)
	if display_mode is not None: render_all()
	blt.refresh()
	
def longmsgbox(text, width=50): #text needs to be a single string
	global game_state

	new_msg_lines = textwrap.wrap(text, width)
	msgbox(new_msg_lines)

	
def simplemsgbox(text): #simple one line small popup box with a message - text needs to be a string
	global game_state

	blt.color('white')
	if game_state == 'playing': 
		blt.clear()
		render_all()
		blt.refresh()
	
	menu_x = SCREEN_WIDTH // 2 - len(text) // 2
	menu_y = SCREEN_HEIGHT // 2 - 1
	create_window(menu_x, menu_y, len(text)+2, 3)
		
	#print the text
	blt.layer(3)
	blt.composition(False)
	blt.puts(menu_x+1, menu_y+1, "[font=log]" + text, len(text), height=2)
	blt.refresh()
	key = blt.read()
	if key == blt.TK_CLOSE:
		if game_state == 'playing': save_game()
		blt.close()
		sys.exit()
	blt.clear_area(BAR_WIDTH,0,VIEW_WIDTH,VIEW_HEIGHT)
	blt.layer(0)
	blt.composition(True)
	if display_mode is not None and player is not None: render_all()
	blt.refresh()
	
def text_input(text, max_length=14):
	global game_state

	blt.color('white')
	if game_state == 'playing': 
		blt.clear()
		render_all()
		
	width = len(text)+3
	if width < max_length+4: width = max_length+4
	height = 4
	input = ''
	
	menu_x = SCREEN_WIDTH // 2 - width // 2
	menu_y = SCREEN_HEIGHT // 2 - height
	create_window(menu_x, menu_y, width, height*2-3, text)
	blt.layer(3)
	blt.composition(False)
	blt.puts(menu_x+2, menu_y+2, "[font=log]" + input + '_', len(input)+1, height=1)
	while True:
		blt.refresh()
		key = blt.read()
		if key == blt.TK_CLOSE:
			if game_state == 'playing': save_game()
			blt.close()
			sys.exit()
		if blt.check(blt.TK_CHAR):
			key_char = blt.state(blt.TK_CHAR)
		else: 
			key_char = None
		if key == blt.TK_RETURN or key == blt.TK_ESCAPE or key == blt.TK_CLOSE:
			break
		elif key == blt.TK_BACKSPACE and len(input) > 0:
			input = input[:-1]
		elif key_char is not None and len(input) < max_length:
			input = input + chr(key_char)
		blt.puts(menu_x+2, menu_y+2, "[font=log]" + input + '_ ', len(input)+2, height=1)
	blt.clear_area(BAR_WIDTH,0,VIEW_WIDTH,VIEW_HEIGHT)
	blt.layer(0)
	blt.composition(True)
	if display_mode is not None and player is not None: render_all()
	blt.refresh()
	
	return input
		
def create_window(x, y, w, h, title=None, header_colour=None):

	last_bg = blt.state(blt.TK_BKCOLOR)
	blt.composition(False)
	blt.bkcolor('black')
	blt.color('white')
	for i in range(1, 3):
		blt.layer(i)
		blt.clear_area(x-2, y-3, w+3, h+2)
	
	blt.color('white')
	blt.bkcolor('black')
	blt.layer(0)
	# upper border
	border = '┌' + '─' * (w) + '┐'
	blt.puts(x - 1, y - 1, "[font=log]" + border)
	# sides
	for i in range(h):
		line = "[font=log]" + '│' + ' ' * (w) + "[font=log]" + '│'
		blt.puts(x - 1, y + i, line)
		#blt.puts(x + w, y + i, "[font=log]" + '│')
	# lower border
	border = '└' + '─' * (w) + "[font=log]" + '┘'
	blt.puts(x - 1, y + h, "[font=log]" + border)

	if title is not None:
		leng = len(title)
		offset = (w + 2 - leng) // 2
		if header_colour is not None: blt.color(header_colour)
		blt.puts(x + offset, y - 1, "[font=log]" + title)
	
	blt.bkcolor(last_bg)
	blt.color('white')
	blt.layer(0)
	blt.composition(True)
	
def are_you_sure_prompt(text='Are you sure you want to do that? ("y" to confirm)'):
	global game_state

	blt.color('white')
	if game_state == 'playing': 
		blt.clear()
		render_all()
		blt.refresh()
	
	menu_x = SCREEN_WIDTH // 2 - len(text) // 2
	menu_y = SCREEN_HEIGHT // 2 - 1
	create_window(menu_x, menu_y, len(text)+2, 3)
		
	#print the text
	blt.layer(3)
	blt.composition(False)
	blt.puts(menu_x+1, menu_y+1, "[font=log]" + text, len(text), height=2)
	blt.refresh()
	result = False
	key = blt.read()
	if key == blt.TK_CLOSE:
		if game_state == 'playing': save_game()
		blt.close()
		sys.exit()
	if blt.check(blt.TK_CHAR):
		key_char = chr(blt.state(blt.TK_CHAR))
	else: 
		key_char = None
	if key_char is not None:
		if key_char == 'y' or key_char == 'Y':
			result = True
	blt.clear_area(BAR_WIDTH,0,VIEW_WIDTH,VIEW_HEIGHT)
	blt.layer(0)
	blt.composition(True)
	if display_mode is not None and player is not None: render_all()
	blt.refresh()
	return result
	
def handle_keys():
	global key, game_state, autoexplore_target
	key = blt.read()
	if key == blt.TK_CLOSE:
		if game_state == 'playing': save_game()
		blt.close()
		sys.exit()
	if blt.check(blt.TK_CHAR):
		key_char = chr(blt.state(blt.TK_CHAR))
	else: 
		key_char = None
	if key == blt.TK_ESCAPE:
		return 'exit'  #exit game
 
	if game_state == 'playing':
		#movement keys
		#keys which can only take effect when player is not incapacitated
		if not is_incapacitated(player):
			if key == blt.TK_KP_1 or key_char == 'b':
				player_move_or_attack(1, -1)
				return
			elif key == blt.TK_KP_2 or key_char == 'j' or key == blt.TK_DOWN:
				player_move_or_attack(0, -1) 
				return
			elif key == blt.TK_KP_3 or key_char == 'n':
				player_move_or_attack(-1, -1) 
				return
			elif key == blt.TK_KP_4 or key_char == 'h' or key == blt.TK_LEFT:
				player_move_or_attack(1, 0)
				return 
			elif key == blt.TK_KP_5 or key_char == '.':
				player_do_nothing()
				return 
			elif key == blt.TK_KP_6 or key_char == 'l' or key == blt.TK_RIGHT:
				player_move_or_attack(-1, 0) 
				return
			elif key == blt.TK_KP_7 or key_char == 'y':
				player_move_or_attack(1, 1)
				return
			elif key == blt.TK_KP_8 or key_char == 'k' or key == blt.TK_UP:
				player_move_or_attack(0, 1)
				return
			elif key == blt.TK_KP_9 or key_char == 'u':
				player_move_or_attack(-1, 1)
				return
			elif key_char == 'f' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				result = player_ranged_attack()
				return result
			elif key_char == 'F' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				result = player_repeat_ranged_attack()
				return result
			elif key_char == 'o' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				blt.clear()
				message('Select the door you wish to open.', 'white')
				render_all()
				blt.refresh()
				(dx, dy) = target_direction()
				if dx is None: return 'didnt-take-turn'
				player_open_door(dx, dy)
				return
			elif key_char == 'c' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				blt.clear()
				message('Select the door you wish to close.', 'white')
				render_all()
				blt.refresh()
				(dx, dy) = target_direction()
				if dx is None: return 'didnt-take-turn'
				player_close_door(dx, dy)
				return
			elif key_char == 'm' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				menu_result = magic_menu('Press the key next to any spell to cast it.')
				if menu_result is not None:
					spell = menu_result[0]
					increased_spell_slot = menu_result[1]
					if spell is not None:
						result = cast(spell, increased_spell_slot=increased_spell_slot)
						return result
				else: return 'didnt-take-turn'
				if spell == 'healing word': return 'didnt-take-turn'
				return
			elif key_char == 'M' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				result = player_repeat_last_spell()
				return result
			elif key_char == 'a' and not dungeon_branch.overworld:
				ability = ability_menu('Press the key next to any ability to use it.')
				if ability is not None:
					use_ability(ability)
					if ability == 'action surge' or ability == 'second wind': return 'didnt-take-turn' #special case which doesn't take a turn to use
				else: return 'didnt-take-turn'
				return
			elif key_char == 'T' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				give_order(actor=None, order_all=True)
				return
			elif key_char == 't' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				blt.clear()
				message('Select the creature that you wish to talk with.')
				render_all()
				blt.refresh()
				(dx, dy) = target_tile()
				if dx is None: return 'didnt-take-turn'
				player_talk(dx, dy)
				return
			elif key == blt.TK_TAB and not dungeon_branch.overworld:
				player_hide()
				return
			elif key_char == 'g' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				if len(player.inventory) >= 26:
					message('You can not carry any more items.')
					return 'didnt-take-turn'
				#pick up an item
				chosen_item = None
				for item in items:	#look for an item in the player's tile
					if item.x == player.x and item.y == player.y and item.item:
						chosen_item = item
				if chosen_item is not None:
					chosen_item.item.pick_up(player)
				else: return 'didnt-take-turn'
				return
			elif key_char == 'd' and not dungeon_branch.overworld:
				if player.true_self is not None: #we are wild shaped
					message('You can not do that in your present form.')
					return 'didnt-take-turn'
				#show the inventory; if an item is selected, drop it
				chosen_item = inventory_menu('Press the key next to an item to drop it.')
				if chosen_item is not None:
					chosen_item.drop(player)
				else: return 'didnt-take-turn'
				return
			elif key_char == 'z' and not dungeon_branch.overworld:
				player_rest()
				return
			elif key_char == '>':
				#go down stairs, if the player is on them
				test = None
				for item in items:
					if item.links_to is not None:
						if item.x == player.x and item.y == player.y:
							test = item
				if test is not None:
					change_level(test.links_to)
				else: return 'didnt-take-turn'
				return
			elif key_char == '<':
				#go up stairs, if the player is on them
				test = None
				for item in items:
					if item.links_to is not None:
						if item.x == player.x and item.y == player.y:
							test = item
				if test is not None:
					change_level(test.links_to)
				else: return 'didnt-take-turn'
				return
			elif key_char == 'X' and not dungeon_branch.overworld:
				autoexplore_target = None
				game_state = 'exploring'
				return
			elif (key_char == '0' or key_char == '1' or key_char == '2' or key_char == '3' or key_char == '4' or key_char == '5' or key_char == '6' or key_char == '7' or key_char == '8' or key_char == '9') and not dungeon_branch.overworld: #possible macros for spells
				if macros[int(key_char)] is not None: #if a macro for that char has been set
					cast(macros[int(key_char)]) #cast the spell stored in that macro
				else: return 'didnt-take-turn' #if failed, don't cost a turn
				return
		#alternate keys for when player is incapacitated
		if is_incapacitated(player):
			if key == blt.TK_KP_1 or key_char == 'b':
				return 
			elif key == blt.TK_KP_2 or key_char == 'j' or key == blt.TK_DOWN:
				return 
			elif key == blt.TK_KP_3 or key_char == 'n':
				return 
			elif key == blt.TK_KP_4 or key_char == 'h' or key == blt.TK_LEFT:
				return
			elif key == blt.TK_KP_5 or key_char == '.':
				return 
			elif key == blt.TK_KP_6 or key_char == 'l' or key == blt.TK_RIGHT:
				return
			elif key == blt.TK_KP_7 or key_char == 'y':
				return
			elif key == blt.TK_KP_8 or key_char == 'k' or key == blt.TK_UP:
				return
			elif key == blt.TK_KP_9 or key_char == 'u':
				return
		#other miscellaneous commands
		if key_char == 'i' and not dungeon_branch.overworld:
			#show the inventory; if an item is selected, use it - unless we are incapacitated
			chosen_item = inventory_menu('Press the key next to an item to use it.')
			if chosen_item is not None:
				if not is_incapacitated(player): 
					chosen_item.use(player)
					return
				else: 
					message('You can not do that while incapacitated.', 'white')
					return 'didnt-take-turn'
			else: return 'didnt-take-turn'
		#collection of commands which never take up a turn
		if key_char == 'x':
			look()
		elif key_char == '?':
			help_menu()
		elif key_char == '@': 
			examine_menu(player)
		elif key == blt.TK_F1:
			toggle_display_mode()
		elif key == blt.TK_F2:
			macro_menu()
		elif key == blt.TK_F3:
			new_char = select_avatar()
			if new_char is not None:
				player.big_char = new_char
		#elif key == blt.TK_F9:
		#	game_state = 'autoplay'
		#elif key == blt.TK_F10:
		#	make_map()
		return 'didnt-take-turn'
			
def help_menu():
	message = []
	message.append('-- List of commands')
	message.append('')
	message.append('Keypad or vi keys to move')
	message.append('@ - display traits and proficiencies')
	message.append('a - use ability')
	message.append('c - close door')
	message.append('d - drop item')
	message.append('f - fire ranged weapon or use reach weapon')
	message.append('F - fire ranged weapon or use reach weapon at last target')
	message.append('g - get item')
	message.append('i - inventory')
	message.append('m - use magic')
	message.append('M - use last spell against last target')
	message.append('o - open door')
	message.append('t - talk or give orders')
	message.append('T - give orders to all')
	message.append('x - examine a location')
	message.append('X - autoexplore')
	message.append('z - rest and heal')
	message.append('TAB - hide')
	message.append('< - go up stairs')
	message.append('> - go down stairs')
	message.append('+/- - cycle targets')
	message.append('F1 - change display made (ascii/graphical)')
	message.append('F2 - set spell macros')
	message.append('F3 - set player avatar')
	msgbox(message)

def examine_menu(target):
	text = []
	text.append(target.name_for_printing(capitalise=True, definite_article=False))
	text.append('')
	if target.description is not None: #description will be a really long string which will look ugly, so we want to figure out how best to break it down into multiple lines. first, split into individual words. second, add words together until we get a string longer than 30 characters. third, repeat for the rest of the words
		words = target.description.split()
		description_strings = [] #this will be the final product to append
		working_string = ''
		while len(words) > 0:
			working_string += words.pop(0) + ' '
			if len(working_string) > 40:
				description_strings.append(working_string)
				working_string = ''
		description_strings.append(working_string) #append whatever is left over
		text += description_strings
		text.append('')
	if target == player:
		text.append('Traits:')
		text.append('')
		traits = set(target.fighter.traits)
		for trait in traits:
			text.append('  ' + trait.capitalize())
		text.append('')
		text.append('Proficiencies:')
		text.append('')
		proficiencies = set(target.fighter.proficiencies)
		for proficiency in proficiencies:
			text.append('  ' + proficiency.capitalize())
			
	elif target.fighter is not None:
		to_hit_bonus, weapon_in_main_hand, finesse, proficient, two_handed, ranged, reach, base_num_dmg_die, base_dmg_die, dmg_bonus, base_dmg_type, two_weapon_fighting, weapon_in_off_hand, off_to_hit_bonus, off_finesse, off_proficient, off_base_num_dmg_die, off_base_dmg_die, off_dmg_bonus, off_base_dmg_type = get_attack_stats(target)
		defender_ac, equipped_armour, equipped_shield, dex_modifier, armour_proficient, shield_proficient = get_defence_stats(target)
		move_cost, action_cost = get_speed_stats(target)
		
		if weapon_in_main_hand is None: weapon_in_main_hand = target.fighter.natural_weapon
		else: weapon_in_main_hand = weapon_in_main_hand.name_for_printing(definite_article=False)
		if dmg_bonus >= 0: dmg_bonus = '+' + str(dmg_bonus)
		else: dmg_bonus = str(dmg_bonus)
		
		if weapon_in_off_hand is None: weapon_in_off_hand = 'None'
		else: weapon_in_off_hand = weapon_in_off_hand.name_for_printing(definite_article=False)
		if off_dmg_bonus >= 0: off_dmg_bonus = '+' + str(off_dmg_bonus)
		else: off_dmg_bonus = str(off_dmg_bonus)	
		
		if equipped_armour is not None: equipped_armour = equipped_armour.name_for_printing(definite_article=False)
		if equipped_shield is not None: equipped_shield = equipped_shield.name_for_printing(definite_article=False)
		
		traits = set(target.fighter.traits)
		proficiencies = set(target.fighter.proficiencies)
		inventory = target.inventory
		
		number_of_attacks = 1
		for trait in traits:
			if trait == 'extra attack':
				number_of_attacks += 1
		while True:
			if 'extra attack' in traits:
				traits.remove('extra attack')
			else:
				break
		
		text.append('Str: ' + str(target.fighter.strength) + '  Int: ' + str(target.fighter.intelligence))
		text.append('Dex: ' + str(target.fighter.dexterity) + '  Wis: ' + str(target.fighter.wisdom))
		text.append('Con: ' + str(target.fighter.constitution) + '  Cha: ' + str(target.fighter.charisma))
		text.append('')
		text.append('Max HP: ' + str(target.fighter.max_hp))
		text.append('Movement speed: ' + str(int(1/float(move_cost)*3000)) + "'")
		text.append('Number of attacks: ' + str(number_of_attacks))
		text.append('')
		text.append('Main: ' + str(weapon_in_main_hand.capitalize()))
		text.append('To hit bonus: ' + str(to_hit_bonus))
		text.append('Damage: ' + str(base_num_dmg_die) + 'd' + str(base_dmg_die) + dmg_bonus)
		text.append('- ' + base_dmg_type.capitalize())
		if proficient: text.append('- Proficient')
		if finesse: text.append('- Finesse')
		if two_handed: text.append('- Two-handed')
		if ranged: text.append('- Ranged')
		if reach: text.append('- Reach')
		if two_weapon_fighting:
			text.append(' ')
			text.append('Off: ' + str(weapon_in_off_hand.capitalize()))
			text.append('To hit bonus: ' + str(off_to_hit_bonus))
			text.append('Damage: ' + str(off_base_num_dmg_die) + 'd' + str(off_base_dmg_die) + off_dmg_bonus)
			text.append('- ' + off_base_dmg_type.capitalize())
			if off_proficient: text.append('- Proficient')
			if off_finesse: text.append('- Finesse')
		text.append(' ')
		text.append('Armour class: ' + str(defender_ac))
		if equipped_armour is not None: 
			text.append(str(equipped_armour.capitalize()))
			if armour_proficient:
				text.append('- Proficient')
			else:
				text.append('- Not proficient')
		if equipped_shield is not None: 
			text.append(' ')
			text.append(str(equipped_shield.capitalize()))
			if shield_proficient:
				text.append('- Proficient')
			else:
				text.append('- Not proficient')
		text.append('')
		if len(traits) > 0:
			text.append('Traits:')
			text.append('')
			for trait in traits:
				text.append('  ' + trait.capitalize())
			text.append('')
		if len(proficiencies) > 0:
			text.append('Proficiencies:')
			text.append('')
			for proficiency in proficiencies:
				text.append('  ' + proficiency.capitalize())
			text.append('')
		if len(inventory) > 0:
			text.append('Inventory:')
			text.append('')
			
			for item in inventory:
				working_string = '  ' + item.name_for_printing(definite_article=False, capitalise=True)
				if item.equipment:
					if item.equipment.is_equipped is not None: working_string += ' (' + item.equipment.is_equipped + ')'
				text.append(working_string)
	elif target.item is not None:
		return
	else:
		return
	msgbox(text)
	
def toggle_display_mode():
	global display_mode
	
	if display_mode == 'graphics': display_mode = 'ascii big'
	elif display_mode == 'ascii big': display_mode = 'ascii small'
	elif display_mode == 'ascii small': display_mode = 'graphics'
	
def check_level_up():
	#see if the player's experience is enough to level-up
	while player.fighter.clevel < LEVEL_CAP:
		if player.fighter.xp >= XP_TO_LEVEL[player.fighter.clevel+1]:
			player.fighter.clevel += 1
			new_level = player.fighter.clevel
			message(player.name_for_printing() + ' has reached level ' + str(new_level) + '!', 'yellow')
			
			if player.fighter.role == 'Cleric':
				player.fighter.base_max_hp += random.randint(1, 8)
				if new_level == 2:
					simplemsgbox('You gain the abilities: turn undead and preserve life!')
					player.fighter.traits.append('turn undead')
					player.fighter.traits.append('preserve life')
				elif new_level == 3:
					simplemsgbox('You gain new spells as your power increases!')
					player.fighter.spells.append('hold person')
					player.fighter.spells.append('aid')
					player.fighter.spells.append('lesser restoration') 
					player.fighter.spells.append('prayer of healing')
					player.fighter.spells.append('spiritual weapon')
				elif new_level == 4: ability_score_improvement()
				elif new_level == 5: 
					simplemsgbox('You gain the ability: destroy undead!')
					player.fighter.traits.append('destroy undead')
					#placeholder for addition of level 3 spells
				elif new_level == 7:
					pass #placeholder for addition of level 4 spells
				elif new_level == 8: ability_score_improvement()
				elif new_level == 9:
					pass #placeholder for addition of level 5 spells
				elif new_level == 10: 
					simplemsgbox('You gain the ability: divine intervention!')
					player.fighter.traits.append('divine intervention')
				elif new_level == 11:
					pass #placeholder for addition of level 6 spells
				elif new_level == 12: ability_score_improvement()
				elif new_level == 13:
					pass #placeholder for addition of level 7 spells
				elif new_level == 15:
					pass #placeholder for addition of level 8 spells
				elif new_level == 16: ability_score_improvement()
				elif new_level == 17:
					pass #placeholder for addition of level 9 spells
				elif new_level == 19: ability_score_improvement()

			if player.fighter.role == 'Fighter':
				player.fighter.base_max_hp += random.randint(1, 10)
				if new_level == 2: 
					simplemsgbox('You gain the ability: action surge!')
					player.fighter.traits.append('action surge')
				elif new_level == 3: 
					simplemsgbox('You gain the ability: improved critical!')
					player.fighter.traits.append('improved critical')
				elif new_level == 4: ability_score_improvement()
				elif new_level == 5: 
					simplemsgbox('You gain the ability: extra attack!')
					player.fighter.traits.append('extra attack')
				elif new_level == 6: ability_score_improvement()
				elif new_level == 7: 
					simplemsgbox('You gain the ability: remarkable athlete!')
					player.fighter.traits.append('remarkable athlete')
				elif new_level == 8: ability_score_improvement()
				elif new_level == 9: 
					simplemsgbox('You gain the ability: indomitable!')
					player.fighter.traits.append('indomitable')
				elif new_level == 10: add_fighting_style()
				elif new_level == 11: 
					simplemsgbox('You gain the ability: extra attack!')
					player.fighter.traits.append('extra attack')
				elif new_level == 12: ability_score_improvement()
				elif new_level == 14: ability_score_improvement()
				elif new_level == 15: 
					simplemsgbox('You gain the ability: superior critical!')
					player.fighter.traits.append('superior critical')
				elif new_level == 16: ability_score_improvement()
				elif new_level == 18: 
					simplemsgbox('You gain the ability: survivor!')
					player.fighter.traits.append('survivor')
				elif new_level == 19: ability_score_improvement()
				elif new_level == 20: 
					simplemsgbox('You gain the ability: extra attack!')
					player.fighter.traits.append('extra attack')

			if player.fighter.role == 'Rogue':
				player.fighter.base_max_hp += random.randint(1, 8)
				if new_level == 2: 
					simplemsgbox('You gain the ability: cunning action!')
					player.fighter.traits.append('cunning action')
				elif new_level == 4: ability_score_improvement()
				elif new_level == 5: 
					simplemsgbox('You gain the ability: uncanny dodge!')
					player.fighter.traits.append('uncanny dodge')
				elif new_level == 7: 
					simplemsgbox('You gain the ability: evasion!')
					player.fighter.traits.append('evasion')
				elif new_level == 8: ability_score_improvement()
				elif new_level == 10: ability_score_improvement()
				elif new_level == 11: 
					simplemsgbox('You gain the ability: reliable talent!')
					player.fighter.traits.append('reliable talent')
				elif new_level == 12: ability_score_improvement()
				elif new_level == 14: 
					simplemsgbox('You gain the ability: blindsense!')
					player.fighter.traits.append('blindsense')
				elif new_level == 15: 
					simplemsgbox('You gain the ability: slippery mind!')
					player.fighter.traits.append('slippery mind')
				elif new_level == 16: ability_score_improvement()
				elif new_level == 18: 
					simplemsgbox('You gain the ability: elusive!')
					player.fighter.traits.append('elusive')
				elif new_level == 19: ability_score_improvement()
				elif new_level == 20: 
					simplemsgbox('You gain the ability: stroke of luck!')
					player.fighter.traits.append('stroke of luck')
			
			if player.fighter.role == 'Wizard':
				player.fighter.base_max_hp += random.randint(1, 6)
				spell_list = []
				level_1_spells = ['burning hands', 'magic missile', 'mage armour', 'charm person', 'shield', 'sleep', 'thunderwave']
				level_2_spells = ['darkness', 'flaming sphere', 'invisibility', 'magic weapon', 'misty step', 'shatter', 'web'] 
				level_3_spells = ['fireball', 'lightning bolt']
				if new_level >= 1: spell_list.extend(level_1_spells)
				if new_level >= 3: spell_list.extend(level_2_spells)
				if new_level >= 5: spell_list.extend(level_3_spells)
				#need to make sure this is updated with all wizard spells (apart from cantrips) available in game
				for _ in range(1):
					for spell in player.fighter.spells:
						if spell in spell_list:
							spell_list.remove(spell)
					spell_choice = menu('As a Wizard, choose 1 spell on level up:', spell_list, 40, return_option=True, can_exit_without_option=False)
					player.fighter.spells.append(spell_choice)
				if new_level == 2: 
					simplemsgbox('You gain the ability: arcane recovery!')
					player.fighter.traits.append('arcane recovery')
				elif new_level == 4: ability_score_improvement()
				elif new_level == 8: ability_score_improvement()
				elif new_level == 12: ability_score_improvement()
				elif new_level == 16: ability_score_improvement()
				elif new_level == 18: 
					simplemsgbox('You gain the ability: spell mastery!')
					player.fighter.traits.append('spell mastery')
				elif new_level == 20: 
					simplemsgbox('You gain the ability: signature spell!')
					player.fighter.traits.append('signature spell')
					
			if player.fighter.role == 'Druid':
				player.fighter.base_max_hp += random.randint(1, 8)
				if new_level == 2:
					simplemsgbox('You gain the ability: wild shape!')
					player.fighter.traits.append('wild shape')
				elif new_level == 3:
					simplemsgbox('You gain new spells as your power increases!')
					player.fighter.spells.append('flaming sphere')
					player.fighter.spells.append('lesser restoration') 
				elif new_level == 4: ability_score_improvement()
				elif new_level == 5:
					pass #placeholder for addition of level 3 spells
				elif new_level == 7:
					pass #placeholder for addition of level 4 spells
				elif new_level == 8: ability_score_improvement()
				elif new_level == 9:
					pass #placeholder for addition of level 5 spells
				elif new_level == 11:
					pass #placeholder for addition of level 6 spells
				elif new_level == 12: ability_score_improvement()
				elif new_level == 13:
					pass #placeholder for addition of level 7 spells
				elif new_level == 15:
					pass #placeholder for addition of level 8 spells
				elif new_level == 16: ability_score_improvement()
				elif new_level == 17:
					pass #placeholder for addition of level 9 spells
				elif new_level == 19: ability_score_improvement()
				
			if player.fighter.role == 'Warlock':
				player.fighter.base_max_hp += random.randint(1, 8)
				spell_list = []
				level_1_spells = ['charm person', 'hellish rebuke']
				level_2_spells = ['darkness', 'invisibility', 'misty step', 'shatter'] 
				level_3_spells = []
				if new_level >= 1: spell_list.extend(level_1_spells)
				if new_level >= 3: spell_list.extend(level_2_spells)
				if new_level >= 5: spell_list.extend(level_3_spells)
				#need to make sure this is updated with all warlock spells (apart from cantrips) available in game
				for _ in range(1):
					for spell in player.fighter.spells:
						if spell in spell_list:
							spell_list.remove(spell)
					if len(spell_list) > 0:
						spell_choice = menu('As a Warlock, choose 1 spell on level up:', spell_list, 40, return_option=True, can_exit_without_option=False)
						player.fighter.spells.append(spell_choice)
				if new_level == 3: 
					pact_choice = menu('As a Warlock, enter into a pact:', ['pact of the tome', 'pact of the chain'], 41, return_option=True, can_exit_without_option=False)
					if pact_choice == 'pact of the tome':
						simplemsgbox('You gain the ability: pact of the tome!')
						player.fighter.traits.append('pact of the tome')
						spell_list = ['acid splash', 'chill touch', 'fire bolt', 'light', 'poison spray', 'ray of frost', 'shocking grasp', 'resistance', 'sacred flame', 'eldritch blast'] #all possible cantrips - needs to be constantly updated
						for _ in range(3):
							for spell in player.fighter.spells:
								if spell in spell_list:
									spell_list.remove(spell)
							if len(spell_list) > 0:
								spell_choice = menu('As a Warlock with Pact of the Tome, choose 3 cantrips:', spell_list, 51, return_option=True, can_exit_without_option=False)
								player.fighter.spells.append(spell_choice)
					if pact_choice == 'pact of the chain':
						simplemsgbox('You gain the ability: pact of the chain!')
						player.fighter.traits.append('pact of the chain')
				elif new_level == 4: ability_score_improvement()
				elif new_level == 8: ability_score_improvement()
				elif new_level == 12: ability_score_improvement()
				elif new_level == 16: ability_score_improvement()
				
			if player.fighter.race == 'Tiefling':
				if new_level == 3:
					simplemsgbox('You gain the ability: infernal legacy - hellish rebuke!')
					player.fighter.traits.append('hellish rebuke')
				elif new_level == 5:
					simplemsgbox('You gain the ability: infernal legacy - darkness!')
					player.fighter.traits.append('darkness')
			#recalculate real max_hp taking into account potential changes in constitution
			bonus = ABILITY_MODIFIER[player.fighter.constitution] * player.fighter.clevel
			if 'dwarvern toughness' in player.fighter.traits:
				bonus += player.fighter.clevel
			player.fighter.max_hp = player.fighter.base_max_hp + bonus
			player.fighter.hp = player.fighter.max_hp #heal the player on level up

			if 'magic' in player.fighter.proficiencies:
				if player.fighter.role == 'Warlock':
					player.fighter.warlock_spell_slots = WARLOCK_SPELL_SLOTS_PER_LEVEL[player.fighter.clevel]
				else:
					player.fighter.spell_slots = list(SPELL_SLOTS_PER_LEVEL[player.fighter.clevel]) #adjust new number of spell slots
				
			render_all()
			blt.refresh()
			
		else:
			break
		
def ability_score_improvement(amount_to_increase=2):
	for i in range(amount_to_increase):
		has_increased = False
		while not has_increased:
			choice = menu('Choose an ability to improve:', ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma'], 26, can_exit_without_option=False)
			if choice == 0: 
				if player.fighter.base_strength < 20:
					player.fighter.strength += 1
					player.fighter.base_strength += 1
					has_increased = True
				else:
					message('You can not increase that attribute any further.')
			if choice == 1: 
				if player.fighter.base_dexterity < 20:
					player.fighter.dexterity += 1
					player.fighter.base_dexterity += 1
					has_increased = True
				else:
					message('You can not increase that attribute any further.')
			if choice == 2: 
				if player.fighter.base_constitution < 20:
					player.fighter.constitution += 1
					player.fighter.base_constitution += 1
					has_increased = True
				else:
					message('You can not increase that attribute any further.')
			if choice == 3: 
				if player.fighter.base_intelligence < 20:
					player.fighter.intelligence += 1
					player.fighter.base_intelligence += 1
					has_increased = True
				else:
					message('You can not increase that attribute any further.')
			if choice == 4: 
				if player.fighter.base_wisdom < 20:
					player.fighter.wisdom += 1
					player.fighter.base_wisdom += 1
					has_increased = True
				else:
					message('You can not increase that attribute any further.')
			if choice == 5: 
				if player.fighter.base_charisma < 20:
					player.fighter.charisma += 1
					player.fighter.base_charisma += 1
					has_increased = True
				else:
					message('You can not increase that attribute any further.')
	
def add_fighting_style():
	list_of_styles = ['archery', 'defence', 'dueling', 'great weapon fighting', 'protection', 'two-weapon fighting']
	if 'archery' in player.fighter.proficiencies: list_of_styles.remove('archery')
	if 'defence' in player.fighter.proficiencies: list_of_styles.remove('defence')
	if 'dueling' in player.fighter.proficiencies: list_of_styles.remove('dueling')
	if 'great weapon fighting' in player.fighter.proficiencies: list_of_styles.remove('great weapon fighting')
	if 'protection' in player.fighter.proficiencies: list_of_styles.remove('protection')
	if 'two-weapon fighting' in player.fighter.proficiencies: list_of_styles.remove('two-weapon fighting')
	style_choice = menu('Choose an additional fighting style:', list_of_styles, 36, can_exit_without_option=False) 
	player.fighter.proficiencies.append(list_of_styles[style_choice])

def wild_shape_death(monster, attacker):
	global player
	
	message(monster.name_for_printing() + ' reverts to its true form!', 'red')
	if monster == player:
		x = player.x
		y = player.y
		player.x = 0
		player.y = 0
		player.true_self.x = x
		player.true_self.y = y
		player.true_self.fighter.xp = player.fighter.xp #preserve any xp gains
		if player in actors: actors.remove(player)
		player = player.true_self
		actors.append(player)
		for follower in player.followers:
			follower.ai.master = player
		update_lookup_map()
	else:
		x = monster.x
		y = monster.y
		monster.x = 0
		monster.y = 0
		monster.true_self.x = x
		monster.true_self.y = y
		if monster in actors: actors.remove(monster)
		actors.append(monster.true_self)
		for follower in monster.followers:
			follower.ai.master = monster
		update_lookup_map()
	
def player_ko(player, attacker):
	#the game ended!
	global game_state
	message('You were knocked unconscious by ' + attacker.name_for_printing() + '!', 'red')
	player.fighter.hp = 0
	obj = Condition(name='unconscious', duration=40, colour='red')
	player.fighter.conditions.append(obj)
	obj.owner = player
 
def player_death():
	#the game ended!
	global game_state
	game_state = 'dead'
	message('You have died!', 'red')
 
	#for added effect, transform the player into a corpse!
	player.char = '%'
	player.colour = 'red'
 
def monster_death(monster, attacker):
	global familiar
	
	#transform it into a nasty corpse! it doesn't block, can't be
	#attacked and doesn't move
	if (attacker == player or attacker in player.followers) and monster != player and monster not in player.followers: #yield experience to the player but not if the player knocks themselves out or their followers
		player.fighter.xp += int(monster.fighter.xp * PLAYER_XP_MODIFER)
	if attacker == player or attacker in player.followers: 
		message(monster.name_for_printing() + ' is dead! You gain ' + str(int(monster.fighter.xp * PLAYER_XP_MODIFER)) + ' experience points.', 'red')
	else:
		player_can_see = player.can_see_object(monster)
		if player_can_see: message(monster.name_for_printing() + ' is dead!', 'red')
	summoned = False
	for condition in monster.fighter.conditions:
		if condition.name == 'summoned':
			summoned = True
	monster.char = '%'
	monster.small_char = int("0xE510", 16)
	monster.big_char = int("0xE010", 16)
	monster.colour = 'red'
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	if monster in actors: 
		actors.remove(monster)
	for actor in actors: #test to see if we need to tidy up any followers lists
		if monster in actor.followers:
			actor.followers.remove(monster)
		if actor.familiar == monster:
			actor.familiar = None
			familiar = None
	if not summoned:
		items.append(monster)
		send_to_back(monster)
	list_of_items = [] #we need to create a second list because we lose track of item indexes when trying to drop them all at once
	for item in monster.inventory:
		list_of_items.append(item)
	for item in list_of_items:
		item.item.drop(monster)
	journal.append('killed ' + monster.name)
	
def monster_ko_to_death(monster, attacker):
	monster.char = '%'
	monster.small_char = int("0xE510", 16)
	monster.big_char = int("0xE010", 16)
	monster.colour = 'red'
	monster.blocks = False
	if (attacker == player or attacker in player.followers) and monster != player and monster not in player.followers: #yield experience to the player but not if the player knocks themselves out or their followers
		player.fighter.xp += int(monster.fighter.xp * PLAYER_XP_MODIFER)
	if attacker == player or attacker in player.followers: 
		message(monster.name_for_printing() + ' is dead! You gain ' + str(int(monster.fighter.xp * PLAYER_XP_MODIFER)) + ' experience points.', 'red')
	else:
		player_can_see = player.can_see_object(monster)
		if player_can_see: message(monster.name_for_printing() + ' is dead!', 'red')
	monster.fighter = None
	monster.ai = None
	if monster in actors:
		actors.remove(monster)
	for actor in actors: #test to see if we need to tidy up any followers lists
		if monster in actor.followers:
			actor.followers.remove(monster)
	items.append(monster)
	send_to_back(monster)
	list_of_items = [] #we need to create a second list because we lose track of item indexes when trying to drop them all at once
	for item in monster.inventory:
		list_of_items.append(item)
	for item in list_of_items:
		item.item.drop(monster)

def monster_ko(monster, attacker):
	#only do this for allies of the player otherwise it's too annoying, so check for that first
	if monster.fighter.faction == player.fighter.faction:
		#transform it into a nasty corpse! it doesn't block, can't be
		#attacked and doesn't move
		if attacker == player or attacker in player.followers: 
			message(monster.name_for_printing() + ' is knocked unconscious!', 'red')
		else:
			player_can_see = player.can_see_object(monster)
			if player_can_see: message(monster.name_for_printing() + ' is knocked unconscious!', 'red')
		monster.fighter.hp = 0
		obj = Condition(name='unconscious', duration=20, colour='red')
		obj.special = attacker #keep track of this using the special variable
		monster.fighter.conditions.append(obj)
		obj.owner = monster
	else:
		monster_death(monster, attacker)
	
def monster_revive(monster, reviver):
	player_can_see = player.can_see_object(monster)
	for actor in actors:
		if actor.fighter and not is_incapacitated(actor):
			if actor.fighter.faction != reviver.fighter.faction and actor.fighter.faction != 'neutral':
				if reviver.can_see_object(actor):
					if player_can_see: message(monster.name_for_printing() + ' can not be revived with enemies in sight.', 'white')
					return
	if monster == player:
		message(player.name_for_printing() + ' is revived by ' + reviver.name_for_printing() + '!', 'green')
	elif player_can_see:
		message(monster.name_for_printing() + ' is revived by ' + reviver.name_for_printing() + '!', 'green')
	for condition in monster.fighter.conditions:
		if condition.name == 'unconscious':
			condition.remove_from_actor(monster)
	monster.fighter.hp = 1
	
def look():
	(x, y) = target_tile()
	if (x or y) != None:
		list_of_objects = []
		for obj in actors:
			if obj.x == x and obj.y == y and fov_map.fov[obj.y, obj.x]:
				list_of_objects.append(obj)
		for obj in items:
			if obj.x == x and obj.y == y and fov_map.fov[obj.y, obj.x]:
				list_of_objects.append(obj)
		for obj in effects:
			if obj.x == x and obj.y == y and fov_map.fov[obj.y, obj.x]:
				list_of_objects.append(obj)
		
		if len(list_of_objects) > 0:
			names = []
			for object in list_of_objects:
				names.append(object.name_for_printing(definite_article=False, capitalise=True))
			choice = menu('Choose something to examine: ', names, 40, capitalise=False)
			if choice is not None:
				examine_menu(list_of_objects[choice])
		
		
def target_tile(max_range=None, target_radius=None, projectile=False, can_target_anywhere=False, target_hostile_first=True):
	global game_state
	(x, y) = (player.x, player.y)
	tiles_to_redraw = []
	list_of_hostile_actors = []
	list_of_friendly_actors = []
	list_of_actors = []
	list_index = -1 #start below zero because on first iteration will move to zero
	for actor in actors:
		if fov_map.fov[actor.y, actor.x] and light_map[actor.x][actor.y] > 0 and actor != player: #this should mean that it is visible to the player
			if actor.fighter.faction == player.fighter.faction:
				list_of_friendly_actors.append(actor)
			else:
				list_of_hostile_actors.append(actor)
	if target_hostile_first:
		list_of_actors.extend(list_of_hostile_actors)
		list_of_actors.extend(list_of_friendly_actors)
	else:
		list_of_actors.extend(list_of_friendly_actors)
		list_of_actors.extend(list_of_hostile_actors)
	redraw = True
	while True:
		if redraw:
			tiles_to_redraw = []
			tiles_to_redraw.append((x, y, blt.color_from_argb(255, 255, 0, 255)))
			if max_range is not None:
				for dy in range(MAP_HEIGHT): #draw the potential range
					for dx in range(MAP_WIDTH):
						if (dx, dy) != (x, y) and not blocks_sight(dx, dy) and fov_map.fov[dy, dx]:
							if math.sqrt((player.x - dx) ** 2 + (player.y - dy) ** 2) < max_range + 1:
								tiles_to_redraw.append((dx, dy, blt.color_from_argb(64, 128, 64, 128)))
			if projectile: #if projectile, then show trajectory
				tcod.line_init(player.x, player.y, x, y)
				while True:	 
					(dx, dy) = tcod.line_step() #step through all tiles in the line 
					if dx is None: break
					if (dx, dy) != (x, y) and not blocks_sight(dx, dy) and fov_map.fov[dy, dx]:
						tiles_to_redraw.append((dx, dy, blt.color_from_argb(85, 128, 64, 96)))
			if target_radius is not None:
				for dy in range(MAP_HEIGHT): #if area of effect, then colour surrounding tiles
					for dx in range(MAP_WIDTH):
						if (dx, dy) != (x, y) and not blocks_sight(dx, dy) and fov_map.fov[dy, dx]: #isn't the start square, isn't blocked and is in view
							if math.sqrt((x - dx) ** 2 + (y - dy) ** 2) < target_radius + 1: #is in range
								tiles_to_redraw.append((dx, dy, blt.color_from_argb(128, 255, 115, 185)))

			render_all(tiles_to_redraw)
			blt.refresh()
			redraw = False
		key = blt.read()
		if key == blt.TK_CLOSE:
			if game_state == 'playing': save_game()
			blt.close()
			sys.exit()
		if blt.check(blt.TK_CHAR):
			key_char = chr(blt.state(blt.TK_CHAR))
		else: 
			key_char = None
		if key == blt.TK_ESCAPE: return (None, None)

		elif key == blt.TK_RETURN:
			if can_target_anywhere:
				return (x, y)
			else:
				if (fov_map.fov[y, x]) and (max_range is None or player.distance(x, y) < max_range + 1): return (x, y)

		elif key in [blt.TK_UP, blt.TK_KP_8] or key_char == 'k':
			y=y+1
			redraw = True

		elif key in [blt.TK_DOWN, blt.TK_KP_2] or key_char == 'j':
			y=y-1
			redraw = True			

		elif key in [blt.TK_LEFT, blt.TK_KP_4] or key_char == 'h':
			x=x+1
			redraw = True
 
		elif key in [blt.TK_RIGHT, blt.TK_KP_6] or key_char == 'l':
			x=x-1
			redraw = True
 
		elif key == blt.TK_KP_7 or key_char == 'y':
			x=x+1
			y=y+1
			redraw = True
 
		elif key == blt.TK_KP_9 or key_char == 'u':
			x=x-1
			y=y+1
			redraw = True
 
		elif key == blt.TK_KP_1 or key_char == 'b':
			x=x+1
			y=y-1
			redraw = True
 
		elif key == blt.TK_KP_3 or key_char == 'n':
			x=x-1
			y=y-1
			redraw = True
			
		elif key_char == '+':
			if len(list_of_actors) > 0:
				list_index += 1
				if list_index >= len(list_of_actors):
					list_index = 0
				x = list_of_actors[list_index].x
				y = list_of_actors[list_index].y
				redraw = True
		
		elif key_char == '-':
			if len(list_of_actors) > 0:
				list_index -= 1
				if list_index < 0:
					list_index = len(list_of_actors)-1
				x = list_of_actors[list_index].x
				y = list_of_actors[list_index].y
				redraw = True

def target_direction():
	global game_state
	blt.clear()
	render_all()
	blt.refresh()
	while True:
		key = blt.read()
		if key == blt.TK_CLOSE:
			if game_state == 'playing': save_game()
			blt.close()
			sys.exit()
		if blt.check(blt.TK_CHAR):
			key_char = chr(blt.state(blt.TK_CHAR))
		else: 
			key_char = None
		if key == blt.TK_ESCAPE:
			return (None, None)
		elif key in [blt.TK_UP, blt.TK_KP_8] or key_char == 'k': 
			return (0, 1)
		elif key in [blt.TK_DOWN, blt.TK_KP_2] or key_char == 'j': 
			return (0, -1)
		elif key in [blt.TK_LEFT, blt.TK_KP_4] or key_char == 'h':
			return (1, 0)
		elif key in [blt.TK_RIGHT, blt.TK_KP_6] or key_char == 'l': 
			return (-1, 0)
		elif key == blt.TK_KP_7 or key_char == 'y':	
			return (1, 1)
		elif key == blt.TK_KP_9 or key_char == 'u':
			return (-1, 1)
		elif key == blt.TK_KP_1 or key_char == 'b':
			return (1, -1)
		elif key == blt.TK_KP_3 or key_char == 'n':
			return (-1, -1)
 
def target_monster(max_range=None, target_radius=None, projectile=False, can_target_self=False, target_hostile_first=True):
	global last_target
	
	#returns a clicked monster inside FOV up to a range, or None if right-clicked
	while True:
		(x, y) = target_tile(max_range, target_radius, projectile, target_hostile_first)
		if x is None:  #player cancelled
			return None
 
		#return the first clicked monster, otherwise continue looping
		for obj in actors:
			if obj.x == x and obj.y == y and obj.fighter and obj != player:
				last_target = obj
				return obj
			if can_target_self:
				if obj.x == x and obj.y == y and obj.fighter and obj == player:
					return obj
 
def closest_monster():
	#find closest enemy, up to a maximum range, and in the player's FOV
	closest_enemy = None
	closest_dist = 10  #start with (slightly more than) maximum range
 
	for actor in actors:
		if actor.fighter and not actor == player and player.can_see_object(actor):
			if actor.fighter.faction != player.fighter.faction:
				#calculate distance between this object and the player
				dist = player.distance_to(actor)
				if dist < closest_dist:	 #it's closer, so remember it
					closest_enemy = actor
					closest_dist = dist
	return closest_enemy
	
def player_rest():
	global game_state, rest_counter
	
	if is_incapacitated(player): return
	path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
	food = None
	test = False
	for item in player.inventory:
		if item.name == 'food rations':
			if item.quantity > 0:
				food = item
	for actor in actors:
		if actor.fighter:
			if actor.fighter.hp > 0:
				if actor.fighter.faction != player.fighter.faction: 
					tcod.path_compute(path, player.x, player.y, actor.x, actor.y)
					if 0 < tcod.path_size(path) < 20: #if an enemy is within 20 steps, you can't rest
						test = True
					if fov_map.fov[actor.y, actor.x]: #if an enemy is in sight, you can't rest
						test = True
	if food is None:
		message('You can not rest without any food rations.', 'white')
	elif test: 
		message('You can not rest with enemies nearby!', 'white')
	else:
		message('You bandage your wounds and rest for a few hours...', 'white')
		game_state = 'resting'
		rest_counter = 50
		for actor in actors:
			if actor.fighter:
				actor.fighter.hp = actor.fighter.max_hp #heal everyone
				actor.fighter.temp_hp = 0
				if 'magic' in actor.fighter.proficiencies:
					if actor.fighter.role == 'Warlock':
						actor.fighter.warlock_spell_slots = WARLOCK_SPELL_SLOTS_PER_LEVEL[actor.fighter.clevel]
					else:
						actor.fighter.spell_slots = list(SPELL_SLOTS_PER_LEVEL[actor.fighter.clevel]) #reset spell levels
				for condition in actor.fighter.conditions: #clean up any conditions which reset on resting
					if condition.remove_on_rest: condition.remove_from_actor(actor)
			for item in actor.inventory: #reset charges on items in everyone's inventory
				if item.item:
					if item.item.max_charges is not None:
						if item.item.recharges:
							item.item.charges = item.item.max_charges
		for item in items: #reset charges on any items on the ground
			if item.item:
				if item.item.max_charges is not None:
					if item.item.recharges:
						item.item.charges = item.item.max_charges
		food.use_quantity(player)

def player_ranged_attack(target=None): #deal with missile attacks and reach attacks
	if is_incapacitated(player): 
		return
	launcher = None
	quiver = None
	has_ammo = False
	ammo_limit = None
	thrown = False
	reach = False
	if 'reach' in player.fighter.traits:
		reach_range = 2
		reach = True
	else:
		reach_range = 1
	for item in player.inventory:
		if item.equipment is not None:
			if item.equipment.is_equipped:
				if item.equipment.is_equipped == 'main hand':
					if 'launcher' in item.equipment.properties:
						reach = False
						launcher = item
					if 'reach' in item.equipment.properties:
						reach = True
						reach_range += 1
				if item.equipment.is_equipped == 'quiver':
					quiver = item

	if launcher is not None:
		if quiver is not None:
			if launcher.name == 'shortbow' or launcher.name == 'longbow':
				test_string = 'arrows'
			if launcher.name == 'light crossbow' or launcher.name == 'heavy crossbow' or launcher.name == 'hand crossbow':
				test_string = 'bolts'
			if launcher.name == 'sling':
				test_string = 'bullets'
			if launcher.name == 'blowgun':
				test_string = 'needles'
			if quiver.name == test_string: 
				has_ammo = True
				ammo_limit = quiver.quantity

	if launcher is None and quiver:
		if 'thrown' in quiver.equipment.properties:
			thrown = True
			
	if not reach:
		if launcher is None and quiver is None: 
			message('You have nothing equipped to fire with.', 'white')
			return 'didnt-take-turn'
		if launcher and not has_ammo:
			message('You have no ammunition equipped to fire with.', 'white')
			return 'didnt-take-turn'
		if launcher is None and quiver:
			if not thrown:
				message('You have nothing equipped to fire with.', 'white')
				return 'didnt-take-turn'
				
	if target is None:
		message('Select a target to fire at.', 'white')
		if reach and not thrown: #wielding a reach weapon and no ranged weapon on standby
			target = target_monster(max_range=reach_range)
		else: 
			target = target_monster(projectile=True)

	if target:
		if reach and not thrown:
			if player.distance_to(target) >= reach_range+1: #we are reaching but have no thrown weapon as a backup and the target is out of range for some reason
				message('You can not reach that far with this weapon.', 'white')
				return 'didnt-take-turn'
	
	if target is not None:
		#if we have a reach weapon and a target within range, then attack with the reach weapon as the first option. if we have a reach weapon and no target within range, then fall back onto the thrown weapon
		if reach and player.distance_to(target) < reach_range+1:
				player.fighter.attack(target)
		else:
			ammo_used = player.fighter.attack(target, ranged=True, ammo_limit=ammo_limit)
			if quiver.quantity is not None:
				player.last_quiver = quiver
				#make another instance of the ammo at the target location 50% of the time for each projectile
				for j in range(ammo_used):
					if random.randint(1, 2) == 2:
						new_quiver = copy.deepcopy(quiver)
						new_quiver.quantity = 1
						new_quiver.x = target.x
						new_quiver.y = target.y
						items.append(new_quiver)
				#deal with using ammo from the initial quiver
				quiver.use_quantity(player, ammo_used)
				merge_items() #tidy up items by merging like quantities 
			else:
				player.last_quiver = quiver
				quiver.equipment.dequip(player)
				player.inventory.remove(quiver)
				quiver.x = target.x
				quiver.y = target.y
				items.append(quiver)
	else:
		return 'didnt-take-turn'

def player_repeat_ranged_attack():
	global last_target
	
	#first check if there is still a legitimate last target stored
	if last_target is not None:
		if not last_target.fighter or is_incapacitated(last_target):
			last_target = None
	#if not, check if there is a hostile within sight and substitute that
	last_target = closest_monster()
	
	if last_target is not None:
		if player.can_see_object(last_target):
			result = player_ranged_attack(last_target)
			return result
		else:
			message('No target to fire at.', 'white')
			return 'didnt-take-turn'
	else:
		message('No target to fire at.', 'white')
		return 'didnt-take-turn'
		
def player_repeat_last_spell():
	global last_target, last_spell
	
	if last_spell is None: return
	#first check if there is still a legitimate last target stored
	if last_target is not None:
		if not last_target.fighter or is_incapacitated(last_target):
			last_target = None
	#if not, check if there is a hostile within sight and substitute that
	last_target = closest_monster()
	
	if last_target is not None:
		if player.can_see_object(last_target):
			result = cast(last_spell, target=last_target)
			return result
		else:
			message('No target to cast spell at.', 'white')
			return 'didnt-take-turn'
	else:
		message('No target to cast spell at.', 'white')
		return 'didnt-take-turn'
			
###
### ABILITY FUNCTIONS
###

def use_ability(ability):

	if ability == 'arcane recovery': use_arcane_recovery(player)
	if ability == 'turn undead': use_turn_undead(player)
	if ability == 'preserve life': use_preserve_life(player)
	if ability == 'destroy undead': use_destroy_undead(player)
	if ability == 'divine intervention': use_divine_intervention(player)
	if ability == 'divine strike': use_divine_strike(player)
	if ability == 'second wind': use_second_wind(player)
	if ability == 'action surge': use_action_surge(player)
	if ability == 'uncanny dodge': use_uncanny_dodge(player)
	if ability == 'healing hands': use_healing_hands(player)
	if ability == 'wild shape': use_wild_shape(player)
	if ability == 'use invisibility': use_invisibility(player)
	if ability == 'hellish rebuke': use_hellish_rebuke(player)
	if ability == 'darkness': use_darkness(player)
	if ability == 'pact of the chain': use_pact_of_the_chain(player)
	
def use_arcane_recovery(user):
	test = False
	for condition in user.fighter.conditions:
		if condition.name == 'used arcane recovery':
			test = True
	if test:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')
	else:
		spell_levels = int(math.ceil(float(user.fighter.clevel) // 2)) #half the caster's level rounded up
		one_select, two_select, three_select, four_select, five_select = (0,)*5
		selector = 1
		while True:
			change = 0
			blt.clear()
			blt.color('white')
			blt.puts(SCREEN_WIDTH//2-15, SCREEN_HEIGHT//2-10, '[font=log]Choose which spell slots to recover:')
			blt.puts(SCREEN_WIDTH//2-14, SCREEN_HEIGHT//2-5, '[font=log]Points remaining - ' + str(spell_levels))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2-2, '[font=log]Level 1 - ' + str(one_select+user.fighter.spell_slots[0]))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2, '[font=log]Level 2 - ' + str(two_select+user.fighter.spell_slots[1]))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2+2, '[font=log]Level 3 - ' + str(three_select+user.fighter.spell_slots[2]))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2+4, '[font=log]Level 4 - ' + str(four_select+user.fighter.spell_slots[3]))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2+6, '[font=log]Level 5 - ' + str(five_select+user.fighter.spell_slots[4]))
			blt.puts(SCREEN_WIDTH//2-23, SCREEN_HEIGHT-3, '[font=log]Up/down to select and left/right to change values')
			blt.color('red')
			blt.puts(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 + (selector * 2) - 4, '[font=log]*')
			blt.refresh()
			key = blt.read()
			if key == blt.TK_CLOSE:
				if game_state == 'playing': save_game()
				blt.close()
				sys.exit()
			if blt.check(blt.TK_CHAR):
				key_char = chr(blt.state(blt.TK_CHAR))
			else: 
				key_char = None
			if key == blt.TK_ESCAPE:
				break
			elif key == blt.TK_RETURN:
				break
			elif key in [blt.TK_UP, blt.TK_KP_8] or key_char == 'k':
				if selector > 1:
					selector = selector - 1
			elif key in [blt.TK_DOWN, blt.TK_KP_2] or key_char == 'j':
				if selector < 5:
					selector = selector + 1
			elif key in [blt.TK_LEFT, blt.TK_KP_4] or key_char == 'h':
				change = -1
			elif key in [blt.TK_RIGHT, blt.TK_KP_6] or key_char == 'l':
				change = 1
			if change != 0:
				if selector == 1: 
					if one_select + change + user.fighter.spell_slots[0] >= user.fighter.spell_slots[0] and one_select + change + user.fighter.spell_slots[0] <= SPELL_SLOTS_PER_LEVEL[user.fighter.clevel][0]: 
						if (spell_levels >= 1 and change > 0) or change < 0:
							one_select = one_select + change
							spell_levels = spell_levels - (1 * change)
				elif selector == 2: 
					if two_select + change + user.fighter.spell_slots[1] >= user.fighter.spell_slots[1] and two_select + change + user.fighter.spell_slots[1] <= SPELL_SLOTS_PER_LEVEL[user.fighter.clevel][1]: 
						if (spell_levels >= 2 and change > 0) or change < 0:
							two_select = two_select + change
							spell_levels = spell_levels - (2 * change)
				elif selector == 3: 
					if three_select + change + user.fighter.spell_slots[2] >= user.fighter.spell_slots[2] and three_select + change + user.fighter.spell_slots[2] <= SPELL_SLOTS_PER_LEVEL[user.fighter.clevel][2]: 
						if (spell_levels >= 3 and change > 0) or change < 0:
							three_select = three_select + change
							spell_levels = spell_levels - (3 * change)
				elif selector == 4: 
					if four_select + change + user.fighter.spell_slots[3] >= user.fighter.spell_slots[3] and four_select + change + user.fighter.spell_slots[3] <= SPELL_SLOTS_PER_LEVEL[user.fighter.clevel][3]: 
						if (spell_levels >= 4 and change > 0) or change < 0:
							four_select = four_select + change
							spell_levels = spell_levels - (4 * change)
				elif selector == 5: 
					if five_select + change + user.fighter.spell_slots[4] >= user.fighter.spell_slots[4] and five_select + change + user.fighter.spell_slots[4] <= SPELL_SLOTS_PER_LEVEL[user.fighter.clevel][4]: 
						if (spell_levels >= 5 and change > 0) or change < 0:
							five_select = five_select + change
							spell_levels = spell_levels - (5 * change)
		change = False
		if one_select > 0:
			user.fighter.spell_slots[0] = user.fighter.spell_slots[0] + one_select
			change = True
		if two_select > 0:
			user.fighter.spell_slots[1] = user.fighter.spell_slots[1] + two_select
			change = True
		if three_select > 0:
			user.fighter.spell_slots[2] = user.fighter.spell_slots[2] + three_select
			change = True
		if four_select > 0:
			user.fighter.spell_slots[3] = user.fighter.spell_slots[3] + four_select
			change = True
		if five_select > 0:
			user.fighter.spell_slots[4] = user.fighter.spell_slots[4] + five_select
			change = True
		if change:
			message(user.name_for_printing() + ' uses arcane recovery.')
			obj = Condition(name='used arcane recovery', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest, or more times if higher level
			obj.owner = user 
			user.fighter.conditions.append(obj)
		blt.clear()
		blt.refresh()
	
def use_turn_undead(user):
	channel_divinity_count = 0
	for condition in user.fighter.conditions:
		if condition.name == 'used channel divinity':
			channel_divinity_count += 1
	#check to see if we can still channel divinity based on character level 
	if user.fighter.clevel >= 18: number_of_uses = 3
	elif user.fighter.clevel >= 6: number_of_uses = 2
	else: number_of_uses = 1
	if channel_divinity_count >= number_of_uses:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')
	else:
		message(user.name_for_printing() + ' channels divinity and rebukes nearby undead.', 'white')
		obj = Condition(name='used channel divinity', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest, or more times if higher level
		obj.owner = user 
		user.fighter.conditions.append(obj)
		for actor in actors:
			if actor.fighter:
				if 'undead' in actor.fighter.traits:
					if actor.can_see_object(player):
						difficulty = user.fighter.spell_dc()
						result = actor.fighter.saving_throw('wisdom', difficulty)
						if result == False: # failed saving throw
							message(actor.name_for_printing() + ' cowers away from the holy symbol.', 'white')
							old_ai = actor.ai
							actor.ai = ScaredMonster(old_ai, num_turns=20, scared_of=user)
							actor.ai.owner = actor  #tell the new component who owns it
						else:
							message(actor.name_for_printing() + ' resists the effect.', 'white')
	
def use_preserve_life(user):
	channel_divinity_count = 0
	for condition in user.fighter.conditions:
		if condition.name == 'used channel divinity':
			channel_divinity_count += 1
	#check to see if we can still channel divinity based on character level 
	if user.fighter.clevel >= 18: number_of_uses = 3
	elif user.fighter.clevel >= 6: number_of_uses = 2
	else: number_of_uses = 1
	if channel_divinity_count >= number_of_uses:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')
	else:
		message(user.name_for_printing() + ' channels divinity and heals those in need.', 'white')
		obj = Condition(name='used channel divinity', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest, or more times if higher level
		obj.owner = user 
		user.fighter.conditions.append(obj)
		message('Select as many targets within sight as you would like to share the healing power. Press Esc when finished.', 'white')
		targets = []
		while True:
			target = target_monster(can_target_self=True, target_hostile_first=False)
			if target is not None:
				if target.fighter:
					if 'undead' not in target.fighter.traits and 'construct' not in target.fighter.traits:
						targets.append(target)
			else:
				break
		if len(targets) > 0:
			list(set(targets)) #this will remove duplicates and tidy up the list
			power = user.fighter.clevel * 5
			for target in targets:
				if target.fighter.hp < (target.fighter.max_hp // 2):
					heal_amount = (target.fighter.max_hp // 2) - target.fighter.hp
					if heal_amount > power: heal_amount = power
					target.fighter.heal(heal_amount)
					message(target.name_for_printing() + ' regains ' + str(heal_amount) + ' hit points.', 'white')
					power -= heal_amount
					explosion_effect(target.x, target.y, 1, [255,255,0])
		else:
			message('With no targets selected, the divine power dissipates.', 'white')
	
def use_destroy_undead(user):
	pass
	
def use_divine_intervention(user):
	pass 
	
def use_divine_strike(user):
	pass
	
def use_second_wind(user):
	test = False
	for condition in user.fighter.conditions:
		if condition.name == 'used second wind':
			test = True
	if test is not True:
		obj = Condition(name='used second wind', permanent=True, visible=False, remove_on_rest=True)
		obj.owner = user 
		user.fighter.conditions.append(obj)
		heal_amount = dice_roll(1, 10) + user.fighter.clevel
		if heal_amount > (user.fighter.max_hp - user.fighter.hp): #make sure we aren't trying to heal above maximum  
			heal_amount = (user.fighter.max_hp - user.fighter.hp)
		user.fighter.heal(heal_amount)
		message(user.name_for_printing() + ' uses second wind and regains ' + str(heal_amount) + ' hit points.', 'white')
	else:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')

def use_action_surge(user):
	test = False
	for condition in user.fighter.conditions:
		if condition.name == 'used action surge':
			test = True
	if test is not True:
		obj = Condition(name='used action surge', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest
		obj.owner = user 
		user.fighter.conditions.append(obj)
		#obj = Condition(name='action surge', duration=0, colour='red')
		#obj.owner = user  #this object allows us to take that extra turn and expires in 1 turn
		#user.fighter.conditions.append(obj)
		user.cooldown -= STANDARD_TURN_LENGTH
		message(user.name_for_printing() + ' uses action surge and moves with extra speed.', 'white')
	else:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')
	
def use_uncanny_dodge(user):
	pass
	
def use_healing_hands(user, target=None):
	test = False
	for condition in user.fighter.conditions:
		if condition.name == 'used healing hands':
			test = True
	if test is not True:
		if target is None and user == player:
			message('Select a target for the spell.', 'white')
			target = target_monster(max_range=1, can_target_self=True, target_hostile_first=False)
		if target is not None:
			if 'undead' not in target.fighter.traits and 'construct' not in target.fighter.traits:
				healing = user.fighter.clevel
				max_heal = target.fighter.max_hp - target.fighter.hp
				if healing > max_heal: healing = max_heal
				if healing == 0:
					message(user.name_for_printing() + ' uses healing hands on ' + target.name_for_printing() + ' but it has no effect.', 'white')
				else:
					message(user.name_for_printing() + ' uses healing hands on ' + target.name_for_printing() + ' and heals ' + str(healing) + ' damage.', 'white')
					target.fighter.heal(healing)
			obj = Condition(name='used healing hands', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest
			obj.owner = user 
			user.fighter.conditions.append(obj)
	else:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')
		
def use_wild_shape(user):
	global player, actors
	test = 0
	if user.true_self is not None:
		user.true_self.x = user.x
		user.true_self.y = user.y
		user.true_self.fighter.xp = user.fighter.xp #preserve any xp gains
		actors.remove(player)
		player = user.true_self
		actors.append(player)
		for follower in player.followers:
			follower.ai.master = player
		update_lookup_map()
	else:
		for condition in user.fighter.conditions:
			if condition.name == 'used wild shape':
				test += 1
		if test < 2:
			possible_shapes = []
			if user.fighter.clevel >= 2: possible_shapes = possible_shapes + ['axe beak', 'boar', 'giant bat', 'giant frog', 'giant lizard', 'giant poisonous snake', 'giant wolf spider', 'panther', 'wolf']
			if user.fighter.clevel >= 4: possible_shapes = possible_shapes + ['ape', 'black bear', 'crocodile', 'giant wasp', 'worg'] 
			if user.fighter.clevel >= 8: possible_shapes = possible_shapes + ['brown bear', 'dire wolf', 'giant spider', 'lion', 'tiger']
			choice = menu('Choose a shape to transform  into:', possible_shapes, 40)
			if choice is not None:
				text = possible_shapes[choice]
				text = text.replace(' ', '_')
				func_name = 'create_' + text
				new_form = eval(func_name)(player.x, player.y)
				new_form.ai = None
				new_form.fighter.death_function = wild_shape_death
				new_form.fighter.faction = player.fighter.faction
				new_form.fighter.true_faction = player.fighter.faction
				new_form.fighter.traits.append('wild shape')
				new_form.fighter.conditions = copy.deepcopy(player.fighter.conditions)
				new_form.fighter.intelligence = player.fighter.intelligence
				new_form.fighter.wisdom = player.fighter.wisdom
				new_form.fighter.charisma = player.fighter.charisma
				new_form.fighter.xp = player.fighter.xp
				new_form.fighter.clevel = player.fighter.clevel
				new_form.followers = player.followers
				obj = Condition(name='used wild shape', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest
				obj.owner = user 
				user.fighter.conditions.append(obj)
				actors.remove(player)
				new_form.true_self = player #keep a record of the old player's form
				player = new_form
				actors.append(player)
				for follower in player.followers:
					follower.ai.master = player
				update_lookup_map()
		else:
			message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')

def use_invisibility(user):
	obj = Condition(name='invisibility', colour='han', duration=100)
	user.fighter.conditions.append(obj)
	obj.owner = user
	message(user.name_for_printing() + ' uses invisibility and fades from sight.', 'white')
	
def use_hellish_rebuke(user):
	test = False
	for condition in user.fighter.conditions:
		if condition.name == 'used infernal legacy':
			test = True
	if test is not True:
		obj = Condition(name='used infernal legacy', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest
		obj.owner = user 
		user.fighter.conditions.append(obj)
		cast_hellish_rebuke(user, level=2) #tieflings use this as a 2nd level spell
	else:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')
		
def use_darkness(user):
	test = False
	for condition in user.fighter.conditions:
		if condition.name == 'used infernal legacy':
			test = True
	if test is not True:
		obj = Condition(name='used infernal legacy', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest
		obj.owner = user 
		user.fighter.conditions.append(obj)
		cast_darkness(user)
	else:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')
			
def use_pact_of_the_chain(user):
	test = False
	for condition in user.fighter.conditions:
		if condition.name == 'used pact of the chain':
			test = True
	if test is not True:
		obj = Condition(name='used pact of the chain', permanent=True, visible=False, remove_on_rest=True) #this object prevents us from using it twice without rest
		obj.owner = user 
		user.fighter.conditions.append(obj)
		cast_find_familiar(user)
	else:
		message(user.name_for_printing() + ' needs to rest before using that ability again.', 'white')
			
###
### MAGIC FUNCTIONS
###
				
def cast(spell, target=None, increased_spell_slot=0): #function to turn keyboard input into player spells
	global last_spell

	if spell in WIZARD_CANTRIP or spell in CLERIC_CANTRIP or spell in DRUID_CANTRIP or spell in WARLOCK_CANTRIP: level = 0
	if spell in WIZARD_1 or spell in CLERIC_1 or spell in DRUID_1 or spell in WARLOCK_1: level = 1
	if spell in WIZARD_2 or spell in CLERIC_2 or spell in DRUID_2 or spell in WARLOCK_2: level = 2
	if spell in WIZARD_3 or spell in CLERIC_3 or spell in DRUID_3 or spell in WARLOCK_3: level = 3
	if spell in WIZARD_4 or spell in CLERIC_4 or spell in DRUID_4 or spell in WARLOCK_4: level = 4
	if spell in WIZARD_5 or spell in CLERIC_5 or spell in DRUID_5 or spell in WARLOCK_5: level = 5
	if spell in WIZARD_6 or spell in CLERIC_6 or spell in DRUID_6 or spell in WARLOCK_6: level = 6
	if spell in WIZARD_7 or spell in CLERIC_7 or spell in DRUID_7 or spell in WARLOCK_7: level = 7
	if spell in WIZARD_8 or spell in CLERIC_8 or spell in DRUID_8 or spell in WARLOCK_8: level = 8
	if spell in WIZARD_9 or spell in CLERIC_9 or spell in DRUID_9 or spell in WARLOCK_9: level = 9
	
	### deal with increases in spell power
	
	if level != 0: #we don't need to worry if there is an attempt to use a higher level spell slot with a cantrip - it just should be ignored
		if player.fighter.role == 'Warlock': #warlocks get automatic spell slot level increases
			if player.fighter.clevel >= 9:
				level = 5
			elif player.fighter.clevel >= 7:
				level = 4
			elif player.fighter.clevel >= 5:
				level = 3
			elif player.fighter.clevel >= 3:
				level = 2
			else:
				level = 1
		elif increased_spell_slot != 0: #this means that we have user input to use a higher spell slot
			if increased_spell_slot > level: #ignore this input if the selected spell slot is lower or equal to the default one
				level = increased_spell_slot
	
	### deal with available spell slots and tracking the use of these
	
	if level != 0: #no checks for cantrips
		if player.fighter.role == 'Warlock':
			if player.fighter.warlock_spell_slots > 0:
				player.fighter.warlock_spell_slots -= 1
			else:
				message('Not enough spell slots to cast that spell.')
				return 'didnt-take-turn'
		else:
			if player.fighter.spell_slots[level-1] > 0:
				player.fighter.spell_slots[level-1] -= 1
			else:
				message('Not enough spell slots to cast that spell.')
				return 'didnt-take-turn'
			
	### CROSSOVER SPELLS
	#CANTRIP
	if spell == 'light': cast_light(player, level=level)
	#LEVEL 1
	if spell == 'find familiar': cast_find_familiar(player, level=level)
	#LEVEL 2
	if spell == 'hold person': cast_hold_person(player, target=target, level=level)
	
	### WIZARD
	#CANTRIP
	if spell == 'acid splash': cast_acid_splash(player, target=target, level=level)
	if spell == 'fire bolt': cast_fire_bolt(player, target=target, level=level)
	if spell == 'poison spray': cast_poison_spray(player, target=target, level=level)
	if spell == 'ray of frost': cast_ray_of_frost(player, target=target, level=level)
	if spell == 'shocking grasp': cast_shocking_grasp(player, target=target, level=level) 
	if spell == 'chill touch': cast_chill_touch(player, target=target, level=level)
	#LEVEL 1
	if spell == 'burning hands': cast_burning_hands(player, level=level)
	if spell == 'charm person': cast_charm_person(player, target=target, level=level)
	if spell == 'mage armour': cast_mage_armour(player, level=level)
	if spell == 'magic missile': cast_magic_missile(player, target=target, level=level)
	if spell == 'shield': cast_shield(player, level=level)
	if spell == 'sleep': cast_sleep(player, level=level)
	if spell == 'thunderwave': cast_thunderwave(player, level=level)
	#LEVEL 2
	if spell == 'darkness': cast_darkness(player, level=level)
	if spell == 'flaming sphere': cast_flaming_sphere(player, level=level)
	if spell == 'invisibility': cast_invisibility(player, level=level)
	if spell == 'magic weapon': cast_magic_weapon(player, level=level)
	if spell == 'misty step': cast_misty_step(player, level=level)
	if spell == 'shatter': cast_shatter(player, level=level)
	if spell == 'web': cast_web(player, level=level)
	#LEVEL 3
	if spell == 'fireball': cast_fireball(player, target=target, level=level)
	if spell == 'lightning bolt': cast_lightning_bolt(player, target=target, level=level)
	
	### CLERIC
	#CANTRIP
	if spell == 'resistance': cast_resistance(player, level=level)
	if spell == 'sacred flame': cast_sacred_flame(player, target=target, level=level)
	#LEVEL 1
	if spell == 'bless': cast_bless(player, level=level)
	if spell == 'cure wounds': cast_cure_wounds(player, level=level)
	if spell == 'healing word': cast_healing_word(player, level=level)
	if spell == 'inflict wounds': cast_inflict_wounds(player, target=target, level=level)
	if spell == 'shield of faith': cast_shield_of_faith(player, level=level)
	#LEVEL 2
	if spell == 'aid': cast_aid(player, level=level)
	if spell == 'lesser restoration': cast_lesser_restoration(player, level=level)
	if spell == 'prayer of healing': cast_prayer_of_healing(player, level=level)
	if spell == 'silence': cast_silence(player, level=level)
	if spell == 'spiritual weapon': cast_spiritual_weapon(player, level=level)
	if spell == 'warding bond': cast_warding_bond(player, level=level)
	
	### DRUID
	if spell == 'fog cloud': cast_fog_cloud(player, level=level)
	
	### WARLOCK
	if spell == 'eldritch blast': cast_eldritch_blast(player, target=target, level=level)
	if spell == 'hellish rebuke': cast_hellish_rebuke(player, level=level)
	
	last_spell = spell
		
def general_spell_check(caster):
	#this function is used to check for general things which spellcasters need to worry about on each cast - one example is dispelling invisibility whenever a spell is cast
	if caster.fighter:
		for condition in caster.fighter.conditions:
			if condition.name == 'invisibility':
				condition.remove_from_actor(caster)
				if player.can_see_object(caster):
					message(caster.name_for_printing() + ' becomes visible by casting a spell.', 'white')
		
### CROSSOVER SPELLS
		
def cast_light(caster, level=None):
	general_spell_check(caster)
	test = False
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	for condition in caster.fighter.conditions:
		if condition.name == 'illumination': test = True
	if test:
		if player_can_see: message(caster.name_for_printing() + ' casts light but it has no effect.', 'white')
	else:
		obj = Condition(name='illumination', duration=100, colour='yellow')
		caster.fighter.conditions.append(obj)
		obj.owner = caster
		if player_can_see: message(caster.name_for_printing() + ' casts light and the nearby area is illuminated.', 'white')
		#explosion_effect(caster.x, caster.y, 2, [255,255,153])

def cast_find_familiar(caster, level=None):
	global familiar

	general_spell_check(caster)
	test = False
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	possible_familiars = ['bat', 'cat', 'crab', 'frog', 'hawk', 'lizard', 'owl', 'poisonous snake', 'rat', 'raven', 'spider', 'weasel']
	choice = menu('Choose a familiar to summon:', possible_familiars, 40)
	text = possible_familiars[choice]
	text = text.replace(' ', '_')
	func_name = 'create_' + text
	(x, y) = random_unblocked_spot_near(caster.x, caster.y)
	monster = eval(func_name)(x, y)
	caster.familiar = monster
	familiar = caster.familiar
	monster.fighter.faction = caster.fighter.faction
	monster.ai = CompanionMonster(caster, 5)
	monster.ai.owner = monster
	monster.ai.can_talk = False
	monster.ai.can_revive = False
	cond = Condition(name='summoned', visible=False, colour='white')
	cond.apply_to_actor(monster)
	caster.followers.append(monster)
	actors.append(monster)
	if player_can_see: message(caster.name_for_printing() + ' casts find familiar and a creature appears.', 'white')
		
def cast_hold_person(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	targets = []
	if level == None or level <= 2: #this will be the default power level
		number_of_targets = 1
	else:
		number_of_targets = level - 1 #this should give us an extra target for every spell slot above level 2
	if caster == player and target == None:
		for i in range(number_of_targets):
			message('Select target ' + str(i+1) + ' of ' + str(number_of_targets) + ' for the spell.', 'white')
			target = target_monster()
			if target is not None: 
				targets.append(target)
	for target in targets:
		if target.char in ['@', 'k', 'o', 'g', 'h', 'C', 'G']: #dirty way of finding humanoids
			if target.fighter is not None:
				test_result = None
				for condition in target.fighter.conditions:
					if condition.name == 'hold person': test_result = condition
				if test_result is not None:
					if player_can_see: message(caster.name_for_printing() + ' casts hold person but ' + target.name_for_printing() + ' is already held.', 'white')
				else:
					difficulty = caster.fighter.spell_dc()
					result = target.fighter.saving_throw('wisdom', difficulty)
					if result == False: #failed saving throw
						newAI = HeldMonster(target.ai, difficulty=caster.fighter.spell_dc())
						newAI.owner = target
						target.ai = newAI
						if player_can_see: message(caster.name_for_printing() + ' casts hold person successfully on ' + target.name_for_printing() + '.', 'white')
					else:
						if player_can_see: message(caster.name_for_printing() + ' casts hold person but ' + target.name_for_printing() + ' resists the effect.', 'white')
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts hold person but it does not work on ' + target.name_for_printing() + '.', 'white')
		
### WIZARD SPELLS
		
def cast_acid_splash(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	x = None
	y = None
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(target_radius=1, projectile=True)
	if target is not None:
		x = target.x
		y = target.y
		targets = [] #area of effect spell so let's find anyone in range
		targets.append(target)
		for actor in actors: 
			if actor != target:
				if target.distance_to(actor) < 2:
					targets.append(actor)
		difficulty = caster.fighter.spell_dc()
		for target in targets:
			result = target.fighter.saving_throw('dexterity', difficulty)
			if result == False: #failed saving throw
				clvl = caster.fighter.clevel
				if clvl >= 17: num_rolls = 4
				elif clvl >= 11: num_rolls = 3
				elif clvl >= 5: num_rolls = 2
				else: num_rolls = 1
				damage = dice_roll(num_rolls, 6)
				if player_can_see: message(caster.name_for_printing() + ' casts acid splash on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'acid')
			else:
				if player_can_see: message(caster.name_for_printing() + ' casts acid splash on ' + target.name_for_printing() + ' to no effect.', 'white')
		if x is not None: explosion_effect(x, y, 1, [0,255,0])

def cast_fire_bolt(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(projectile=True)
	if target is not None:
		difficulty = caster.fighter.spell_attack()
		result = target.fighter.saving_throw('dexterity', difficulty)
		if result == False and 'fire immune' not in target.fighter.traits: #failed saving throw
			clvl = caster.fighter.clevel
			if clvl >= 17: num_rolls = 4
			elif clvl >= 11: num_rolls = 3
			elif clvl >= 5: num_rolls = 2
			else: num_rolls = 1
			damage = dice_roll(num_rolls, 10)
			if player_can_see: message(caster.name_for_printing() + ' casts fire bolt on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
			target.fighter.take_damage(damage, caster, 'fire')
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts fire bolt on ' + target.name_for_printing() + ' to no effect.', 'white')
		bolt_effect(caster.x, caster.y, target.x, target.y, [204,0,0])

def cast_poison_spray(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(projectile=True)
	if target is not None:
		difficulty = caster.fighter.spell_dc()
		result = target.fighter.saving_throw('constitution', difficulty)
		if result == False and 'poison immune' not in target.fighter.traits: #failed saving throw
			clvl = caster.fighter.clevel
			if clvl >= 17: num_rolls = 4
			elif clvl >= 11: num_rolls = 3
			elif clvl >= 5: num_rolls = 2
			else: num_rolls = 1
			damage = dice_roll(num_rolls, 12)
			if player_can_see: message(caster.name_for_printing() + ' casts poison spray on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
			target.fighter.take_damage(damage, caster, 'poison')
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts poison spray on ' + target.name_for_printing() + ' to no effect.', 'white')
		bolt_effect(caster.x, caster.y, target.x, target.y, [127,0,255])

def cast_ray_of_frost(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(projectile=True)
	if target is not None:
		result = caster.fighter.ranged_spell_attack(target)
		if result == True and 'cold immune' not in target.fighter.traits: #successful ranged attack
			clvl = caster.fighter.clevel
			if clvl >= 17: num_rolls = 4
			elif clvl >= 11: num_rolls = 3
			elif clvl >= 5: num_rolls = 2
			else: num_rolls = 1
			damage = dice_roll(num_rolls, 8)
			if player_can_see: message(caster.name_for_printing() + ' casts ray of frost on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
			target.fighter.take_damage(damage, caster, 'cold')
			###
			### need to add in slow effect
			###
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts ray of frost on ' + target.name_for_printing() + ' to no effect.', 'white')
		ray_effect(caster.x, caster.y, target.x, target.y, [0,255,255])

def cast_shocking_grasp(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if target is not None:
		if caster.distance_to(target) >= 2: 
			target = None #predefined target is too far away
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(max_range=1)
	if target is not None:
		result = caster.fighter.melee_spell_attack(target)
		if result == True and 'electric immune' not in target.fighter.traits: #successful melee attack
			clvl = caster.fighter.clevel
			if clvl >= 17: num_rolls = 4
			elif clvl >= 11: num_rolls = 3
			elif clvl >= 5: num_rolls = 2
			else: num_rolls = 1
			damage = dice_roll(num_rolls, 8)
			if player_can_see: message(caster.name_for_printing() + ' casts shocking grasp on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
			target.fighter.take_damage(damage, caster, 'lightning')
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts shocking grasp on ' + target.name_for_printing() + ' to no effect.', 'white')
			
def cast_chill_touch(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(projectile=True)
	if target is not None:
		result = caster.fighter.ranged_spell_attack(target)
		if result == True and 'necrotic immune' not in target.fighter.traits: #successful ranged attack
			clvl = caster.fighter.clevel
			if clvl >= 17: num_rolls = 4
			elif clvl >= 11: num_rolls = 3
			elif clvl >= 5: num_rolls = 2
			else: num_rolls = 1
			damage = dice_roll(num_rolls, 8)
			if player_can_see: message(caster.name_for_printing() + ' casts chill touch on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
			target.fighter.take_damage(damage, caster, 'necrotic')
			###
			### disadvantage effect for undead targets
			###
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts chill touch on ' + target.name_for_printing() + ' to no effect.', 'white')
		ray_effect(caster.x, caster.y, target.x, target.y, [128,128,128])
		
def cast_burning_hands(caster, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 1:
		number_of_d6 = 3 #default spell power of 3d6
	else:
		number_of_d6 = level + 2 #this will give the user an extra d6 for every level higher than first
	if caster == player:
		blt.clear()
		message('Select a direction for the spell.')
		render_all()
		blt.refresh()
		direction = target_direction()
	if direction is not None:
		target_squares = find_cone_area_of_effect(direction, 3, player.x, player.y)
		targets = []
		for square in target_squares:
			for actor in actors:
				if actor.x == square[0] and actor.y == square[1]:
					if actor.fighter is not None:
						if 'fire immune' not in actor.fighter.traits:
							difficulty = caster.fighter.spell_dc()
							result = actor.fighter.saving_throw('dexterity', difficulty)
							damage = dice_roll(number_of_d6, 6) #3d6 damage
							if result: 
								damage = damage // 2 #half damage if saving throw made
								if player_can_see: message(caster.name_for_printing() + ' casts burning hands ineffectively on ' + actor.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
							else:
								if player_can_see: message(caster.name_for_printing() + ' casts burning hands on ' + actor.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
							actor.fighter.take_damage(damage, caster, 'fire')
	area_effect(target_squares, [255, 0, 0], [255, 128, 0])
		
def cast_magic_missile(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 1:
		number_of_missiles = 3
	else:
		number_of_missiles = level + 2 #this will give the caster an extra magic missile for every spell slot above first level
	targets = []
	if caster == player and target == None:
		for i in range(number_of_missiles):
			message('Select target ' + str(i+1) + ' of ' + str(number_of_missiles) + ' for the spell.', 'white')
			target = target_monster(projectile=True)
			if target is not None: 
				targets.append(target)
	if len(targets) == 0 and target is not None:
		for i in range(number_of_missiles):
			targets.append(target) #aim all three at the one target for simplicity's sake
	if len(targets) > 0:
		for target in targets:
			if target.fighter is not None:
				#first test if target has the shield spell
				shield = False
				for condition in target.fighter.conditions:
					if condition.name == 'shield': 
						shield = True
						condition.permanent = False
						condition.duration = 1 #make the condition expire the next turn - we need to do it this way in case multiple missiles are aimed at the same target - they should all be blocked in the one turn
				if shield == False:
					#work out damage
					damage = dice_roll(1, 4) + 1 #1d4 + 1
					if player_can_see: message(caster.name_for_printing() + ' casts magic missile on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
					target.fighter.take_damage(damage, caster, 'force')
			projectile_effect(caster.x, caster.y, target.x, target.y, [255,0,255])

def cast_mage_armour(caster, level=None):
#just make it affect the caster so we don't have to worry about dealing with NPC's and monsters who aren't wearing armour but their stats mean that they probably actually are, ie. everyone
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	test_result = None
	for condition in caster.fighter.conditions:
		if condition.name == 'mage armour': test_result = condition
	if test_result is not None:
		if player_can_see: message(caster.name_for_printing() + ' casts mage armour and extends the duration of the spell.', 'white')
		condition.duration = 100
	else:
		equipped_armour = None
		for item in caster.inventory:
			if item.equipment:
				if item.equipment.is_equipped:
					if item.equipment.is_equipped == 'body':
						equipped_armour = item
		if equipped_armour is not None:
			if player_can_see: message(caster.name_for_printing() + ' casts mage armour but it has no effect.', 'white')
		else:
			obj = Condition(name='mage armour', duration=100, colour='sky', ac_bonus=3)
			caster.fighter.conditions.append(obj)
			obj.owner = caster
			if player_can_see: message(caster.name_for_printing() + ' casts mage armour and is enveloped by a blue glow.', 'white')
			
def cast_charm_person(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	targets = []
	if level == None or level <= 1: #this will be the default power level
		number_of_targets = 1
	else:
		number_of_targets = level #this should give us an extra target for every spell slot above level 1
	if caster == player and target == None:
		for i in range(number_of_targets):
			message('Select target ' + str(i+1) + ' of ' + str(number_of_targets) + ' for the spell.', 'white')
			target = target_monster()
			if target is not None: 
				targets.append(target)
	for target in targets:
		if target.char in ['@', 'k', 'o', 'g', 'h', 'C', 'G']: #dirty way of finding humanoids
			if target.fighter is not None:
				test_result = None
				for condition in target.fighter.conditions:
					if condition.name == 'charm person': test_result = condition
				if test_result is not None:
					if player_can_see: message(caster.name_for_printing() + ' casts charm person but ' + target.name_for_printing() + ' is already charmed.', 'white')
				else:
					difficulty = caster.fighter.spell_dc()
					result = target.fighter.saving_throw('wisdom', difficulty)
					if result == False: #failed saving throw
						target.fighter.faction = caster.fighter.faction
						obj = Condition(name='charm person', duration=100, colour='fuchsia')
						target.fighter.conditions.append(obj)
						obj.owner = target
						if player_can_see: message(caster.name_for_printing() + ' casts charm person successfully on ' + target.name_for_printing() + '.', 'white')
					else:
						if player_can_see: message(caster.name_for_printing() + ' casts charm person but ' + target.name_for_printing() + ' resists the effect.', 'white')
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts charm person but it does not work on ' + target.name_for_printing() + '.', 'white')
			
def cast_shield(caster, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	test_result = None
	for condition in caster.fighter.conditions:
		if condition.name == 'shield': test_result = condition
	if test_result is not None:
		if player_can_see: message(caster.name_for_printing() + ' casts shield but it has no effect.', 'white')
	else:
		obj = Condition(name='shield', colour='sky', permanent=True)
		caster.fighter.conditions.append(obj)
		obj.owner = caster
		if player_can_see: message(caster.name_for_printing() + ' casts shield and is enveloped by a blue glow.', 'white')
		
def cast_sleep(caster, level=None):
	#find all creatures within 9 tiles of caster (including allies and caster), ignore undead and unconscious and other immune, order from lowest current HP to highest, roll 5d8 and this is total HP that spell affects, work way up list putting creatures to sleep and subtracting the current HP of each one until done
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 1: #this will be the default power level
		number_of_d8 = 5
	else:
		number_of_d8 = 5 + (level - 1) * 2 #this should give us an extra 2d8 for every spell slot above level 1
	list_of_targets = []
	spell_power = dice_roll(number_of_d8, 8)
	for actor in actors:
		if caster.distance_to(actor) <= 9:
			if actor.fighter is not None:
				if 'undead' not in actor.fighter.traits and 'sleep immune' not in actor.fighter.traits:
					test = False
					for condition in actor.fighter.conditions:
						if condition.name == 'unconscious': test = True
						if condition.name == 'sleep': test = True
					if test == False:
						list_of_targets.append(actor)
	#sort list of targets by ascending current HP
	list_of_targets.sort(key=lambda x: x.fighter.hp)
	#apply effects of spell to targets
	if player_can_see: message(caster.name_for_printing() + ' casts sleep and a sense of calm extends throughout the area.', 'white')
	for target in list_of_targets:
		if target.fighter.hp < spell_power:
			spell_power -= target.fighter.hp
			if player.can_see_object(target): message(target.name_for_printing() + ' falls alseep.', 'white')
			obj = Condition(name='sleep', duration=20, colour='sky')
			target.fighter.conditions.append(obj)
			obj.owner = target
			if player.can_see_object(target): explosion_effect(target.x, target.y, 1, [0,0,255])
		else: break

def cast_thunderwave(caster, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 1: #this will be the default power level
		number_of_d8 = 2
	else:
		number_of_d8 = level + 1 #this should give us an extra d8 of damage for every spell slot above level 1
	targets = []
	for actor in actors:
		if actor != caster:
			if caster.distance_to(actor) <= 3:
				targets.append(actor)
	for item in items:
		if caster.distance_to(item) <= 3:
			targets.append(item)
	for target in targets:
		if target.fighter:
			difficulty = caster.fighter.spell_dc()
			result = target.fighter.saving_throw('constitution', difficulty)
			if result == False: #failed saving throw
				damage = dice_roll(number_of_d8, 8)
				if player_can_see: message(caster.name_for_printing() + ' casts thunderwave on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'thunder')
				knock_back(target, caster, 2) 
			else:
				damage = dice_roll(number_of_d8, 8) // 2 #2d8 and then halved
				if player_can_see: message(caster.name_for_printing() + ' casts thunderwave ineffectively on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'thunder')
		else:
			knock_back(target, caster, 2) #items and other inanimate objects get knocked back as well

def cast_darkness(caster, x=None, y=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if x is None and caster == player:
		message('Select a target for the spell.')
		(x, y) = target_tile()
	if x is not None:
		for a in range(x-4, x+4):
			for b in range(y-4, y+4):
				if 0 < a < MAP_WIDTH and 0 < b < MAP_HEIGHT:
					if distance_between(x, y, a, b) <= 3:
						if not map[a][b].block_sight or map[a][b].openable:
							#for any square on the map, within 3 squares of the target tile and which doesn't block sight (or is openable, ie a closed door), create a new effect with the dark tag so that we know that light is incompatible with this
							darkness = Effect(duration=100, visible=False)
							darkness.dark = True
							obj = Object(a, b, ' ', 'darkness', 'black', effect=darkness)
							darkness.owner = obj
							effects.append(obj)
		if player_can_see: message(caster.name_for_printing() + ' casts darkness and light is drained from the area.', 'white')
	
def cast_flaming_sphere(caster, x=None, y=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 2: #this will be the default power level
		number_of_d6 = 2
	else:
		number_of_d6 = level #this should give us an extra d6 of damage for every spell slot above level 2
	if x is None and caster == player:
		while True:
			message('Select a target for the spell.')
			(x, y) = target_tile()
			if x is not None:
				if is_blocked(x, y): message('You need to target an empty space.')
				else: break
	if x is not None:
		effect = Effect(duration=20, illumination=True)
		effect.special = caster.fighter.spell_dc()
		effect.num_dmg_die = number_of_d6
		effect.dmg_die = 6
		effect.creator = caster
		spell = Object(x, y, '*', 'flaming sphere', 'flame')
		spell.big_char = int("0xE015", 16)
		spell.small_char = int("0xE515", 16)
		spell.effect = effect
		effect.owner = spell
		effects.append(spell)
		if player_can_see: message(caster.name_for_printing() + ' casts a spell and a flaming sphere appears.', 'white')
		
def cast_invisibility(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(max_range=1, can_target_self=True, target_hostile_first=False)
		if target is not None:
			obj = Condition(name='invisibility', colour='han', duration=100)
			target.fighter.conditions.append(obj)
			obj.owner = target
			if player_can_see: message(caster.name_for_printing() + ' casts invisibility and ' + target.name_for_printing() + ' fades from sight.', 'white')
			
def cast_magic_weapon(caster, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None:
		bonus = 1
	else:
		if level >= 6:
			bonus = 3
		elif level >= 4:
			bonus = 2
		else: 
			bonus = 1
	blt.clear()
	render_all()
	blt.refresh()
	target = inventory_menu('Choose a weapon to enchant.')
	test_result = None
	if target is not None:
		if target.owner.equipment is not None:
			for condition in target.conditions:
				if condition.name == 'magic weapon': test_result = condition #can't cast this twice on same object
			if 'martial weapon' in target.owner.equipment.properties or 'simple weapon' in target.owner.equipment.properties and test_result == None:
				obj = Condition(name='magic weapon', colour='han', duration=100, to_hit_bonus=bonus, damage_bonus=bonus)
				obj.apply_to_item(target.owner)
				if player_can_see: message(caster.name_for_printing() + ' casts magic weapon on ' + target.owner.name + ' and it is imbued with an enchantment.', 'white')
				return
	if player_can_see: message(caster.name_for_printing() + ' casts magic weapon but it has no effect.', 'white')
	
def cast_misty_step(caster, x=None, y=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if x is None and caster == player:
		while True:
			message('Select a target for the spell.')
			(x, y) = target_tile(max_range=6)
			if not is_blocked(x, y): break
	if x is not None:
		caster.x = x
		caster.y = y
		update_lookup_map()
		if player_can_see: message('Mists appear around ' + caster.name_for_printing() + ' and they reappear nearby.', 'white')

def cast_shatter(caster, x=None, y=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 2: #this will be the default power level
		number_of_d8 = 3
	else:
		number_of_d8 = level+1 #this should give us an extra d8 of damage for every spell slot above level 2
	if x is None and caster == player:
		message('Select a target for the spell.', 'white')
		(x, y) = target_tile(target_radius=2)
	if x is not None:
		targets = [] #area of effect spell so let's find anyone in range
		for actor in actors: 
			if actor.distance(x, y) < 3:
				targets.append(actor)
		difficulty = caster.fighter.spell_dc()
		for target in targets:
			result = target.fighter.saving_throw('constitution', difficulty)
			if result == False: #failed saving throw
				damage = dice_roll(number_of_d8, 8)
				if player_can_see: message(caster.name_for_printing() + ' casts shatter on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'thunder')
			else:
				damage = dice_roll(number_of_d8, 8) // 2
				if player_can_see: message(caster.name_for_printing() + ' casts shatter ineffectively on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'thunder')
		explosion_effect(x, y, 2, [160,160,160])
	
def cast_web(caster, x=None, y=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if x is None and caster == player:
		message('Select a target for the spell.', 'white')
		(x, y) = target_tile(target_radius=2)
	difficulty = caster.fighter.spell_dc()
	if x is not None:
		for a in range(x-3, x+3):
			for b in range(y-3, y+3):
				if 0 < a < MAP_WIDTH and 0 < b < MAP_HEIGHT:
					if distance_between(x, y, a, b) <= 2:
						if not map[a][b].blocked:
							#for any square on the map, within 2 squares of the target tile and which doesn't block sight (or is openable, ie a closed door), create a new effect
							web = Effect(duration=100, visible=True)
							web.special = difficulty
							obj = Object(a, b, '#', 'web', 'grey', effect=web)
							obj.big_char = int("0xE011", 16)
							obj.small_char = int("0xE511", 16)
							web.owner = obj
							effects.append(obj)

def cast_fireball(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 3: #this will be the default power level
		number_of_d6 = 8
	else:
		number_of_d6 = level+5 #this should give us an extra d6 of damage for every spell slot above level 3
	x = None
	y = None
	if target is not None:
		x = target.x
		y = target.y
	if x is None and caster == player:
		message('Select a target for the spell.', 'white')
		(x, y) = target_tile(target_radius=3, projectile=True)
	if x is not None:
		targets = [] #area of effect spell so let's find anyone in range
		for actor in actors: 
			if actor.distance(x, y) < 4:
				targets.append(actor)
		difficulty = caster.fighter.spell_dc()
		for target in targets:
			result = target.fighter.saving_throw('dexterity', difficulty)
			if result == False: #failed saving throw
				damage = dice_roll(number_of_d6, 6)
				if player_can_see: message(caster.name_for_printing() + ' casts fireball on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'fire')
			else:
				damage = dice_roll(number_of_d6, 6) // 2
				if player_can_see: message(caster.name_for_printing() + ' casts fireball ineffectively on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'fire')
		if x is not None: explosion_effect(x, y, 3, [255,128,0])
		
def cast_lightning_bolt(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 3: #this will be the default power level
		number_of_d6 = 8
	else:
		number_of_d6 = level+5 #this should give us an extra d6 of damage for every spell slot above level 3
	x = None
	y = None
	if target is not None:
		x = target.x
		y = target.y
	if x is None and caster == player:
		message('Select a target for the spell.', 'white')
		(x, y) = target_tile(projectile=True)
	if x is not None:
		targets = [] #area of effect spell so let's find anyone in range
		tcod.line_init(caster.x, caster.y, x, y)
		while True:
			(a, b) = tcod.line_step()
			if a is None: break
			if map[a][b].blocked: 
				break
			for actor in actors:
				if actor.fighter:
					if actor.x == a and actor.y == b:
						targets.append(actor)
		difficulty = caster.fighter.spell_dc()
		for target in targets:
			result = target.fighter.saving_throw('dexterity', difficulty)
			if result == False: #failed saving throw
				damage = dice_roll(number_of_d6, 6)
				if player_can_see: message(caster.name_for_printing() + ' casts lightning bolt on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'lightning')
			else:
				damage = dice_roll(number_of_d6, 6) // 2
				if player_can_see: message(caster.name_for_printing() + ' casts lightning bolt ineffectively on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
				target.fighter.take_damage(damage, caster, 'lightning')
		if x is not None: 
			bolt_effect(caster.x, caster.y, x, y, [0,255,255])
							
### CLERIC SPELLS
			
def cast_sacred_flame(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if target is None and caster == player:
		message('Select a target for the spell.')
		target = target_monster()
	if target is not None:
		difficulty = caster.fighter.spell_dc()
		result = target.fighter.saving_throw('dexterity', difficulty)
		if result == False: #failed saving throw
			clvl = caster.fighter.clevel
			if clvl >= 17: num_rolls = 4
			elif clvl >= 11: num_rolls = 3
			elif clvl >= 5: num_rolls = 2
			else: num_rolls = 1
			damage = dice_roll(num_rolls, 8)
			if player_can_see: message(caster.name_for_printing() + ' casts sacred flame on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
			target.fighter.take_damage(damage, caster, 'radiant')
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts sacred flame on ' + target.name_for_printing() + ' to no effect.', 'white')
		bolt_effect(caster.x, caster.y, target.x, target.y, [255,0,0])
				
def cast_resistance(caster, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	test = False
	for condition in caster.fighter.conditions:
		if condition.name == 'resistance': test = True
	if test:
		if player_can_see: message(caster.name_for_printing() + ' casts resistance but it has no effect.', 'white')
	else:
		obj = Condition(name='resistance', permanent=True, saving_throw_bonus=4, variable_bonus=True, colour='yellow')
		caster.fighter.conditions.append(obj)
		obj.owner = caster
		if player_can_see: message(caster.name_for_printing() + ' casts resistance and is covered by a golden glow.', 'white')
			
def cast_bless(caster, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 1: #this will be the default power level
		number_of_targets = 3
	else:
		number_of_targets = level+2 #this should give us an extra target for every spell slot above level 1
	targets = []
	if caster == player:
		for i in range(number_of_targets):
			message('Select up to ' + str((number_of_targets-i)) + ' more targets for the spell.', 'white')
			target = target_monster(can_target_self=True, target_hostile_first=False)
			if target is not None: targets.append(target)
	for target in targets:
		test = None
		for condition in target.fighter.conditions:
			if condition.name == 'bless': test = condition
		if test:
			if player_can_see: message(caster.name_for_printing() + ' casts bless and extends the duration of the spell on ' + target.name_for_printing() + '.', 'white')
			test.duration = 20
		else:
			obj = Condition(name='bless', duration=20, to_hit_bonus=4, saving_throw_bonus=4, variable_bonus=True, colour='yellow')
			target.fighter.conditions.append(obj)
			obj.owner = target
			if player_can_see: message(caster.name_for_printing() + ' casts bless and ' + target.name_for_printing() + ' is covered by a golden glow.', 'white')
		explosion_effect(target.x, target.y, 1, [255,255,0])
			
def cast_cure_wounds(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster) #tcod.map_is_in_fov(fov_map, caster.x, caster.y) and light_map[caster.x][caster.y] > 
	if level == None or level <= 1: #this will be the default power level
		number_of_d8 = 1
	else:
		number_of_d8 = level #this should give us an extra d8 of healing power for every spell slot above level 1
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(max_range=1, can_target_self=True, target_hostile_first=False)
	if target is not None:
		if 'undead' not in target.fighter.traits and 'construct' not in target.fighter.traits:
			healing = dice_roll(number_of_d8, 8) + ABILITY_MODIFIER[caster.fighter.wisdom]
			max_heal = target.fighter.max_hp - target.fighter.hp
			if healing > max_heal: healing = max_heal
			if healing == 0:
				if player_can_see: message(caster.name_for_printing() + ' casts cure wounds on ' + target.name_for_printing() + ' but it has no effect.', 'white')
			else:
				if player_can_see: message(caster.name_for_printing() + ' casts cure wounds on ' + target.name_for_printing() + ' and heals ' + str(healing) + ' damage.', 'white')
				target.fighter.heal(healing)
			
def cast_healing_word(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 1: #this will be the default power level
		number_of_d4 = 1
	else:
		number_of_d4 = level #this should give us an extra d4 of healing power for every spell slot above level 1
	test = False
	for condition in caster.fighter.conditions:
		if condition.name == 'used healing word':
			test = True
	if test is True:
		message(caster.name_for_printing() + ' can only use healing word once per turn.', 'white')
	else:
		obj = Condition(name='used healing word', duration=1, visible=False) #this object prevents us from using it twice on a single turn
		obj.owner = caster 
		caster.fighter.conditions.append(obj)
		if target is None and caster == player:
			message('Select a target for the spell.', 'white')
			target = target_monster(can_target_self=True, target_hostile_first=False)
		if target is not None:
			if 'undead' not in target.fighter.traits and 'construct' not in target.fighter.traits:
				healing = dice_roll(number_of_d4, 4) + ABILITY_MODIFIER[caster.fighter.wisdom]
				max_heal = target.fighter.max_hp - target.fighter.hp
				if healing > max_heal: healing = max_heal
				if healing == 0:
					if player_can_see: message(caster.name_for_printing() + ' casts healing word on ' + target.name_for_printing() + ' but it has no effect.', 'white')
				else:
					if player_can_see: message(caster.name_for_printing() + ' casts healing word on ' + target.name_for_printing() + ' and heals ' + str(healing) + ' damage.', 'white')
					target.fighter.heal(healing)
				
def cast_inflict_wounds(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 1: #this will be the default power level
		number_of_d10 = 3
	else:
		number_of_d10 = level+2 #this should give us an extra d10 of power for every spell slot above level 1
	if target is not None:
		if caster.distance_to(target) >= 2: 
			target = None #predefined target is too far away
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(max_range=1)
	if target is not None:
		result = caster.fighter.melee_spell_attack(target)
		if result == True and 'necrotic immune' not in target.fighter.traits: #successful melee attack
			damage = dice_roll(number_of_d10, 10)
			if player_can_see: message(caster.name_for_printing() + ' casts inflict wounds on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
			target.fighter.take_damage(damage, caster, 'necrotic')
		else:
			if player_can_see: message(caster.name_for_printing() + ' casts inflict wounds on ' + target.name_for_printing() + ' to no effect.', 'white')
				
def cast_shield_of_faith(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if caster == player and target == None:
		message('Select a target for the spell.', 'white')
		target = target_monster(can_target_self=True, target_hostile_first=False)
	test = False
	for condition in target.fighter.conditions:
		if condition.name == 'shield of faith': test = condition
	if test:
		if player_can_see: message(caster.name_for_printing() + ' casts shield of faith and extends the duration of the spell on ' + target.name_for_printing() + '.', 'white')
		test.duration = 100
	else:
		obj = Condition(name='shield of faith', duration=100, ac_bonus=2, colour='yellow')
		target.fighter.conditions.append(obj)
		obj.owner = target
		if player_can_see: message(caster.name_for_printing() + ' casts shield of faith and ' + target.name_for_printing() + ' is covered by a golden glow.', 'white')

def cast_aid(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 2: #this will be the default power level
		spell_power = 1
	else:
		spell_power = level-1 #this should give us a multiplier for extra HP bonus
	targets = []
	if caster == player:
		for i in range(3):
			message('Select up to ' + str((3-i)) + ' more targets for the spell.', 'white')
			target = target_monster(can_target_self=True, target_hostile_first=False)
			targets.append(target)
	else:
		targets.append(target)
	for target in targets:
		test = None
		for condition in target.fighter.conditions:
			if condition.name == 'aid': test = condition
		if test:
			if player_can_see: message(caster.name_for_printing() + ' casts aid and extends the duration of the spell on ' + target.name_for_printing() + '.', 'white')
			test.duration = 800
		else:
			target.fighter.hp += (5 * spell_power)
			target.fighter.max_hp += (5 * spell_power)
			obj = Condition(name='aid', duration=800, colour='yellow', remove_on_rest=True)
			target.fighter.conditions.append(obj)
			obj.owner = target
			if player_can_see: message(caster.name_for_printing() + ' casts aid and ' + target.name_for_printing() + ' is covered by a golden glow.', 'white')
	
def cast_lesser_restoration(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if target is None and caster == player:
		message('Select a target for the spell.', 'white')
		target = target_monster(max_range=1, can_target_self=True, target_hostile_first=False)
	test = False
	if target is not None:
		if target.fighter:
			for cond in target.fighter.conditions:
				if cond.name == 'poisoned':
					cond.remove_from_actor(target)
					test = True
	if test: 
		if player_can_see: message(caster.name_for_printing() + ' casts lesser restoration on ' + target.name_for_printing() + ' and their health is restored.', 'white')
	else:
		if player_can_see: message(caster.name_for_printing() + ' casts lesser restoration on ' + target.name_for_printing() + ' but it has no effect.', 'white')
	
def cast_prayer_of_healing(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 2: #this will be the default power level
		number_of_d8 = 2
	else:
		number_of_d8 = level #this should give us an extra d8 of healing power for every spell slot above level 2
	targets = []
	if caster == player:
		for i in range(6):
			message('Select up to ' + str((6-i)) + ' more targets for the spell.', 'white')
			target = target_monster(can_target_self=True, target_hostile_first=False)
			if target is not None: 
				if target not in targets:
					targets.append(target)
			else:
				break #give up if the player doesn't select anyone because 6 might be a lot
	else:
		targets.append(target)
	if len(targets) > 0:
		for target in targets:
			if target.fighter is not None:
				if 'undead' not in target.fighter.traits and 'construct' not in target.fighter.traits:
					healing = dice_roll(number_of_d8, 8) + ABILITY_MODIFIER[caster.fighter.wisdom]
					max_heal = target.fighter.max_hp - target.fighter.hp
					if healing > max_heal: healing = max_heal
					if healing == 0:
						if player_can_see: message(caster.name_for_printing() + ' casts prayer of healing on ' + target.name_for_printing() + ' but it has no effect.', 'white')
					else:
						if player_can_see: message(caster.name_for_printing() + ' casts prayer of healing on ' + target.name_for_printing() + ' and heals ' + str(healing) + ' damage.', 'white')
						target.fighter.heal(healing)
	
def cast_silence(caster, level=None):
	pass
	
def cast_spiritual_weapon(caster, x=None, y=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 2: #this will be the default power level
		number_of_d8 = 1
	else:
		if level >= 8:
			number_of_d8 = 4 
		elif level >= 6:
			number_of_d8 = 3
		elif level >= 4:
			number_of_d8 = 2
		else: 
			number_of_d8 = 1
	if x is None and caster == player:
		while True:
			message('Select a target for the spell.')
			(x, y) = target_tile(max_range=6)
			if x is not None:
				if not is_blocked(x, y): break
	if x is not None:
		faction = caster.fighter.faction
		fighter_component = Fighter(hp=100, strength=12, dexterity=15, constitution=11, intelligence=1, wisdom=5, charisma=1, clevel=1, proficiencies=[], traits=['poison immune', 'flying', 'blindsight', 'construct'], spells=[], xp=50, death_function=monster_death, ac=20, num_dmg_die=number_of_d8, dmg_die=8, dmg_bonus=ABILITY_MODIFIER[caster.fighter.wisdom], dmg_type = 'bludgeoning', to_hit=ABILITY_MODIFIER[caster.fighter.wisdom], challenge_rating=1, faction=faction)  
		ai_component = CompanionMonster(caster, 5)
		ai_component.can_talk = False
		ai_component.can_revive = False
		monster = Object(x, y, ')', 'spiritual weapon', 'gold', blocks=True, fighter=fighter_component, ai=ai_component)
		monster.big_char = int("0xE147", 16)
		monster.small_char = int("0xE647", 16)
		cond = Condition(name='summoned', duration=20, visible=False, colour='white')
		cond.apply_to_actor(monster)
		actors.append(monster)
		if player_can_see: message(caster.name_for_printing() + ' casts spiritual weapon and a spectral hammer appears.', 'white')
	
def cast_warding_bond(caster, level=None):
	pass
		
### DRUID SPELLS

def cast_fog_cloud(caster, x=None, y=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if x is None and caster == player:
		message('Select a target for the spell.', 'white')
		(x, y) = target_tile(target_radius=3)
	difficulty = caster.fighter.spell_dc()
	if x is not None:
		for a in range(x-4, x+4):
			for b in range(y-4, y+4):
				if 0 < a < MAP_WIDTH and 0 < b < MAP_HEIGHT:
					if distance_between(x, y, a, b) <= 3:
						if not map[a][b].blocked:
							#for any square on the map, within 3 squares of the target tile and which doesn't block sight (or is openable, ie a closed door), create a new effect
							fog = Effect(duration=100, visible=True, block_sight=True)
							obj = Object(a, b, '#', 'fog', 'grey', effect=fog)
							obj.big_char = int("0xE017", 16)
							obj.small_char = int("0xE517", 16)
							fog.owner = obj
							effects.append(obj)
		
### WARLOCK SPELLS
		
def cast_eldritch_blast(caster, target=None, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	targets = []
	if caster.fighter.clevel < 5: number_of_blasts = 1
	elif caster.fighter.clevel < 11: number_of_blasts = 2
	elif caster.fighter.clevel < 17: number_of_blasts = 3
	else: number_of_blasts = 4
	if caster == player and target == None:
		for i in range(number_of_blasts):
			message('Select target ' + str(i+1) + ' of ' + str(number_of_blasts) + ' for the spell.', 'white')
			target = target_monster(projectile=True)
			if target is not None: 
				targets.append(target)
	if len(targets) == 0 and target is not None:
		for i in range(number_of_blasts):
			targets.append(target) #aim all at the one target for simplicity's sake
	if len(targets) > 0:
		for target in targets:
			if target.fighter is not None:
				result = caster.fighter.ranged_spell_attack(target)
				damage = dice_roll(1, 10)
				if result == True:
					if player_can_see: message(caster.name_for_printing() + ' casts eldritch blast on ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
					target.fighter.take_damage(damage, caster, 'force')
				else:
					if player_can_see: message(caster.name_for_printing() + ' casts eldritch blast on ' + target.name_for_printing() + ' to no effect.', 'white')
			bolt_effect(caster.x, caster.y, target.x, target.y, [255,0,255])

def cast_hellish_rebuke(caster, level=None):
	general_spell_check(caster)
	if caster == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(caster)
	if level == None or level <= 1: #this will be the default power level
		number_of_d10 = 2
	else:
		number_of_d10 = level+1 #this should give us an extra d10 of damage for each spell slot level
	test_result = None
	for condition in caster.fighter.conditions:
		if condition.name == 'hellish rebuke': test_result = condition
	if test_result is not None:
		if player_can_see: message(caster.name_for_printing() + ' casts hellish rebuke but it has no effect.', 'white')
	else:
		obj = Condition(name='hellish rebuke', colour='red', permanent=True, remove_on_rest=True)
		obj.special = number_of_d10 #use this variable to store the spell power
		caster.fighter.conditions.append(obj)
		obj.owner = caster
		if player_can_see: message(caster.name_for_printing() + ' casts hellish rebuke and is enveloped by a red glow.', 'white')
		
def process_hellish_rebuke(target, attacker, power=None):
	if target == player or attacker == player:
		player_can_see = True
	else:
		player_can_see = player.can_see_object(attacker)
	if power == None: power = 2
	difficulty = target.fighter.spell_dc()
	result = attacker.fighter.saving_throw('dexterity', difficulty)
	if result == False: #failed saving throw
		damage = dice_roll(power, 10)
		if player_can_see: message(target.name_for_printing() + ' uses hellish rebuke on ' + attacker.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
		attacker.fighter.take_damage(damage, target, 'fire')
	else:
		damage = dice_roll(power, 10) // 2
		if player_can_see: message(target.name_for_printing() + ' uses hellish rebuke ineffectively on ' + attacker.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
		attacker.fighter.take_damage(damage, target, 'fire')
	bolt_effect(target.x, target.y, attacker.x, attacker.y, [255,0,0])
		
### MAGIC UTILITY FUNCTIONS
		
def find_cone_area_of_effect(direction, range, x, y): #this dumb function only works for range 3 at this stage
	result = []
	if direction == (-1, -1):
		if range == 3:
			result = [(x-1, y-1), (x-2, y-1), (x-3, y-1), (x-4, y-1), (x-1, y-2), (x-2, y-2), (x-3, y-2), (x-1, y-3), (x-2, y-3), (x-1, y-4)]
	if direction == (0, -1):
		if range == 3:
			result = [(x, y-1), (x-1, y-2), (x, y-2), (x+1, y-2), (x-2, y-3), (x-1, y-3), (x, y-3), (x+1, y-3), (x+2, y-3)]
	if direction == (1, -1):
		if range == 3:
			result = [(x+1, y-1), (x+2, y-1), (x+3, y-1), (x+4, y-1), (x+1, y-2), (x+2, y-2), (x+3, y-2), (x+1, y-3), (x+2, y-3), (x+1, y-4)]
	if direction == (1, 0):
		if range == 3:
			result = [(x+1, y), (x+2, y-1), (x+2, y), (x+2, y+1), (x+3, y-2), (x+3, y-1), (x+3, y), (x+3, y+1), (x+3, y+2)]
	if direction == (1, 1):
		if range == 3:
			result = [(x+1, y+1), (x+2, y+1), (x+3, y+1), (x+4, y+1), (x+1, y+2), (x+2, y+2), (x+3, y+2), (x+1, y+3), (x+2, y+3), (x+4, y+1)]
	if direction == (0, 1):
		if range == 3:
			result = [(x, y+1), (x-1, y+2), (x, y+2), (x+1, y+2), (x-2, y+3), (x-1, y+3), (x, y+3), (x+1, y+3), (x+2, y+3)]
	if direction == (-1, 1):
		if range == 3:
			result = [(x-1, y+1), (x-2, y+1), (x-3, y+1), (x-4, y+1), (x-1, y+2), (x-2, y+2), (x-3, y+2), (x-1, y+3), (x-2, y+3), (x-1, y+4)]	
	if direction == (-1, 0):
		if range == 3:
			result = [(x-1, y), (x-2, y-1), (x-2, y), (x-2, y+1), (x-3, y-2), (x-3, y-1), (x-3, y), (x-3, y+1), (x-3, y+2)]
	return result
	
###
### OTHER EFFECTS AND CONDITIONS
###
	
def use_potion_of_healing(user, item):
	if user.fighter:
		heal_amount = dice_roll(number_of_die=2, type_of_die=4) + 2
		max_heal = user.fighter.max_hp - user.fighter.hp
		if heal_amount > max_heal: heal_amount = max_heal
		user.fighter.heal(heal_amount)
		message(user.name_for_printing() + ' uses potion of healing and recovers ' + str(heal_amount) + ' hit points.', 'white')
	else:
		return 'cancelled'
		
def use_vial_of_acid(user, item):
	message('Select a target for the vial of acid.', 'white')
	target = target_monster(projectile=True)
	if target is not None:
		damage = dice_roll(2, 6)
		message(user.name_for_printing() + ' throws a vial of acid at ' + target.name_for_printing() + ' for ' + str(damage) + ' damage.', 'white')
		target.fighter.take_damage(damage, user, 'acid')
	else:
		return 'cancelled'
		
def use_oil_of_sharpness(user, item):
	weapon = None
	for item in user.inventory:
		if item.equipment:
			if item.equipment.is_equipped == 'main hand':
				weapon = item
	if weapon is not None:
		if 'slashing' in weapon.equipment.properties or 'piercing' in weapon.equipment.properties:
			condition = Condition(name='sharpness', duration=100, to_hit_bonus=3, damage_bonus=3)
			condition.owner = weapon
			weapon.item.conditions.append(condition)
			message(user.name_for_printing() + ' applies oil of sharpness to the ' + weapon.name_for_printing() + '.', 'white')
		else:
			message('The oil can not be applied to a weapon like that.')
			return 'cancelled'
	else:
		message('There is no weapon in main hand to apply oil to.')
		return 'cancelled'
	
def use_potion_of_giant_strength(user, item):
	condition = Condition(name='giant strength', duration=100)
	condition.stat_to_override = 'strength'
	condition.special = item.item.special #this will be the strength value to change to
	condition.owner = user
	user.fighter.conditions.append(condition)
	recalc_stats(user)
	message(user.name_for_printing() + ' uses potion of giant strength and grows in power.', 'white')
	
def use_potion_of_heroism(user, item):
	if user.fighter:
		obj = Condition(name='heroism', duration=100, to_hit_bonus=4, saving_throw_bonus=4, variable_bonus=True, colour='yellow')
		user.fighter.conditions.append(obj)
		obj.owner = user
		user.fighter.temp_hp = 10
		message(user.name_for_printing() + ' uses potion of heroism and grows in power.', 'white')
	else:
		return 'cancelled'
		
def use_wand_of_fireball(user, item):
	cast_fireball(user)
	
def use_wand_of_lightning_bolt(user, item):
	cast_lightning_bolt(user)

def use_wand_of_magic_missile(user, item):
	cast_magic_missile(user)
	
def use_wand_of_web(user, item):
	cast_web(user)
	
def use_wand_of_humblesongs_gift(user, item):
	cast_prayer_of_healing(user)
	
###
### MONSTER GENERATION FUNCTIONS
###
	
def create_adult_red_dragon(x, y):
	fighter_component = Fighter(hp=256, strength=27, dexterity=10, constitution=25, intelligence=16, wisdom=13, charisma=21, clevel=1, proficiencies=['resistance'], traits=['blindsight', 'darkvision', 'fire breath', 'extra attack', 'extra attack'], spells=[], xp=18000, death_function=monster_death, ac=19, num_dmg_die=2, dmg_die=10, dmg_bonus=8, dmg_type = 'piercing', to_hit=14, challenge_rating=17)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'adult red dragon', 'red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE104", 16)
	monster.small_char = int("0xE604", 16)
	monster.move_cost = 75
	monster.description = 'The odor of sulfur and pumice surrounds a red dragon, whose swept-back horns and spinal frill define its silhouette. Its beaked snout vents smoke at all times, and its eyes dance with flame when it is angry.'
	return monster
	
def create_air_elemental(x, y):
	fighter_component = Fighter(hp=90, strength=14, dexterity=20, constitution=14, intelligence=6, wisdom=10, charisma=6, clevel=1, proficiencies=[], traits=['poison immune', 'darkvision', 'flying', 'extra attack'], spells=['whirlwind'], xp=1800, death_function=monster_death, ac=15, num_dmg_die=2, dmg_die=8, dmg_bonus=5, dmg_type = 'bludgeoning', to_hit=8, challenge_rating=5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'E', 'air elemental', 'sky', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE105", 16)
	monster.small_char = int("0xE605", 16)
	monster.move_cost = 33
	monster.description = 'An air elemental is a funneling cloud of whirling air with a vague semblance of a face. It can turn itself into a screaming cyclone, creating a whirlwind that batters creatures even as it flings them away.'
	return monster
	
def create_allosaurus(x, y):
	fighter_component = Fighter(hp=51, strength=19, dexterity=13, constitution=17, intelligence=2, wisdom=12, charisma=5, clevel=1, proficiencies=[], traits=[], spells=[], xp=450, death_function=monster_death, ac=13, num_dmg_die=2, dmg_die=10, dmg_bonus=4, dmg_type = 'piercing', to_hit=6, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'allosaurus', 'light blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE106", 16)
	monster.small_char = int("0xE606", 16)
	monster.move_cost = 50
	monster.description = 'The allosaurus is a predatory dinosaur of great size, strength, and speed. It can run down almost any prey over open ground, pouncing to pull creatures down with its wicked claws.'
	return monster
	
def create_animated_armour(x, y):
	fighter_component = Fighter(hp=33, strength=14, dexterity=11, constitution=13, intelligence=1, wisdom=3, charisma=1, clevel=1, proficiencies=[], traits=['poison immune', 'extra attack', 'construct'], spells=[], xp=200, death_function=monster_death, ac=18, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'bludgeoning', to_hit=4, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, ']', 'animated armour', 'lighter grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE107", 16)
	monster.small_char = int("0xE607", 16)
	monster.move_cost = 120
	monster.description = 'This suit of magically animated plate armor clamors as it moves, banging and grinding like the vengeful spirit of a fallen knight.'
	return monster
	
def create_ankylosaurus(x, y):
	fighter_component = Fighter(hp=68, strength=19, dexterity=11, constitution=15, intelligence=2, wisdom=12, charisma=5, clevel=1, proficiencies=[], traits=[], spells=[], xp=700, death_function=monster_death, ac=15, num_dmg_die=4, dmg_die=6, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=7, challenge_rating=3)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'ankylosaurus', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE108", 16)
	monster.small_char = int("0xE608", 16)
	monster.move_cost = 100
	monster.description = 'Thick armor plating covers the body of the plant-eating dinosaur ankylosaurus, which defends itself against predators with a knobbed tail that delivers a devastating strike.'
	return monster
	
def create_ape(x, y): 
	fighter_component = Fighter(hp=19, strength=16, dexterity=14, constitution=14, intelligence=6, wisdom=12, charisma=7, clevel=1, proficiencies=[], traits=['extra attack'], spells=[], xp=100, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=3, dmg_type = 'bludgeoning', to_hit=5, challenge_rating=0.5) 
	ai_component = BasicMonster()
	monster = Object(x, y, 'Y', 'ape', 'lighter grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE109", 16)
	monster.small_char = int("0xE609", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_axe_beak(x, y): 
	fighter_component = Fighter(hp=19, strength=14, dexterity=12, constitution=12, intelligence=2, wisdom=10, charisma=5, clevel=1, proficiencies=[], traits=[], spells=[], xp=50, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=8, dmg_bonus=2, dmg_type = 'slashing', to_hit=4, challenge_rating=0.25) 
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'axe beak', 'light yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE112", 16)
	monster.small_char = int("0xE612", 16)
	monster.move_cost = 60
	monster.description = 'An axe beak is a tall flightless bird with strong legs, a wedge-shaped beak, and a nasty disposition.'
	return monster
	
def create_baboon(x, y): 
	fighter_component = Fighter(hp=3, strength=8, dexterity=14, constitution=11, intelligence=4, wisdom=12, charisma=6, clevel=1, proficiencies=[], traits=['pack tactics'], spells=[], xp=10, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=4, dmg_bonus=-1, dmg_type = 'piercing', to_hit=1, challenge_rating=0) 
	ai_component = BasicMonster()
	monster = Object(x, y, 'Y', 'baboon', 'han', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE113", 16)
	monster.small_char = int("0xE613", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_badger(x, y): 
	fighter_component = Fighter(hp=3, strength=4, dexterity=11, constitution=12, intelligence=2, wisdom=12, charisma=5, clevel=1, proficiencies=['perception'], traits=['darkvision'], spells=[], xp=10, death_function=monster_death, ac=10, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=2, challenge_rating=0) 
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'badger', 'lighter grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE114", 16)
	monster.small_char = int("0xE614", 16)
	monster.move_cost = 150
	#monster.description = ''
	return monster	
	
def create_banshee(x, y): 
	fighter_component = Fighter(hp=58, strength=1, dexterity=14, constitution=10, intelligence=12, wisdom=11, charisma=17, clevel=1, proficiencies=[], traits=['poison immune', 'cold immune', 'necrotic immune', 'flying'], spells=['wail'], xp=1100, death_function=monster_death, ac=12, num_dmg_die=3, dmg_die=6, dmg_bonus=2, dmg_type = 'necrotic', to_hit=4, challenge_rating=4) 
	ai_component = BasicMonster()
	monster = Object(x, y, 'n', 'banshee', 'fuchsia', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE115", 16)
	monster.small_char = int("0xE615", 16)
	monster.move_cost = 75
	monster.description = 'The woeful banshee is a spiteful creature formed from the spirit of a female elf. Its face is wreathed in a wild tangle of hair, its body clad in wispy rags that flutter and stream around it.'
	return monster
	
def create_bat(x, y):
	fighter_component = Fighter(hp=1, strength=2, dexterity=15, constitution=8, intelligence=2, wisdom=12, charisma=4, clevel=1, proficiencies=[], traits=['blindsight', 'flying'], spells=[], xp=10, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=0, challenge_rating=0.125) 
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'bat', 'dark orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE116", 16)
	monster.small_char = int("0xE616", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_basilisk(x, y):
	fighter_component = Fighter(hp=52, strength=16, dexterity=8, constitution=15, intelligence=2, wisdom=8, charisma=7, clevel=1, proficiencies=[], traits=['darkvision', 'poisonous', 'petrifying gaze'], spells=[], xp=700, death_function=monster_death, ac=15, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'S', 'basilisk', 'sea', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, num_dmg_die=2, dmg_die=6, dmg_type='poison')
	#note - no saving throw for basilisk venom
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE117", 16)
	monster.small_char = int("0xE617", 16)
	monster.move_cost = 150
	monster.description = 'A basilisk is a multilegged, reptilian horror whose deadly gaze transforms victims into porous stone. With its strong jaws, the creature consumes this stone, which returns to organic form in its gullet.'
	return monster
	
def create_black_bear(x, y):
	fighter_component = Fighter(hp=19, strength=15, dexterity=10, constitution=14, intelligence=2, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=['extra attack'], spells=[], xp=100, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=3, challenge_rating=0.5)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'h', 'black bear', 'darker grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE118", 16)
	monster.small_char = int("0xE618", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_blink_dog(x, y):
	fighter_component = Fighter(hp=22, strength=12, dexterity=17, constitution=12, intelligence=10, wisdom=13, charisma=11, clevel=1, proficiencies=['perception'], traits=['stealthy'], spells=['teleport'], xp=50, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'blink dog', 'azure', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE119", 16)
	monster.small_char = int("0xE619", 16)
	monster.move_cost = 75
	monster.description = 'A blink dog takes its name from its ability to blink in and out of existence, a talent it uses to aid its attacks and to avoid harm.'
	return monster
	
def create_blood_hawk(x, y):
	fighter_component = Fighter(hp=7, strength=6, dexterity=14, constitution=10, intelligence=3, wisdom=14, charisma=5, clevel=1, proficiencies=['perception'], traits=['pack tactics', 'flying'], spells=[], xp=25, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.125)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'blood hawk', 'red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE120", 16)
	monster.small_char = int("0xE620", 16)
	monster.move_cost = 50
	monster.description = 'Taking its name from its crimson feathers and aggressive nature, the blood hawk fearlessly attacks with its daggerlike beak.'
	return monster
	
def create_boar(x, y):
	fighter_component = Fighter(hp=11, strength=13, dexterity=11, constitution=12, intelligence=2, wisdom=9, charisma=5, clevel=1, proficiencies=[], traits=['relentless', 'charge'], spells=[], xp=50, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'slashing', to_hit=3, challenge_rating=0.25)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'boar', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE121", 16)
	monster.small_char = int("0xE621", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_brown_bear(x, y):
	fighter_component = Fighter(hp=34, strength=19, dexterity=10, constitution=16, intelligence=2, wisdom=13, charisma=7, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=200, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=8, dmg_bonus=4, dmg_type = 'piercing', to_hit=5, challenge_rating=1)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'h', 'black bear', 'brass', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE122", 16)
	monster.small_char = int("0xE622", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_bugbear(x, y):
	fighter_component = Fighter(hp=27, strength=15, dexterity=14, constitution=13, intelligence=8, wisdom=11, charisma=9, clevel=1, proficiencies=[], traits=['brute'], spells=[], xp=200, death_function=monster_death, ac=16, num_dmg_die=2, dmg_die=8, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=1)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'h', 'bugbear', 'amber', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE123", 16)
	monster.small_char = int("0xE623", 16)
	monster.move_cost = 100
	monster.description = 'Bugbears are hairy goblinoids born for battle and mayhem. They survive by raiding and hunting, but are fond of setting ambushes and fleeing when outmatched.'
	return monster
	
def create_cat(x, y):
	fighter_component = Fighter(hp=2, strength=3, dexterity=15, constitution=10, intelligence=3, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=10, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'slashing', to_hit=0, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'f', 'cat', 'lightest grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE125", 16)
	monster.small_char = int("0xE625", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_centaur(x, y):
	fighter_component = Fighter(hp=45, strength=18, dexterity=14, constitution=14, intelligence=9, wisdom=13, charisma=11, clevel=1, proficiencies=[], traits=['charge', 'extra attack'], spells=[], xp=450, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=6, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'C', 'centaur', 'dark red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE126", 16)
	monster.small_char = int("0xE626", 16)
	monster.move_cost = 60
	monster.description = 'A centaur has the body of a great horse topped by a humanoid torso, head, and arms. Reclusive wanderers, they avoid conflict but fight fiercely when pressed.'
	return monster	
	
def create_chimera(x, y):
	fighter_component = Fighter(hp=114, strength=19, dexterity=11, constitution=19, intelligence=3, wisdom=14, charisma=10, clevel=1, proficiencies=[], traits=['darkvision', 'fire breath', 'extra attack', 'extra attack'], spells=[], xp=2300, death_function=monster_death, ac=14, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'piercing', to_hit=7, challenge_rating=6)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'U', 'chimera', 'violet', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE127", 16)
	monster.small_char = int("0xE627", 16)
	monster.move_cost = 50
	monster.description = 'A chimera is a vile combination of goat, lion, and dragon, and features the heads of all three of those creatures. It likes to swoop down from the sky and engulf prey with its fiery breath before landing to attack.'
	return monster
	
def create_cockatrice(x, y):
	fighter_component = Fighter(hp=27, strength=6, dexterity=12, constitution=12, intelligence=2, wisdom=13, charisma=5, clevel=1, proficiencies=[], traits=['darkvision', 'petrify'], spells=[], xp=100, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=4, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.5)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'c', 'cockatrice', 'flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE128", 16)
	monster.small_char = int("0xE628", 16)
	monster.move_cost = 75
	monster.description = 'The cockatrice looks like a hideous hybrid of lizard, bird, and bat. It is infamous for its ability to turn flesh to stone.'
	return monster
	
def create_constrictor_snake(x, y):
	fighter_component = Fighter(hp=13, strength=15, dexterity=14, constitution=12, intelligence=1, wisdom=10, charisma=3, clevel=1, proficiencies=[], traits=['blindsight', 'constrict'], spells=[], xp=50, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'S', 'constrictor snake', 'light green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE129", 16)
	monster.small_char = int("0xE629", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_crab(x, y):
	fighter_component = Fighter(hp=2, strength=2, dexterity=11, constitution=10, intelligence=1, wisdom=8, charisma=2, clevel=1, proficiencies=[], traits=['blindsight', 'amphibious'], spells=[], xp=10, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'bludgeoning', to_hit=0, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'a', 'crab', 'light flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE130", 16)
	monster.small_char = int("0xE630", 16)
	monster.move_cost = 150
	#monster.description = ''
	return monster
	
def create_crocodile(x, y):
	fighter_component = Fighter(hp=19, strength=15, dexterity=10, constitution=13, intelligence=2, wisdom=10, charisma=5, clevel=1, proficiencies=[], traits=['amphibious'], spells=[], xp=100, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=10, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.5)	 
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'crocodile', 'dark green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE131", 16)
	monster.small_char = int("0xE631", 16)
	monster.move_cost = 150
	#monster.description = ''
	return monster
	
def create_cyclops(x, y):
	fighter_component = Fighter(hp=138, strength=22, dexterity=11, constitution=20, intelligence=8, wisdom=6, charisma=10, clevel=1, proficiencies=[], traits=['rock', 'extra attack'], spells=[], xp=2300, death_function=monster_death, ac=14, num_dmg_die=3, dmg_die=8, dmg_bonus=6, dmg_type = 'bludgeoning', to_hit=9, challenge_rating=6)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'cyclops', 'dark azure', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE132", 16)
	monster.small_char = int("0xE632", 16)
	monster.move_cost = 100
	monster.description = 'Cyclopes are one-eyed giants that eke out a meager existence in wild lands. They are a terrifying threat in combat due to their size and strength, but they can often be tricked by clever foes.'
	return monster
	
def create_death_dog(x, y):
	fighter_component = Fighter(hp=39, strength=15, dexterity=14, constitution=14, intelligence=3, wisdom=13, charisma=6, clevel=1, proficiencies=[], traits=['darkvision', 'extra attack'], spells=[], xp=200, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=1)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'death dog', 'darker red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE133", 16)
	monster.small_char = int("0xE633", 16)
	monster.move_cost = 75
	monster.description = 'A death dog is an ugly two-headed hound that roams plains, deserts, and the Underdark.'
	return monster
	
def create_deer(x, y):
	fighter_component = Fighter(hp=4, strength=11, dexterity=16, constitution=11, intelligence=2, wisdom=14, charisma=5, clevel=1, proficiencies=[], traits=[], spells=[], xp=10, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=4, dmg_bonus=0, dmg_type = 'piercing', to_hit=2, challenge_rating=0)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'deer', 'light flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE134", 16)
	monster.small_char = int("0xE634", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_dire_wolf(x, y):
	fighter_component = Fighter(hp=37, strength=17, dexterity=15, constitution=15, intelligence=3, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=['pack tactics'], spells=[], xp=200, death_function=monster_death, ac=14, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'dire wolf', 'dark red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE135", 16)
	monster.small_char = int("0xE635", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_doppelganger(x, y):
	fighter_component = Fighter(hp=52, strength=11, dexterity=18, constitution=14, intelligence=11, wisdom=12, charisma=14, clevel=1, proficiencies=[], traits=['darkvision', 'shapechanger', 'extra attack'], spells=[], xp=700, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=6, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=6, challenge_rating=3)  
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'doppelganger', 'pink', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE136", 16)
	monster.small_char = int("0xE636", 16)
	monster.move_cost = 100
	monster.description = 'Doppelgangers are devious shapeshifters that take on the appearance of other humanoids, throwing off pursuit or luring victims to their doom with misdirection and disguise.'
	return monster
	
def create_draft_horse(x, y):
	fighter_component = Fighter(hp=19, strength=18, dexterity=10, constitution=12, intelligence=2, wisdom=11, charisma=7, clevel=1, proficiencies=[], traits=[], spells=[], xp=50, death_function=monster_death, ac=14, num_dmg_die=2, dmg_die=4, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=6, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'draft horse', 'brass', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE137", 16)
	monster.small_char = int("0xE637", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_eagle(x, y):
	fighter_component = Fighter(hp=3, strength=6, dexterity=15, constitution=10, intelligence=2, wisdom=14, charisma=7, clevel=1, proficiencies=['perception'], traits=['flying'], spells=[], xp=10, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'slashing', to_hit=4, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'eagle', 'azure', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE138", 16)
	monster.small_char = int("0xE638", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster
	
def create_earth_elemental(x, y):
	fighter_component = Fighter(hp=126, strength=20, dexterity=8, constitution=20, intelligence=5, wisdom=10, charisma=5, clevel=1, proficiencies=[], traits=['poison immune', 'extra attack'], spells=[], xp=1800, death_function=monster_death, ac=17, num_dmg_die=2, dmg_die=8, dmg_bonus=5, dmg_type = 'bludgeoning', to_hit=8, challenge_rating=5)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'E', 'earth elemental', 'dark orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE139", 16)
	monster.small_char = int("0xE639", 16)
	monster.move_cost = 100
	monster.description = 'An earth elemental plods forward like a walking hill, club-like arms of jagged stone swinging at its sides. Its head and body consist of dirt and stone, occasionally set with chunks of metal, gems, and bright minerals.'
	return monster
	
def create_elephant(x, y):
	fighter_component = Fighter(hp=76, strength=22, dexterity=9, constitution=17, intelligence=3, wisdom=11, charisma=6, clevel=1, proficiencies=[], traits=['charge'], spells=[], xp=1100, death_function=monster_death, ac=12, num_dmg_die=3, dmg_die=8, dmg_bonus=5, dmg_type = 'piercing', to_hit=8, challenge_rating=4)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'elephant', 'light grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE140", 16)
	monster.small_char = int("0xE640", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_elk(x, y):
	fighter_component = Fighter(hp=13, strength=16, dexterity=10, constitution=12, intelligence=2, wisdom=10, charisma=6, clevel=1, proficiencies=[], traits=['charge'], spells=[], xp=50, death_function=monster_death, ac=10, num_dmg_die=1, dmg_die=6, dmg_bonus=3, dmg_type = 'bludgeoning', to_hit=5, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'elk', 'light amber', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE141", 16)
	monster.small_char = int("0xE641", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_fire_elemental(x, y):
	fighter_component = Fighter(hp=102, strength=10, dexterity=17, constitution=16, intelligence=6, wisdom=10, charisma=7, clevel=1, proficiencies=[], traits=['illumination', 'fire immune', 'extra attack'], spells=[], xp=1800, death_function=monster_death, ac=13, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'fire', to_hit=6, challenge_rating=5)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'E', 'fire elemental', 'red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE142", 16)
	monster.small_char = int("0xE642", 16)
	monster.move_cost = 60
	monster.description = 'A faint humanoid shape shows in a fire elemental’s capricious devastation. Wherever it moves, it sets its surroundings ablaze, turning the world to ash, smoke, and cinders.'
	return monster
	
def create_fire_giant(x, y):
	fighter_component = Fighter(hp=162, strength=25, dexterity=9, constitution=23, intelligence=10, wisdom=14, charisma=13, clevel=1, proficiencies=[], traits=['fire immune', 'rock', 'extra attack'], spells=[], xp=5000, death_function=monster_death, ac=18, num_dmg_die=6, dmg_die=6, dmg_bonus=7, dmg_type = 'slashing', to_hit=11, challenge_rating=9)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'fire giant', 'red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE143", 16)
	monster.small_char = int("0xE643", 16)
	monster.move_cost = 100
	monster.description = 'With dark skin and flaming red hair, fire giants have a fearsome reputation as soldiers and conquerors. They dwell among volcanoes, lava flows, and rocky mountains, and are known for their ability to burn, plunder, and destroy.'
	return monster
	
def create_flameskull(x, y):
	fighter_component = Fighter(hp=40, strength=1, dexterity=17, constitution=14, intelligence=16, wisdom=10, charisma=11, clevel=1, proficiencies=[], traits=['illumination', 'flying', 'poison immune', 'fire immune', 'cold immune', 'extra attack', 'undead'], spells=[], xp=1100, death_function=monster_death, ac=13, num_dmg_die=3, dmg_die=6, dmg_bonus=0, dmg_type = 'fire', to_hit=5, challenge_rating=4)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'e', 'flameskull', 'red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE144", 16)
	monster.small_char = int("0xE644", 16)
	monster.move_cost = 75
	monster.description = 'Blazing green flames and mad, echoing laughter surround an undead flameskull. This disembodied skull blasts foes with fiery rays from its eyes and dreadful spells called up from the dark recesses of its memory.'
	return monster
	
def create_flesh_golem(x, y):
	fighter_component = Fighter(hp=93, strength=19, dexterity=9, constitution=18, intelligence=6, wisdom=10, charisma=5, clevel=1, proficiencies=[], traits=['extra attack', 'construct'], spells=[], xp=1800, death_function=monster_death, ac=9, num_dmg_die=2, dmg_die=8, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=7, challenge_rating=5)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'flesh golem', 'gold', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE145", 16)
	monster.small_char = int("0xE645", 16)
	monster.move_cost = 100
	monster.description = 'A flesh golem is a grisly assortment of humanoid body parts stitched and bolted together into a muscled brute imbued with formidable strength. Powerful enchantments protect it, deflecting spells and all but the most potent weapons.'
	return monster
	
def create_flying_snake(x, y):
	fighter_component = Fighter(hp=5, strength=4, dexterity=18, constitution=11, intelligence=2, wisdom=12, charisma=5, clevel=1, proficiencies=[], traits=['flying', 'blindsight', 'poisonous'], spells=[], xp=25, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=6, challenge_rating=0.125)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'S', 'flying snake', 'lime' , blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, num_dmg_die=3, dmg_die=4, dmg_type='poison')
	#note - no saving throw for flying snake venom
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE146", 16)
	monster.small_char = int("0xE646", 16)
	monster.move_cost = 50
	monster.description = 'A flying snake is a brightly colored, winged serpent found in remote jungles.'
	return monster
	
def create_flying_sword(x, y):
	fighter_component = Fighter(hp=17, strength=12, dexterity=15, constitution=11, intelligence=1, wisdom=5, charisma=1, clevel=1, proficiencies=[], traits=['poison immune', 'flying', 'blindsight', 'construct'], spells=[], xp=50, death_function=monster_death, ac=17, num_dmg_die=1, dmg_die=8, dmg_bonus=1, dmg_type = 'slashing', to_hit=3, challenge_rating=0.25)  
	ai_component = BasicMonster()
	monster = Object(x, y, ')', 'flying sword', 'sky', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE147", 16)
	monster.small_char = int("0xE647", 16)
	monster.move_cost = 50
	monster.description = 'A magically animated flying sword dances through the air, fighting like a warrior that can’t be injured.'
	return monster
	
def create_frog(x, y):
	fighter_component = Fighter(hp=1, strength=1, dexterity=13, constitution=8, intelligence=1, wisdom=8, charisma=3, clevel=1, proficiencies=[], traits=['darkvision', 'amphibious'], spells=[], xp=10, death_function=monster_death, ac=11, num_dmg_die=0, dmg_die=0, dmg_bonus=0, dmg_type = 'bludgeoning', to_hit=0, challenge_rating=0)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'F', 'frog', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE148", 16)
	monster.small_char = int("0xE648", 16)
	monster.move_cost = 150
	monster.description = 'A frog has no effective attacks. It feeds on small insects and typically dwells near water, in trees, or underground.'
	return monster
	
def create_frost_giant(x, y):
	fighter_component = Fighter(hp=138, strength=23, dexterity=9, constitution=21, intelligence=9, wisdom=10, charisma=12, clevel=1, proficiencies=[], traits=['cold immune', 'rock', 'extra attack'], spells=[], xp=3900, death_function=monster_death, ac=15, num_dmg_die=3, dmg_die=12, dmg_bonus=6, dmg_type = 'slashing', to_hit=9, challenge_rating=8)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'frost giant', 'blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE149", 16)
	monster.small_char = int("0xE649", 16)
	monster.move_cost = 75
	monster.description = 'Frost giants are creatures of ice and snow, with hair and beards of pale white or light blue, and flesh as blue as glacial ice. They respect only brute strength and skill in battle.'
	return monster
	
def create_gargoyle(x, y):
	fighter_component = Fighter(hp=52, strength=15, dexterity=11, constitution=16, intelligence=6, wisdom=11, charisma=7, clevel=1, proficiencies=[], traits=['poison immune', 'extra attack'], spells=[], xp=450, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=2)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'g', 'gargoyle', 'darker red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE150", 16)
	monster.small_char = int("0xE650", 16)
	monster.move_cost = 50
	monster.description = 'These malevolent creatures of elemental earth resemble grotesque, fiendish statues. A gargoyle lurks among masonry and ruins, delighting in the terror it creates when it breaks from its suspended pose.'
	return monster
	
def create_ghost(x, y):
	fighter_component = Fighter(hp=45, strength=7, dexterity=13, constitution=10, intelligence=10, wisdom=12, charisma=17, clevel=1, proficiencies=[], traits=['poison immune', 'cold immune', 'necrotic immune', 'undead'], spells=[], xp=1100, death_function=monster_death, ac=11, num_dmg_die=4, dmg_die=6, dmg_bonus=3, dmg_type = 'necrotic', to_hit=5, challenge_rating=4)	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'ghost', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE151", 16)
	monster.small_char = int("0xE651", 16)
	monster.move_cost = 75
	monster.description = 'A ghost is the soul of a once-living creature, bound to haunt a location, creature, or object from its life.'
	return monster
	
def create_ghoul(x, y):
	fighter_component = Fighter(hp=22, strength=13, dexterity=15, constitution=10, intelligence=7, wisdom=10, charisma=6, clevel=1, proficiencies=[], traits=['poison immune', 'necrotic immune', 'darkvision', 'undead'], spells=[], xp=200, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=2, challenge_rating=1)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'Z', 'ghoul', 'dark red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE152", 16)
	monster.small_char = int("0xE652", 16)
	monster.move_cost = 100
	monster.description = 'With their razor-sharp teeth and jagged claws, ghouls roam the night in packs, driven by an insatiable hunger for humanoid flesh.'
	return monster
	
def create_giant_ape(x, y):
	fighter_component = Fighter(hp=157, strength=23, dexterity=14, constitution=18, intelligence=7, wisdom=12, charisma=7, clevel=1, proficiencies=[], traits=['rock', 'extra attack'], spells=[], xp=2900, death_function=monster_death, ac=12, num_dmg_die=3, dmg_die=10, dmg_bonus=6, dmg_type = 'bludgeoning', to_hit=9, challenge_rating=7)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'Y', 'giant ape', 'brass', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE153", 16)
	monster.small_char = int("0xE653", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_giant_badger(x, y):
	fighter_component = Fighter(hp=13, strength=13, dexterity=10, constitution=15, intelligence=2, wisdom=12, charisma=5, clevel=1, proficiencies=[], traits=['extra attack'], spells=[], xp=50, death_function=monster_death, ac=10, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.25)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'giant badger', 'light grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE154", 16)
	monster.small_char = int("0xE654", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_bat(x, y):
	fighter_component = Fighter(hp=22, strength=15, dexterity=16, constitution=11, intelligence=2, wisdom=12, charisma=6, clevel=1, proficiencies=['perception'], traits=['flying', 'blindsight'], spells=[], xp=50, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'giant bat', 'dark orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE155", 16)
	monster.small_char = int("0xE655", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster
	
def create_giant_boar(x, y):
	fighter_component = Fighter(hp=42, strength=17, dexterity=10, constitution=16, intelligence=2, wisdom=7, charisma=5, clevel=1, proficiencies=[], traits=['relentless', 'charge'], spells=[], xp=450, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'slashing', to_hit=5, challenge_rating=2)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'giant boar', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE156", 16)
	monster.small_char = int("0xE656", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_giant_centipede(x, y):
	fighter_component = Fighter(hp=4, strength=5, dexterity=14, constitution=12, intelligence=1, wisdom=7, charisma=3, clevel=1, proficiencies=[], traits=['blindsight'], spells=[], xp=50, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 's', 'giant centipede', 'light green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE157", 16)
	monster.small_char = int("0xE657", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_constrictor_snake(x, y):
	fighter_component = Fighter(hp=60, strength=19, dexterity=14, constitution=12, intelligence=1, wisdom=10, charisma=3, clevel=1, proficiencies=[], traits=['blindsight', 'constrict'], spells=[], xp=450, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'piercing', to_hit=6, challenge_rating=2)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'S', 'giant constrictor snake', 'light green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE158", 16)
	monster.small_char = int("0xE658", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_crab(x, y):
	fighter_component = Fighter(hp=13, strength=13, dexterity=15, constitution=11, intelligence=1, wisdom=9, charisma=3, clevel=1, proficiencies=[], traits=['blindsight', 'amphibious'], spells=[], xp=25, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'bludgeoning', to_hit=3, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'a', 'giant crab', 'flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE159", 16)
	monster.small_char = int("0xE659", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_crocodile(x, y):
	fighter_component = Fighter(hp=85, strength=21, dexterity=9, constitution=17, intelligence=2, wisdom=10, charisma=7, clevel=1, proficiencies=[], traits=['amphibious', 'extra attack'], spells=[], xp=1800, death_function=monster_death, ac=14, num_dmg_die=3, dmg_die=10, dmg_bonus=5, dmg_type = 'piercing', to_hit=8, challenge_rating=5)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'giant crocodile', 'dark green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE160", 16)
	monster.small_char = int("0xE660", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_eagle(x, y):
	fighter_component = Fighter(hp=26, strength=16, dexterity=17, constitution=13, intelligence=8, wisdom=14, charisma=10, clevel=1, proficiencies=['perception'], traits=['flying', 'extra attack'], spells=[], xp=200, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'giant eagle', 'gold', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE161", 16)
	monster.small_char = int("0xE661", 16)
	monster.move_cost = 37
	monster.description = 'A giant eagle is a noble creature that speaks its own language and understands some speech.'
	return monster
	
def create_giant_elk(x, y):
	fighter_component = Fighter(hp=42, strength=19, dexterity=16, constitution=14, intelligence=7, wisdom=14, charisma=10, clevel=1, proficiencies=[], traits=['charge'], spells=[], xp=450, death_function=monster_death, ac=14, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=6, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'giant elk', 'orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE162", 16)
	monster.small_char = int("0xE662", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster
	
def create_giant_fire_beetle(x, y):
	fighter_component = Fighter(hp=4, strength=8, dexterity=10, constitution=12, intelligence=1, wisdom=7, charisma=3, clevel=1, proficiencies=[], traits=['blindsight', 'illumination'], spells=[], xp=10, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=-1, dmg_type = 'slashing', to_hit=1, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'a', 'giant fire beetle', 'red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE163", 16)
	monster.small_char = int("0xE663", 16)
	monster.move_cost = 100
	monster.description = 'A giant fire beetle is a nocturnal creature that features a pair of glowing glands that give off light for 1d6 days after the beetle dies.'
	return monster
	
def create_giant_frog(x, y):
	fighter_component = Fighter(hp=18, strength=12, dexterity=13, constitution=11, intelligence=2, wisdom=10, charisma=3, clevel=1, proficiencies=[], traits=['darkvision', 'amphibious', 'swallow'], spells=[], xp=50, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'F', 'giant frog', 'sea', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE164", 16)
	monster.small_char = int("0xE664", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_goat(x, y):
	fighter_component = Fighter(hp=19, strength=17, dexterity=11, constitution=12, intelligence=3, wisdom=12, charisma=6, clevel=1, proficiencies=[], traits=['charge'], spells=[], xp=100, death_function=monster_death, ac=11, num_dmg_die=2, dmg_die=4, dmg_bonus=3, dmg_type = 'bludgeoning', to_hit=5, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'giant goat', 'light grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE165", 16)
	monster.small_char = int("0xE665", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_giant_hyena(x, y):
	fighter_component = Fighter(hp=45, strength=16, dexterity=14, constitution=14, intelligence=2, wisdom=12, charisma=7, clevel=1, proficiencies=[], traits=[], spells=[], xp=200, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'c', 'giant hyena', 'orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE166", 16)
	monster.small_char = int("0xE666", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_giant_lizard(x, y):
	fighter_component = Fighter(hp=19, strength=15, dexterity=12, constitution=13, intelligence=2, wisdom=10, charisma=5, clevel=1, proficiencies=[], traits=['darkvision'], spells=[], xp=50, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=8, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, ':', 'giant lizard', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE167", 16)
	monster.small_char = int("0xE667", 16)
	monster.move_cost = 100
	monster.description = 'Giant lizards are fearsome predators often used as mounts or draft animals by reptilian humanoids and residents of the Underdark.'
	return monster
	
def create_giant_octopus(x, y):
	fighter_component = Fighter(hp=52, strength=17, dexterity=13, constitution=13, intelligence=4, wisdom=10, charisma=4, clevel=1, proficiencies=[], traits=['stealthy', 'water'], spells=[], xp=200, death_function=monster_death, ac=11, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'bludgeoning', to_hit=5, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'giant octopus', 'sky', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE168", 16)
	monster.small_char = int("0xE668", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster
	
def create_giant_owl(x, y):
	fighter_component = Fighter(hp=19, strength=13, dexterity=15, constitution=12, intelligence=8, wisdom=13, charisma=10, clevel=1, proficiencies=['perception'], traits=['flying'], spells=[], xp=50, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=6, dmg_bonus=1, dmg_type = 'slashing', to_hit=3, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'giant owl', 'darker orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE169", 16)
	monster.small_char = int("0xE669", 16)
	monster.move_cost = 50
	monster.description = 'Giant owls are intelligent creatures that are the guardians of their woodland realms.'
	return monster
	
def create_giant_poisonous_snake(x, y):
	fighter_component = Fighter(hp=11, strength=10, dexterity=18, constitution=13, intelligence=2, wisdom=10, charisma=3, clevel=1, proficiencies=[], traits=['blindsight', 'poisonous'], spells=[], xp=50, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=4, dmg_bonus=4, dmg_type = 'piercing', to_hit=6, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'S', 'giant poisonous snake', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=11, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=3, dmg_die=6, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE170", 16)
	monster.small_char = int("0xE670", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_rat(x, y):
	fighter_component = Fighter(hp=7, strength=7, dexterity=15, constitution=11, intelligence=2, wisdom=10, charisma=4, clevel=1, proficiencies=['perception'], traits=['pack tactics'], spells=[], xp=25, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'r', 'giant rat', 'darker flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE171", 16)
	monster.small_char = int("0xE671", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_scorpion(x, y):
	fighter_component = Fighter(hp=52, strength=15, dexterity=13, constitution=15, intelligence=1, wisdom=9, charisma=3, clevel=1, proficiencies=[], traits=['blindsight', 'poisonous', 'extra attack'], spells=[], xp=700, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=10, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 's', 'giant scorpion', 'darker red', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=12, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=4, dmg_die=10, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE172", 16)
	monster.small_char = int("0xE672", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_giant_sea_horse(x, y):
	fighter_component = Fighter(hp=16, strength=12, dexterity=15, constitution=11, intelligence=2, wisdom=12, charisma=5, clevel=1, proficiencies=[], traits=['water', 'charge'], spells=[], xp=100, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'bludgeoning', to_hit=3, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'giant sea horse', 'blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE173", 16)
	monster.small_char = int("0xE673", 16)
	monster.move_cost = 75
	monster.description = 'Giant sea horses are often used as mounts by aquatic humanoids.'
	return monster
	
def create_giant_shark(x, y):
	fighter_component = Fighter(hp=126, strength=23, dexterity=11, constitution=21, intelligence=1, wisdom=10, charisma=5, clevel=1, proficiencies=[], traits=['water', 'blindsight', 'blood frenzy'], spells=[], xp=1800, death_function=monster_death, ac=13, num_dmg_die=3, dmg_die=10, dmg_bonus=6, dmg_type = 'piercing', to_hit=9, challenge_rating=5)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'giant shark', 'sky', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE174", 16)
	monster.small_char = int("0xE674", 16)
	monster.move_cost = 60
	monster.description = 'A giant shark is 30 feet long and normally found in deep oceans.'
	return monster
	
def create_giant_spider(x, y):
	fighter_component = Fighter(hp=26, strength=14, dexterity=16, constitution=12, intelligence=2, wisdom=11, charisma=4, clevel=1, proficiencies=[], traits=['blindsight', 'darkvision', 'poisonous', 'web'], spells=[], xp=200, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=8, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, 's', 'giant spider', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=11, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=2, dmg_die=8, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE175", 16)
	monster.small_char = int("0xE675", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_giant_toad(x, y):
	fighter_component = Fighter(hp=39, strength=15, dexterity=13, constitution=13, intelligence=2, wisdom=10, charisma=3, clevel=1, proficiencies=[], traits=['amphibious', 'swallow'], spells=[], xp=200, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=10, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'F', 'giant toad', 'darker flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE176", 16)
	monster.small_char = int("0xE676", 16)
	monster.move_cost = 150
	#monster.description = ''
	return monster
	
def create_giant_vulture(x, y):
	fighter_component = Fighter(hp=22, strength=15, dexterity=10, constitution=15, intelligence=6, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=['flying', 'pack tactics', 'extra attack'], spells=[], xp=200, death_function=monster_death, ac=10, num_dmg_die=2, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'giant vulture', 'darker red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE177", 16)
	monster.small_char = int("0xE677", 16)
	monster.move_cost = 50
	monster.description = 'A giant vulture has advanced intelligence and a malevolent bent.'
	return monster
	
def create_giant_wasp(x, y):
	fighter_component = Fighter(hp=13, strength=10, dexterity=14, constitution=10, intelligence=1, wisdom=10, charisma=3, clevel=1, proficiencies=[], traits=['flying', 'poisonous'], spells=[], xp=100, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'a', 'giant wasp', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=11, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=3, dmg_die=6, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE178", 16)
	monster.small_char = int("0xE678", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_giant_weasel(x, y):
	fighter_component = Fighter(hp=9, strength=11, dexterity=16, constitution=10, intelligence=4, wisdom=12, charisma=5, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=25, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=4, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'r', 'giant weasel', 'darker amber', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE179", 16)
	monster.small_char = int("0xE679", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_giant_wolf_spider(x, y):
	fighter_component = Fighter(hp=11, strength=12, dexterity=16, constitution=13, intelligence=3, wisdom=12, charisma=4, clevel=1, proficiencies=[], traits=['poisonous'], spells=[], xp=50, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 's', 'giant wolf spider', 'darker red', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=11, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=2, dmg_die=6, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE180", 16)
	monster.small_char = int("0xE680", 16)
	monster.move_cost = 75
	monster.description = 'Giant wolf spiders hunt prey across open ground or hide in burrows or crevices to attack from ambush.'
	return monster
	
def create_gnoll(x, y):
	fighter_component = Fighter(hp=22, strength=14, dexterity=12, constitution=11, intelligence=6, wisdom=10, charisma=7, clevel=1, proficiencies=[], traits=[], spells=[], xp=100, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.5)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'G', 'gnoll', 'orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE181", 16)
	monster.small_char = int("0xE681", 16)
	monster.move_cost = 100
	monster.description = 'Gnolls are feral, hyena-headed humanoids that attack without warning, slaughtering their victims and devouring their flesh.'
	return monster
	
def create_goat(x, y):
	fighter_component = Fighter(hp=4, strength=12, dexterity=10, constitution=11, intelligence=2, wisdom=10, charisma=5, clevel=1, proficiencies=[], traits=[], spells=[], xp=10, death_function=monster_death, ac=10, num_dmg_die=1, dmg_die=4, dmg_bonus=1, dmg_type = 'bludgeoning', to_hit=3, challenge_rating=0)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'goat', 'amber', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE182", 16)
	monster.small_char = int("0xE682", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_goblin(x, y):
	fighter_component = Fighter(hp=7, strength=8, dexterity=14, constitution=10, intelligence=10, wisdom=8, charisma=8, clevel=1, proficiencies=[], traits=['darkvision'], spells=[], xp=50, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'g', 'goblin', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE183", 16)
	monster.small_char = int("0xE683", 16)
	monster.move_cost = 100
	monster.description = 'Goblins are small, black-hearted humanoids that lair in despoiled dungeons and other dismal settings. Individually weak, they gather in large numbers to torment other creatures.'
	return monster
	
def create_grick(x, y):
	fighter_component = Fighter(hp=27, strength=14, dexterity=14, constitution=11, intelligence=3, wisdom=14, charisma=5, clevel=1, proficiencies=[], traits=['darkvision', 'extra attack'], spells=[], xp=450, death_function=monster_death, ac=14, num_dmg_die=2, dmg_die=6, dmg_bonus=2, dmg_type = 'slashing', to_hit=4, challenge_rating=2)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'x', 'grick', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE184", 16)
	monster.small_char = int("0xE684", 16)
	monster.move_cost = 100
	monster.description = 'This wormlike monstrosity blends in with the rock of the caverns it haunts. When prey comes near, its barbed tentacles unfurl to reveal its hungry, snapping beak.'
	return monster
	
def create_griffon(x, y):
	fighter_component = Fighter(hp=59, strength=18, dexterity=15, constitution=16, intelligence=2, wisdom=13, charisma=8, clevel=1, proficiencies=['perception'], traits=['extra attack', 'flying'], spells=[], xp=450, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=8, dmg_bonus=4, dmg_type = 'piercing', to_hit=6, challenge_rating=2)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'griffon', 'sky', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE185", 16)
	monster.small_char = int("0xE685", 16)
	monster.move_cost = 37
	monster.description = 'A griffon is an avian carnivore with the muscular body of a lion and the head, forelegs, and wings of an eagle.'
	return monster
	
def create_harpy(x, y):
	fighter_component = Fighter(hp=38, strength=12, dexterity=13, constitution=12, intelligence=7, wisdom=10, charisma=13, clevel=1, proficiencies=[], traits=['extra attack'], spells=[], xp=200, death_function=monster_death, ac=11, num_dmg_die=2, dmg_die=4, dmg_bonus=1, dmg_type = 'slashing', to_hit=3, challenge_rating=1)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'harpy', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE186", 16)
	monster.small_char = int("0xE686", 16)
	monster.move_cost = 75
	monster.description = 'A harpy combines the body, legs, and wings of a vulture with the torso, arms, and head of a human female. Its sweet song has lured countless adventurers to their deaths.'
	return monster
	
def create_hawk(x, y):
	fighter_component = Fighter(hp=1, strength=5, dexterity=16, constitution=8, intelligence=2, wisdom=14, charisma=6, clevel=1, proficiencies=['perception'], traits=['flying'], spells=[], xp=25, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=1, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.125)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'hawk', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE187", 16)
	monster.small_char = int("0xE687", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster
	
def create_hell_hound(x, y):
	fighter_component = Fighter(hp=45, strength=17, dexterity=12, constitution=14, intelligence=6, wisdom=13, charisma=6, clevel=1, proficiencies=['perception'], traits=['pack tactics', 'fire immune', 'darkvision', 'fire breath'], spells=[], xp=700, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=8, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'hell hound', 'light red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE188", 16)
	monster.small_char = int("0xE688", 16)
	monster.move_cost = 60
	monster.description = 'Fire-breathing fiends that take the form of powerful dogs, hell hounds commonly serve evil creatures that use them as guard animals and companions.'
	return monster
	
def create_hill_giant(x, y):
	fighter_component = Fighter(hp=105, strength=21, dexterity=8, constitution=19, intelligence=5, wisdom=9, charisma=6, clevel=1, proficiencies=[], traits=['rock', 'extra attack'], spells=[], xp=1800, death_function=monster_death, ac=13, num_dmg_die=3, dmg_die=8, dmg_bonus=5, dmg_type = 'bludgeoning', to_hit=8, challenge_rating=5)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'hill giant', 'dark flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE189", 16)
	monster.small_char = int("0xE689", 16)
	monster.move_cost = 75
	monster.description = 'Hill giants are selfish, dimwitted brutes that hunt and raid in constant search of food. Their skins are tan from lives spent beneath the sun, and their weapons are uprooted trees and rocks pulled from the earth.'
	return monster
	
def create_hippogriff(x, y):
	fighter_component = Fighter(hp=19, strength=17, dexterity=13, constitution=13, intelligence=2, wisdom=12, charisma=8, clevel=1, proficiencies=['perception'], traits=['extra attack', 'flying'], spells=[], xp=200, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=10, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=1)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'hippogriff', 'violet', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE190", 16)
	monster.small_char = int("0xE690", 16)
	monster.move_cost = 50
	monster.description = 'A hippogriff is a magical creature possessing the wings and forelimbs of an eagle, the hindquarters of a horse, and a head that combines the features of both animals.'
	return monster
	
def create_hobgoblin(x, y):
	fighter_component = Fighter(hp=11, strength=13, dexterity=12, constitution=12, intelligence=10, wisdom=10, charisma=9, clevel=1, proficiencies=[], traits=[], spells=[], xp=100, death_function=monster_death, ac=18, num_dmg_die=1, dmg_die=8, dmg_bonus=1, dmg_type = 'slashing', to_hit=3, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'o', 'hobgoblin', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE191", 16)
	monster.small_char = int("0xE691", 16)
	monster.move_cost = 100
	monster.description = 'Hobgoblins are large goblinoids with dark orange or red-orange skin. A hobgoblin measures virtue by physical strength and martial prowess, caring about nothing except skill and cunning in battle.'
	return monster
	
def create_hunter_shark(x, y):
	fighter_component = Fighter(hp=45, strength=18, dexterity=13, constitution=15, intelligence=1, wisdom=10, charisma=4, clevel=1, proficiencies=[], traits=['water', 'blindsight', 'blood frenzy'], spells=[], xp=450, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=8, dmg_bonus=4, dmg_type = 'piercing', to_hit=6, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'hunter shark', 'sea', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE192", 16)
	monster.small_char = int("0xE692", 16)
	monster.move_cost = 75
	monster.description = 'A hunter shark is 15 to 20 feet long, and usually hunts alone in deep waters.'
	return monster
	
def create_hydra(x, y):
	fighter_component = Fighter(hp=172, strength=20, dexterity=12, constitution=20, intelligence=2, wisdom=10, charisma=7, clevel=1, proficiencies=[], traits=['darkvision', 'multiple heads', 'extra attack', 'extra attack'], spells=[], xp=3900, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=10, dmg_bonus=5, dmg_type = 'piercing', to_hit=8, challenge_rating=8)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'hydra', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE193", 16)
	monster.small_char = int("0xE693", 16)
	monster.move_cost = 100
	monster.description = 'The hydra is a reptilian horror with a crocodilian body and multiple heads on long, serpentine necks. Although its heads can be severed, the hydra magically regrows them in short order.'
	return monster
	
def create_hyena(x, y):
	fighter_component = Fighter(hp=5, strength=11, dexterity=13, constitution=12, intelligence=2, wisdom=12, charisma=5, clevel=1, proficiencies=[], traits=['pack tactics'], spells=[], xp=10, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=6, dmg_bonus=0, dmg_type = 'piercing', to_hit=2, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'hyena', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE194", 16)
	monster.small_char = int("0xE694", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_jackal(x, y):
	fighter_component = Fighter(hp=3, strength=8, dexterity=15, constitution=11, intelligence=3, wisdom=12, charisma=6, clevel=1, proficiencies=['perception'], traits=['pack tactics'], spells=[], xp=10, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=4, dmg_bonus=-1, dmg_type = 'piercing', to_hit=1, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'jackal', 'orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE195", 16)
	monster.small_char = int("0xE695", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_killer_whale(x, y):
	fighter_component = Fighter(hp=90, strength=19, dexterity=10, constitution=13, intelligence=3, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=['water', 'blindsight'], spells=[], xp=700, death_function=monster_death, ac=12, num_dmg_die=5, dmg_die=6, dmg_bonus=4, dmg_type = 'piercing', to_hit=6, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'killer whale', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE196", 16)
	monster.small_char = int("0xE696", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster
	
def create_kobold(x, y):
	fighter_component = Fighter(hp=5, strength=7, dexterity=15, constitution=9, intelligence=8, wisdom=7, charisma=8, clevel=1, proficiencies=[], traits=['pack tactics'], spells=[], xp=25, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, ranged_num_dmg_die=1, ranged_dmg_die=4, ranged_dmg_bonus=2, ranged_dmg_type='bludgeoning', ranged_to_hit=4, challenge_rating=0.125)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'k', 'kobold', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE197", 16)
	monster.small_char = int("0xE697", 16)
	monster.move_cost = 100
	monster.description = 'Kobolds are craven reptilian humanoids that commonly infest dungeons. They make up for their physical ineptitude with a cleverness for trap making.'
	return monster
	
def create_lion(x, y):
	fighter_component = Fighter(hp=26, strength=17, dexterity=15, constitution=13, intelligence=3, wisdom=12, charisma=8, clevel=1, proficiencies=['perception'], traits=['pack tactics'], spells=[], xp=200, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=8, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'c', 'lion', 'orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE198", 16)
	monster.small_char = int("0xE698", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_lizard(x, y):
	fighter_component = Fighter(hp=2, strength=2, dexterity=11, constitution=10, intelligence=1, wisdom=8, charisma=3, clevel=1, proficiencies=[], traits=['darkvision', 'pack tactics'], spells=[], xp=10, death_function=monster_death, ac=10, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=0, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, ':', 'lizard', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE199", 16)
	monster.small_char = int("0xE699", 16)
	monster.move_cost = 150
	#monster.description = ''
	return monster
	
def create_lizardfolk(x, y):
	fighter_component = Fighter(hp=22, strength=15, dexterity=10, constitution=13, intelligence=7, wisdom=12, charisma=7, clevel=1, proficiencies=[], traits=['extra attack'], spells=[], xp=100, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'h', 'lizardfolk', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE200", 16)
	monster.small_char = int("0xE700", 16)
	monster.move_cost = 100
	monster.description = 'Lizardfolk are primitive reptilian humanoids that lurk in swamps and jungles. Fiercely territorial, they kill when it is expedient and do whatever it takes to survive.'
	return monster
	
def create_mammoth(x, y):
	fighter_component = Fighter(hp=126, strength=24, dexterity=9, constitution=21, intelligence=3, wisdom=11, charisma=6, clevel=1, proficiencies=[], traits=['charge'], spells=[], xp=2300, death_function=monster_death, ac=13, num_dmg_die=4, dmg_die=8, dmg_bonus=7, dmg_type = 'piercing', to_hit=10, challenge_rating=6)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'mammoth', 'light orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE201", 16)
	monster.small_char = int("0xE701", 16)
	monster.move_cost = 75
	monster.description = 'A mammoth is an elephantine creature with thick fur and long tusks.'
	return monster
	
def create_manticore(x, y):
	fighter_component = Fighter(hp=68, strength=17, dexterity=16, constitution=17, intelligence=7, wisdom=12, charisma=8, clevel=1, proficiencies=[], traits=['extra attack', 'tail spike'], spells=[], xp=700, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=8, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'manticore', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE202", 16)
	monster.small_char = int("0xE702", 16)
	monster.move_cost = 60
	monster.description = 'A manticore has a vaguely humanoid head, the body of a lion, and the wings of a dragon. Its long tail ends in a cluster of deadly spikes that can impale prey at impressive range.'
	return monster
	
def create_mastiff(x, y):
	fighter_component = Fighter(hp=5, strength=13, dexterity=14, constitution=12, intelligence=3, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=25, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'mastiff', 'light orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE203", 16)
	monster.small_char = int("0xE703", 16)
	monster.move_cost = 75
	monster.description = 'Mastiffs are impressive hounds prized by humanoids for their loyalty and keen senses.'
	return monster
	
def create_medusa(x, y):
	fighter_component = Fighter(hp=127, strength=10, dexterity=15, constitution=16, intelligence=12, wisdom=13, charisma=15, clevel=1, proficiencies=[], traits=['petrifying gaze', 'extra attack', 'poisonous'], spells=[], xp=2300, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=5, challenge_rating=6)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'h', 'medusa', 'purple', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, num_dmg_die=4, dmg_die=6, dmg_type='poison')
	#note - no saving throw on medusa poison
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE204", 16)
	monster.small_char = int("0xE704", 16)
	monster.move_cost = 100
	monster.description = 'A victim of a terrible curse, the serpent-haired medusa petrifies all those who gaze upon it, turning creatures into stone monuments to its corruption.'
	return monster
	
def create_merfolk(x, y):
	fighter_component = Fighter(hp=11, strength=10, dexterity=13, constitution=12, intelligence=11, wisdom=11, charisma=12, clevel=1, proficiencies=[], traits=['amphibious', 'water'], spells=[], xp=25, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=6, dmg_bonus=0, dmg_type = 'piercing', to_hit=2, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'h', 'merfolk', 'sky', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE205", 16)
	monster.small_char = int("0xE705", 16)
	monster.move_cost = 75
	monster.description = 'Merfolk are aquatic humanoids with the lower body of a fish. They live in small tribes beneath the waves'
	return monster
	
def create_minotaur(x, y):
	fighter_component = Fighter(hp=76, strength=18, dexterity=11, constitution=16, intelligence=6, wisdom=16, charisma=9, clevel=1, proficiencies=[], traits=['charge', 'reckless'], spells=[], xp=700, death_function=monster_death, ac=14, num_dmg_die=2, dmg_die=12, dmg_bonus=4, dmg_type = 'slashing', to_hit=6, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'minotaur', 'flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE206", 16)
	monster.small_char = int("0xE706", 16)
	monster.move_cost = 75
	monster.description = 'Their fur stained with the blood of fallen foes, minotaurs are massive, bull-headed humanoids whose roar is a savage battle cry that all civilized creatures fear.'
	return monster
	
def create_mule(x, y):
	fighter_component = Fighter(hp=11, strength=14, dexterity=10, constitution=13, intelligence=2, wisdom=10, charisma=5, clevel=1, proficiencies=[], traits=[], spells=[], xp=25, death_function=monster_death, ac=10, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'bludgeoning', to_hit=2, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'mule', 'flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE207", 16)
	monster.small_char = int("0xE707", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_mummy(x, y):
	fighter_component = Fighter(hp=58, strength=16, dexterity=8, constitution=15, intelligence=6, wisdom=10, charisma=12, clevel=1, proficiencies=[], traits=['undead', 'rotting', 'dreadful glare'], spells=[], xp=700, death_function=monster_death, ac=11, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'bludgeoning', to_hit=5, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'M', 'mummy', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE208", 16)
	monster.small_char = int("0xE708", 16)
	monster.move_cost = 150
	monster.description = 'Raised by dark funerary rituals and still wrapped in the shrouds of death, mummies shamble out from lost temples and tombs to slay any who disturb their rest.'
	return monster
	
def create_nothic(x, y):
	fighter_component = Fighter(hp=45, strength=14, dexterity=16, constitution=16, intelligence=13, wisdom=10, charisma=8, clevel=1, proficiencies=['perception'], traits=['extra attack', 'rotting'], spells=[], xp=450, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=3, dmg_type = 'slashing', to_hit=4, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'X', 'nothic', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE209", 16)
	monster.small_char = int("0xE709", 16)
	monster.move_cost = 100
	monster.description = "A nothic is a monstrous creature with terrible talons and a single great eye. When driven to violence, it uses its horrific gaze to rot the flesh from its enemies' bones."
	return monster
	
def create_ochre_jelly(x, y):
	fighter_component = Fighter(hp=45, strength=15, dexterity=6, constitution=14, intelligence=2, wisdom=6, charisma=1, clevel=1, proficiencies=[], traits=['darkvision', 'lightning immune', 'slashing immune', 'acidic'], spells=[], xp=450, death_function=monster_death, ac=8, num_dmg_die=2, dmg_die=6, dmg_bonus=2, dmg_type = 'bludgeoning', to_hit=4, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'J', 'ochre jelly', 'crimson', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE210", 16)
	monster.small_char = int("0xE710", 16)
	monster.move_cost = 300
	monster.description = 'An ochre jelly is a yellowish ooze that can slide under doors and through narrow cracks in pursuit of creatures to devour.'
	return monster
	
def create_octopus(x, y):
	fighter_component = Fighter(hp=3, strength=4, dexterity=15, constitution=11, intelligence=3, wisdom=10, charisma=4, clevel=1, proficiencies=[], traits=['stealthy', 'water'], spells=[], xp=10, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'bludgeoning', to_hit=4, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'octopus', 'sky', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE211", 16)
	monster.small_char = int("0xE711", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_ogre(x, y):
	fighter_component = Fighter(hp=59, strength=19, dexterity=8, constitution=16, intelligence=5, wisdom=7, charisma=7, clevel=1, proficiencies=[], traits=['darkvision'], spells=[], xp=450, death_function=monster_death, ac=11, num_dmg_die=2, dmg_die=8, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=6, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'O', 'ogre', 'amber', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE212", 16)
	monster.small_char = int("0xE712", 16)
	monster.move_cost = 75
	monster.description = 'Ogres are hulking giants notorious for their quick tempers. When its rage is incited, an ogre lashes out in a frustrated tantrum until it runs out of objects or creatures to smash.'
	return monster
	
def create_orc(x, y):
	fighter_component = Fighter(hp=15, strength=16, dexterity=12, constitution=16, intelligence=7, wisdom=11, charisma=10, clevel=1, proficiencies=[], traits=[], spells=[], xp=100, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=12, dmg_bonus=3, dmg_type = 'slashing', to_hit=5, ranged_num_dmg_die=1, ranged_dmg_die=6, ranged_dmg_bonus=3, ranged_dmg_type='piercing', ranged_to_hit=5, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'o', 'orc', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE213", 16)
	monster.small_char = int("0xE713", 16)
	monster.move_cost = 100
	monster.description = 'Orcs are savage humanoids with stooped postures, piggish faces, and prominent teeth that resemble tusks. They gather in tribes that satisfy their bloodlust by slaying any humanoids that stand against them.'
	return monster
	
def create_owl(x, y):
	fighter_component = Fighter(hp=1, strength=3, dexterity=13, constitution=8, intelligence=2, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=['flying'], spells=[], xp=10, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'slashing', to_hit=3, challenge_rating=0)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'owl', 'brown', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE214", 16)
	monster.small_char = int("0xE714", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster
	
def create_owlbear(x, y):
	fighter_component = Fighter(hp=59, strength=20, dexterity=12, constitution=17, intelligence=3, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=['darkvision', 'extra attack'], spells=[], xp=700, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=10, dmg_bonus=5, dmg_type = 'piercing', to_hit=7, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'Y', 'owlbear', 'blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE215", 16)
	monster.small_char = int("0xE715", 16)
	monster.move_cost = 75
	monster.description = 'A monstrous cross between giant owl and bear, an owlbear’s reputation for ferocity and aggression makes it one of the most feared predators of the wild.'
	return monster
	
def create_panther(x, y):
	fighter_component = Fighter(hp=13, strength=14, dexterity=15, constitution=10, intelligence=3, wisdom=14, charisma=7, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=50, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'c', 'panther', 'dark grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE216", 16)
	monster.small_char = int("0xE716", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_pegasus(x, y):
	fighter_component = Fighter(hp=59, strength=18, dexterity=15, constitution=16, intelligence=10, wisdom=15, charisma=13, clevel=1, proficiencies=[], traits=['flying'], spells=[], xp=450, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=6, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'u', 'pegasus', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE217", 16)
	monster.small_char = int("0xE717", 16)
	monster.move_cost = 50
	monster.description = 'The white winged horses known as pegasi soar through the skies, a vision of grace and majesty.'
	return monster
	
def create_phase_spider(x, y):
	fighter_component = Fighter(hp=32, strength=15, dexterity=15, constitution=12, intelligence=6, wisdom=10, charisma=6, clevel=1, proficiencies=[], traits=['poisonous'], spells=['ethereal jaunt'], xp=700, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=10, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 's', 'giant phase spider', 'purple', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=11, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=4, dmg_die=8, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE218", 16)
	monster.small_char = int("0xE718", 16)
	monster.move_cost = 100
	monster.description = 'A phase spider possesses the magical ability to phase in and out of the Ethereal Plane. It seems to appear out of nowhere and quickly vanishes after attacking.'
	return monster
	
def create_plesiosaurus(x, y):
	fighter_component = Fighter(hp=68, strength=18, dexterity=15, constitution=16, intelligence=2, wisdom=12, charisma=5, clevel=1, proficiencies=[], traits=['water'], spells=[], xp=450, death_function=monster_death, ac=13, num_dmg_die=3, dmg_die=6, dmg_bonus=4, dmg_type = 'piercing', to_hit=6, challenge_rating=2)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'plesiosaurus', 'light green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE219", 16)
	monster.small_char = int("0xE719", 16)
	monster.move_cost = 75
	monster.description = 'This predatory marine reptile and cousin to the dinosaurs attacks any creature it encounters. Its long, flexible neck lets it twist in any direction to deliver a powerful bite.'
	return monster
	
def create_poisonous_snake(x, y):
	fighter_component = Fighter(hp=2, strength=2, dexterity=16, constitution=11, intelligence=1, wisdom=10, charisma=3, clevel=1, proficiencies=[], traits=['blindsight', 'poisonous'], spells=[], xp=25, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=5, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'S', 'poisonous snake', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=10, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=2, dmg_die=4, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE220", 16)
	monster.small_char = int("0xE720", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_polar_bear(x, y):
	fighter_component = Fighter(hp=42, strength=20, dexterity=10, constitution=16, intelligence=2, wisdom=13, charisma=7, clevel=1, proficiencies=['perception'], traits=['extra attack'], spells=[], xp=450, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=8, dmg_bonus=5, dmg_type = 'piercing', to_hit=7, challenge_rating=2)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'h', 'polar bear', 'light grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE221", 16)
	monster.small_char = int("0xE721", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_pony(x, y):
	fighter_component = Fighter(hp=11, strength=15, dexterity=10, constitution=13, intelligence=2, wisdom=11, charisma=7, clevel=1, proficiencies=[], traits=[], spells=[], xp=25, death_function=monster_death, ac=10, num_dmg_die=2, dmg_die=4, dmg_bonus=2, dmg_type = 'bludgeoning', to_hit=4, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'pony', 'light grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE222", 16)
	monster.small_char = int("0xE722", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_pteranodon(x, y):
	fighter_component = Fighter(hp=13, strength=12, dexterity=15, constitution=10, intelligence=2, wisdom=9, charisma=5, clevel=1, proficiencies=[], traits=['flying'], spells=[], xp=50, death_function=monster_death, ac=13, num_dmg_die=2, dmg_die=4, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=2)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'pteranodon', 'dark green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE223", 16)
	monster.small_char = int("0xE723", 16)
	monster.move_cost = 50
	monster.description = 'These flying reptilian cousins to the dinosaurs have no teeth, instead using their sharp beaks to stab prey too large to swallow with one gulp.'
	return monster
	
def create_quipper(x, y):
	fighter_component = Fighter(hp=1, strength=2, dexterity=16, constitution=9, intelligence=1, wisdom=7, charisma=2, clevel=1, proficiencies=[], traits=['water'], spells=[], xp=10, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=5, challenge_rating=0)	 
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'quipper', 'light blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE224", 16)
	monster.small_char = int("0xE725", 16)
	monster.move_cost = 75
	monster.description = 'A quipper is a carnivorous fish with sharp teeth.'
	return monster
	
def create_rat(x, y):
	fighter_component = Fighter(hp=1, strength=2, dexterity=11, constitution=9, intelligence=2, wisdom=10, charisma=4, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=10, death_function=monster_death, ac=10, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=0, challenge_rating=0)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'r', 'rat', 'brown', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE225", 16)
	monster.small_char = int("0xE725", 16)
	monster.move_cost = 150
	#monster.description = ''
	return monster
	
def create_raven(x, y):
	fighter_component = Fighter(hp=1, strength=2, dexterity=14, constitution=8, intelligence=2, wisdom=12, charisma=6, clevel=1, proficiencies=[], traits=['flying'], spells=[], xp=10, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=4, challenge_rating=0)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'raven', 'dark grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE226", 16)
	monster.small_char = int("0xE726", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_reef_shark(x, y):
	fighter_component = Fighter(hp=22, strength=14, dexterity=13, constitution=13, intelligence=1, wisdom=10, charisma=4, clevel=1, proficiencies=[], traits=['water', 'pack tactics'], spells=[], xp=100, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=8, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'reef shark', 'cyan', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE227", 16)
	monster.small_char = int("0xE727", 16)
	monster.move_cost = 75
	monster.description = 'Reef sharks measure 6 to 10 feet long, and inhabit shallow waters and coral reefs.'
	return monster
	
def create_rhinoceros(x, y):
	fighter_component = Fighter(hp=45, strength=21, dexterity=8, constitution=15, intelligence=2, wisdom=12, charisma=6, clevel=1, proficiencies=[], traits=['charge'], spells=[], xp=450, death_function=monster_death, ac=11, num_dmg_die=2, dmg_die=8, dmg_bonus=5, dmg_type = 'bludgeoning', to_hit=7, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'rhinoceros', 'light grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE228", 16)
	monster.small_char = int("0xE728", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_riding_horse(x, y):
	fighter_component = Fighter(hp=13, strength=16, dexterity=10, constitution=12, intelligence=2, wisdom=11, charisma=7, clevel=1, proficiencies=[], traits=[], spells=[], xp=50, death_function=monster_death, ac=10, num_dmg_die=2, dmg_die=4, dmg_bonus=3, dmg_type = 'bludgeoning', to_hit=5, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'riding horse', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE229", 16)
	monster.small_char = int("0xE729", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster

def create_sabre_toothed_tiger(x, y):
	fighter_component = Fighter(hp=52, strength=18, dexterity=14, constitution=15, intelligence=3, wisdom=12, charisma=8, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=450, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=10, dmg_bonus=5, dmg_type = 'piercing', to_hit=6, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'c', 'sabre-toothed tiger', 'dark orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE230", 16)
	monster.small_char = int("0xE730", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_satyr(x, y):
	fighter_component = Fighter(hp=31, strength=12, dexterity=16, constitution=11, intelligence=12, wisdom=10, charisma=14, clevel=1, proficiencies=[], traits=['magic resistance'], spells=[], xp=100, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=6, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'h', 'satyr', 'blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE231", 16)
	monster.small_char = int("0xE731", 16)
	monster.move_cost = 75
	monster.description = 'Satyrs are raucous fey that resemble stout male humans with the furry lower bodies and cloven hooves of goats. They frolic in wild forests, driven by curiosity and hedonism in equal measure.'
	return monster
	
def create_scorpion(x, y):
	fighter_component = Fighter(hp=1, strength=2, dexterity=11, constitution=8, intelligence=1, wisdom=8, charisma=2, clevel=1, proficiencies=[], traits=['blindsight', 'poisonous'], spells=[], xp=10, death_function=monster_death, ac=11, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=2, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 's', 'scorpion', 'red', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=9, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=1, dmg_die=8, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE232", 16)
	monster.small_char = int("0xE732", 16)
	monster.move_cost = 300
	#monster.description = ''
	return monster
	
def create_sea_horse(x, y):
	fighter_component = Fighter(hp=1, strength=1, dexterity=12, constitution=8, intelligence=1, wisdom=10, charisma=2, clevel=1, proficiencies=[], traits=['water'], spells=[], xp=0, death_function=monster_death, ac=11, num_dmg_die=0, dmg_die=0, dmg_bonus=0, dmg_type = 'bludgeoning', to_hit=0, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'sea horse', 'light blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE233", 16)
	monster.small_char = int("0xE733", 16)
	monster.move_cost = 150
	#monster.description = ''
	return monster
	
def create_skeleton(x, y):
	fighter_component = Fighter(hp=13, strength=10, dexterity=14, constitution=15, intelligence=6, wisdom=8, charisma=5, clevel=1, proficiencies=[], traits=['poison immune', 'undead'], spells=[], xp=50, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, ranged_num_dmg_die=1, ranged_dmg_die=6, ranged_dmg_bonus=2, ranged_dmg_type='piercing', ranged_to_hit=4, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'Z', 'skeleton', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE234", 16)
	monster.small_char = int("0xE734", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_spectator(x, y):
	fighter_component = Fighter(hp=39, strength=8, dexterity=14, constitution=14, intelligence=13, wisdom=14, charisma=11, clevel=1, proficiencies=['perception'], traits=['darkvision'], spells=['confusion ray', 'paralysing ray', 'fear ray', 'wounding ray'], xp=700, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=6, dmg_bonus=-1, dmg_type = 'piercing', to_hit=1, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'X', 'spectator', 'purple', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE235", 16)
	monster.small_char = int("0xE735", 16)
	monster.move_cost = 100
	monster.description = 'A spectator is a lesser type of beholder — a foul and deadly aberration. It resembles a floating sphere with a gaping maw and a single great eye, set within four eyestalks that shoot forth deadly rays.'
	return monster
	
def create_spider(x, y):
	fighter_component = Fighter(hp=1, strength=2, dexterity=14, constitution=8, intelligence=1, wisdom=10, charisma=2, clevel=1, proficiencies=[], traits=['darkvision', 'poisonous', 'web'], spells=[], xp=10, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=4, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 's', 'spider', 'grey', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=9, damage_on_hit_save_dmg_modifer=0, num_dmg_die=1, dmg_die=4, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE236", 16)
	monster.small_char = int("0xE736", 16)
	monster.move_cost = 150
	#monster.description = ''
	return monster
	
def create_stirge(x, y):
	fighter_component = Fighter(hp=2, strength=16, dexterity=11, constitution=2, intelligence=8, wisdom=6, charisma=4, clevel=1, proficiencies=[], traits=['darkvision', 'blood drain'], spells=[], xp=25, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=4, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'a', 'stirge', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE237", 16)
	monster.small_char = int("0xE737", 16)
	monster.move_cost = 75
	monster.description = 'This horrid monster looks like a cross between a large bat and an oversized mosquito. Its legs end in sharp pincers, and its long, needle-like proboscis slashes the air as it seeks to feed on the blood of living creatures.'
	return monster
	
def create_stone_golem(x, y):
	fighter_component = Fighter(hp=178, strength=22, dexterity=9, constitution=20, intelligence=3, wisdom=11, charisma=1, clevel=1, proficiencies=[], traits=['darkvision', 'poison immune', 'extra attack', 'construct'], spells=[], xp=5900, death_function=monster_death, ac=17, num_dmg_die=3, dmg_die=8, dmg_bonus=6, dmg_type = 'bludgeoning', to_hit=10, challenge_rating=10)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'stone golem', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE238", 16)
	monster.small_char = int("0xE738", 16)
	monster.move_cost = 100
	monster.description = 'Stone golems are magical constructs cut and chiseled from stone to appear as tall, impressive statues. Like other golems, they are nearly impervious to spells and ordinary weapons.'
	return monster
	
def create_swarm_of_bats(x, y):
	fighter_component = Fighter(hp=22, strength=5, dexterity=15, constitution=10, intelligence=2, wisdom=12, charisma=4, clevel=1, proficiencies=['perception'], traits=['flying', 'blindsight'], spells=[], xp=50, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=4, dmg_bonus=0, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'swarm of bats', 'dark orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE239", 16)
	monster.small_char = int("0xE739", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_swarm_of_insects(x, y):
	fighter_component = Fighter(hp=22, strength=3, dexterity=13, constitution=10, intelligence=1, wisdom=7, charisma=1, clevel=1, proficiencies=[], traits=['blindsight'], spells=[], xp=100, death_function=monster_death, ac=12, num_dmg_die=4, dmg_die=4, dmg_bonus=0, dmg_type = 'piercing', to_hit=3, challenge_rating=0.5)
	ai_component = BasicMonster()
	monster = Object(x, y, 's', 'swarm of insects', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE240", 16)
	monster.small_char = int("0xE740", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_swarm_of_poisonous_snakes(x, y):
	fighter_component = Fighter(hp=36, strength=8, dexterity=18, constitution=11, intelligence=1, wisdom=10, charisma=3, clevel=1, proficiencies=[], traits=['blindsight', 'poisonous'], spells=[], xp=450, death_function=monster_death, ac=14, num_dmg_die=2, dmg_die=6, dmg_bonus=0, dmg_type = 'piercing', to_hit=6, challenge_rating=2)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'S', 'swarm of poisonous snakes', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	condition = Condition(name='venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=10, damage_on_hit_save_dmg_modifer=0.5, num_dmg_die=4, dmg_die=6, dmg_type='poison')
	condition.owner = monster
	fighter_component.conditions.append(condition)
	monster.big_char = int("0xE241", 16)
	monster.small_char = int("0xE741", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_swarm_of_quippers(x, y):
	fighter_component = Fighter(hp=28, strength=13, dexterity=16, constitution=9, intelligence=1, wisdom=7, charisma=2, clevel=1, proficiencies=[], traits=['water'], spells=[], xp=200, death_function=monster_death, ac=13, num_dmg_die=4, dmg_die=6, dmg_bonus=0, dmg_type = 'piercing', to_hit=5, challenge_rating=1)	 
	ai_component = BasicMonster()
	monster = Object(x, y, ';', 'swarm of quippers', 'light blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE242", 16)
	monster.small_char = int("0xE742", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_swarm_of_rats(x, y):
	fighter_component = Fighter(hp=24, strength=9, dexterity=11, constitution=9, intelligence=2, wisdom=10, charisma=3, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=50, death_function=monster_death, ac=10, num_dmg_die=2, dmg_die=6, dmg_bonus=0, dmg_type = 'piercing', to_hit=2, challenge_rating=0.25)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'r', 'swarm of rats', 'brown', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE243", 16)
	monster.small_char = int("0xE743", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_swarm_of_ravens(x, y):
	fighter_component = Fighter(hp=24, strength=6, dexterity=14, constitution=8, intelligence=3, wisdom=12, charisma=6, clevel=1, proficiencies=[], traits=['flying'], spells=[], xp=50, death_function=monster_death, ac=12, num_dmg_die=2, dmg_die=6, dmg_bonus=0, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'swarm of ravens', 'dark grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE244", 16)
	monster.small_char = int("0xE744", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_tiger(x, y):
	fighter_component = Fighter(hp=37, strength=17, dexterity=15, constitution=14, intelligence=3, wisdom=12, charisma=8, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=200, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=10, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=1)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'c', 'tiger', 'dark orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE245", 16)
	monster.small_char = int("0xE745", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_triceratops(x, y):
	fighter_component = Fighter(hp=95, strength=22, dexterity=9, constitution=17, intelligence=2, wisdom=11, charisma=5, clevel=1, proficiencies=[], traits=[], spells=[], xp=1800, death_function=monster_death, ac=13, num_dmg_die=4, dmg_die=8, dmg_bonus=6, dmg_type = 'piercing', to_hit=9, challenge_rating=5)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'triceratops', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE246", 16)
	monster.small_char = int("0xE746", 16)
	monster.move_cost = 60
	monster.description = 'One of the most aggressive of the herbivorous dinosaurs, a triceratops possesses great horns and formidable speed, which it uses to gore and trample would-be predators to death.'
	return monster
	
def create_troll(x, y):
	fighter_component = Fighter(hp=84, strength=18, dexterity=13, constitution=20, intelligence=7, wisdom=9, charisma=7, clevel=1, proficiencies=['perception'], traits=['darkvision'], spells=[], xp=1800, death_function=monster_death, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=4, dmg_type = 'piercing', to_hit=7, challenge_rating=5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'T', 'troll', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE247", 16)
	monster.small_char = int("0xE747", 16)
	monster.move_cost = 100
	monster.description = "Fearsome green-skinned giants, trolls eat anything they can catch and devour. Only acid and fire can arrest the regenerative properties of a troll's flesh."
	return monster
	
def create_twig_blight(x, y):
	fighter_component = Fighter(hp=4, strength=6, dexterity=13, constitution=12, intelligence=4, wisdom=8, charisma=3, clevel=1, proficiencies=[], traits=['blindsight'], spells=[], xp=25, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=4, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.125)	
	ai_component = BasicMonster()
	monster = Object(x, y, 't', 'twig blight', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE248", 16)
	monster.small_char = int("0xE748", 16)
	monster.move_cost = 150
	monster.description = 'A twig blight is an awakened plant that resembles a woody shrub that can pull its roots free of the ground. Its branches twist together to form a humanoid-looking body with a head and limbs.'
	return monster
	
def create_tyrannosaurus_rex(x, y):
	fighter_component = Fighter(hp=136, strength=25, dexterity=10, constitution=19, intelligence=2, wisdom=12, charisma=9, clevel=1, proficiencies=[], traits=['extra attack'], spells=[], xp=3900, death_function=monster_death, ac=13, num_dmg_die=4, dmg_die=12, dmg_bonus=7, dmg_type = 'piercing', to_hit=10, challenge_rating=8)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'tyrannosaurus rex', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE249", 16)
	monster.small_char = int("0xE749", 16)
	monster.move_cost = 60
	monster.description = 'This enormous predatory dinosaur terrorizes all other creatures in its territory. It chases anything it thinks it can eat, and there are few creatures it won’t try to devour whole.'
	return monster
	
def create_vulture(x, y):
	fighter_component = Fighter(hp=5, strength=7, dexterity=10, constitution=13, intelligence=2, wisdom=12, charisma=4, clevel=1, proficiencies=['perception'], traits=['flying', 'pack tactics'], spells=[], xp=10, death_function=monster_death, ac=10, num_dmg_die=1, dmg_die=4, dmg_bonus=0, dmg_type = 'piercing', to_hit=2, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'B', 'vulture', 'darker red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE250", 16)
	monster.small_char = int("0xE750", 16)
	monster.move_cost = 60
	#monster.description = ''
	return monster
	
def create_warhorse(x, y):
	fighter_component = Fighter(hp=19, strength=18, dexterity=12, constitution=13, intelligence=2, wisdom=12, charisma=7, clevel=1, proficiencies=[], traits=[], spells=[], xp=100, death_function=monster_death, ac=11, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=6, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'q', 'warhorse', 'brass', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE251", 16)
	monster.small_char = int("0xE751", 16)
	monster.move_cost = 50
	#monster.description = ''
	return monster
	
def create_water_elemental(x, y):
	fighter_component = Fighter(hp=114, strength=18, dexterity=14, constitution=18, intelligence=5, wisdom=10, charisma=8, clevel=1, proficiencies=[], traits=['poison immune', 'extra attack'], spells=[], xp=1800, death_function=monster_death, ac=14, num_dmg_die=2, dmg_die=8, dmg_bonus=4, dmg_type = 'bludgeoning', to_hit=7, challenge_rating=5)	 
	ai_component = BasicMonster()
	monster = Object(x, y, 'E', 'water elemental', 'blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE252", 16)
	monster.small_char = int("0xE752", 16)
	monster.move_cost = 100
	monster.description = 'Beings native to the Elemental Plane of Water and summoned to the world, water elementals resemble cresting waves that roll across the ground. A water elemental engulfs any creatures that stand against it.'
	return monster
	
def create_weasel(x, y):
	fighter_component = Fighter(hp=1, strength=3, dexterity=16, constitution=8, intelligence=2, wisdom=12, charisma=3, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=10, death_function=monster_death, ac=13, num_dmg_die=1, dmg_die=1, dmg_bonus=0, dmg_type = 'piercing', to_hit=5, challenge_rating=0)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'r', 'weasel', 'darker amber', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE253", 16)
	monster.small_char = int("0xE753", 16)
	monster.move_cost = 100
	#monster.description = ''
	return monster
	
def create_werewolf(x, y):
	fighter_component = Fighter(hp=58, strength=15, dexterity=13, constitution=14, intelligence=10, wisdom=11, charisma=10, clevel=1, proficiencies=['perception'], traits=['extra attack'], spells=[], xp=700, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=8, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'werewolf', 'dark red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE254", 16)
	monster.small_char = int("0xE754", 16)
	monster.move_cost = 75
	monster.description = "A werewolf is a savage predator that can appear as a humanoid, as a wolf, or in a terrifying hybrid form — a furred and well-muscled humanoid body topped by a ravening wolf's head."
	return monster
	
def create_wight(x, y):
	fighter_component = Fighter(hp=45, strength=15, dexterity=14, constitution=16, intelligence=10, wisdom=13, charisma=15, clevel=1, proficiencies=[], traits=['extra attack', 'darkvision', 'poison immune', 'undead'], spells=[], xp=700, death_function=monster_death, ac=14, num_dmg_die=1, dmg_die=8, dmg_bonus=2, dmg_type = 'slashing', to_hit=4, challenge_rating=3) 
	ai_component = BasicMonster()
	monster = Object(x, y, 'W', 'wight', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE255", 16)
	monster.small_char = int("0xE755", 16)
	monster.move_cost = 100
	monster.description = 'Wights are intelligent undead humanoids that resemble armed and armored corpses. They never tire in pursuit of their goal of making eternal war against the living.'
	return monster
	
def create_winter_wolf(x, y):
	fighter_component = Fighter(hp=75, strength=18, dexterity=13, constitution=14, intelligence=7, wisdom=12, charisma=8, clevel=1, proficiencies=['perception'], traits=['cold immune', 'pack tactics'], spells=[], xp=700, death_function=monster_death, ac=13, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'piercing', to_hit=6, challenge_rating=3)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'winter wolf', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE256", 16)
	monster.small_char = int("0xE756", 16)
	monster.move_cost = 60
	monster.description = 'Arctic-dwelling winter wolves are evil and intelligent creatures with snow-white fur and pale blue eyes.'
	return monster
	
def create_wolf(x, y):
	fighter_component = Fighter(hp=11, strength=12, dexterity=15, constitution=12, intelligence=3, wisdom=12, charisma=6, clevel=1, proficiencies=['perception'], traits=['pack tactics'], spells=[], xp=50, death_function=monster_death, ac=13, num_dmg_die=2, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.25)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'wolf', 'brown', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE257", 16)
	monster.small_char = int("0xE757", 16)
	monster.move_cost = 75
	#monster.description = ''
	return monster
	
def create_worg(x, y):
	fighter_component = Fighter(hp=26, strength=16, dexterity=13, constitution=13, intelligence=7, wisdom=11, charisma=8, clevel=1, proficiencies=['perception'], traits=[], spells=[], xp=100, death_function=monster_death, ac=13, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'piercing', to_hit=5, challenge_rating=0.5)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'd', 'worg', 'dark red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE258", 16)
	monster.small_char = int("0xE758", 16)
	monster.move_cost = 60
	monster.description = 'A worg is a monstrous wolf-like predator that delights in hunting and devouring creatures weaker than itself.'
	return monster
	
def create_wyvern(x, y):
	fighter_component = Fighter(hp=110, strength=19, dexterity=10, constitution=16, intelligence=5, wisdom=12, charisma=6, clevel=1, proficiencies=[], traits=['darkvision', 'extra attack'], spells=[], xp=2300, death_function=monster_death, ac=13, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'piercing', to_hit=7, challenge_rating=6)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'wyvern', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE259", 16)
	monster.small_char = int("0xE759", 16)
	monster.move_cost = 150
	monster.description = 'Cousins to the great dragons, wyverns have two scaly legs, leathery wings, and a sinewy tail topped with a poison stinger that can kill a creature in seconds.'
	return monster
	
def create_yeti(x, y):
	fighter_component = Fighter(hp=51, strength=18, dexterity=13, constitution=16, intelligence=8, wisdom=12, charisma=7, clevel=1, proficiencies=['perception'], traits=['cold immune', 'extra attack'], spells=[], xp=700, death_function=monster_death, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=4, dmg_type = 'slashing', to_hit=6, challenge_rating=3)  
	ai_component = BasicMonster()
	monster = Object(x, y, 'H', 'yeti', 'white', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE260", 16)
	monster.small_char = int("0xE760", 16)
	monster.move_cost = 75
	monster.description = 'Yeti are hulking monstrosities that stalk alpine peaks in a ceaseless hunt for food. Their snow-white fur lets them move like ghosts against the frozen landscape.'
	return monster
	
def create_young_green_dragon(x, y):
	fighter_component = Fighter(hp=136, strength=19, dexterity=12, constitution=17, intelligence=16, wisdom=13, charisma=15, clevel=1, proficiencies=[], traits=['darkvision', 'extra attack', 'poison immune'], spells=[], xp=3900, death_function=monster_death, ac=18, num_dmg_die=2, dmg_die=10, dmg_bonus=4, dmg_type = 'piercing', to_hit=7, challenge_rating=8)	
	ai_component = BasicMonster()
	monster = Object(x, y, 'D', 'young green dragon', 'green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE261", 16)
	monster.small_char = int("0xE761", 16)
	monster.move_cost = 75
	monster.description = 'The most cunning and treacherous of true dragons, green dragons use misdirection and trickery to get the upper hand against their enemies. A green dragon is recognized by the crest that begins near its eyes and continues down its spine, reaching full height just behind the skull.'
	return monster
	
def create_zombie(x, y):
	fighter_component = Fighter(hp=22, strength=13, dexterity=6, constitution=16, intelligence=3, wisdom=6, charisma=5, clevel=1, proficiencies=[], traits=['fortitude', 'poison immune', 'undead'], spells=[], xp=50, death_function=monster_death, ac=8, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'bludgeoning', to_hit=3, challenge_rating=0.25) 
	ai_component = BasicMonster()
	monster = Object(x, y, 'Z', 'zombie', 'light green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.big_char = int("0xE262", 16)
	monster.small_char = int("0xE762", 16)
	monster.move_cost = 150
	monster.description = 'Undead zombies move with a jerky, uneven gait. They are clad in the moldering apparel they wore when put to rest, and carry the stench of decay.'
	return monster
	
###
### NPC GENERATION FUNCTIONS
###
	
def create_acolyte(x, y):
	fighter_component = Fighter(hp=9, strength=10, dexterity=10, constitution=10, intelligence=10, wisdom=14, charisma=11, clevel=1, proficiencies=['magic', 'simple weapons', 'light armour'], traits=[], spells=['sacred flame', 'bless', 'cure wounds'], xp=50, death_function=monster_ko, ac=10, num_dmg_die=1, dmg_die=4, dmg_bonus=0, dmg_type = 'bludgeoning', to_hit=2, challenge_rating=0.25, casting_stat = 'wisdom', natural_weapon='Club')	
	ai_component = MagicMonster()
	monster = Object(x, y, '@', 'acolyte', 'red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.fighter.magic = True
	monster.big_char = int("0xE263", 16)
	monster.small_char = int("0xE763", 16)
	monster.flavour_text = ["Through patience and dedication, my power grows."]
	monster.description = 'Acolytes are junior members of a clergy, usually answerable to a priest. They perform a variety of functions in a temple and are granted minor spellcasting power by their deities.'
	monster.value = 100
	return monster
	
def create_archmage(x, y):
	fighter_component = Fighter(hp=99, strength=10, dexterity=14, constitution=12, intelligence=20, wisdom=15, charisma=16, clevel=18, proficiencies=['magic', 'simple weapons', 'light armour'], traits=['magic resistance', 'damage resistance'], spells=['fire bolt', 'shocking grasp', 'mage armour', 'magic missile', 'shield', 'lightning bolt', 'banishment', 'fire shield', 'stoneskin', 'cone of cold', 'teleport'], xp=8400, death_function=monster_ko, ac=12, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=6, challenge_rating=12, natural_weapon='Dagger')	
	ai_component = MagicMonster()
	monster = Object(x, y, '@', 'archmage', 'crimson', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.fighter.magic = True
	monster.big_char = int("0xE264", 16)
	monster.small_char = int("0xE764", 16)
	monster.flavour_text = ["The mysteries of the arcane are mine to know."]
	monster.description = 'Archmages are powerful (and usually quite old) spellcasters dedicated to the study of the arcane arts. Benevolent ones counsel kings and queens, while evil ones rule as tyrants and pursue lichdom. Those who are neither good nor evil sequester themselves in remote towers to practice their magic without interruption.'
	monster.value = 10000
	return monster
	
def create_assassin(x, y):
	fighter_component = Fighter(hp=78, strength=11, dexterity=16, constitution=14, intelligence=13, wisdom=11, charisma=10, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour'], traits=['sneak attack', 'assassinate', 'extra attack'], spells=[], xp=3900, death_function=monster_ko, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=3, dmg_type = 'piercing', to_hit=6, challenge_rating=8, natural_weapon='Short sword')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'assassin', 'dark grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE265", 16)
	monster.small_char = int("0xE765", 16)
	monster.flavour_text = ["Do not come too close unless you seek to taste my blade."]
	monster.description = 'Trained in the use of poison, assassins are remorseless killers who work for nobles, guildmasters, sovereigns, and anyone else who can afford them.'
	monster.value = 1000
	return monster
	
def create_bandit(x, y):
	fighter_component = Fighter(hp=11, strength=11, dexterity=12, constitution=12, intelligence=10, wisdom=10, charisma=10, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour', 'medium armour'], traits=[], spells=[], xp=25, death_function=monster_ko, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'slashing', to_hit=3, ranged_num_dmg_die=1, ranged_dmg_die=6, ranged_dmg_bonus=3, ranged_dmg_type='piercing', ranged_to_hit=5, challenge_rating=0.125, natural_weapon='Scimitar')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'bandit', 'dark yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE266", 16)
	monster.small_char = int("0xE766", 16)
	monster.flavour_text = ["What's that you've got in your pack?"]
	monster.description = 'Bandits rove in gangs and are sometimes led by more powerful NPCs, including spellcasters. Not all bandits are evil. Oppression, drought, disease, or famine can often drive otherwise honest folk to a life of banditry.'
	monster.value = 250
	return monster
	
def create_bandit_captain(x, y):
	fighter_component = Fighter(hp=65, strength=15, dexterity=16, constitution=14, intelligence=14, wisdom=11, charisma=14, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour', 'medium armour', 'heavy armour', 'shields'], traits=['extra attack'], spells=[], xp=450, death_function=monster_ko, ac=15, num_dmg_die=1, dmg_die=6, dmg_bonus=3, dmg_type = 'slashing', to_hit=5, challenge_rating=2, natural_weapon='Scimitar')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'bandit captain', 'gold', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE267", 16)
	monster.small_char = int("0xE767", 16)
	monster.flavour_text = ["If you don't want trouble then you'll stay out of our way."]
	monster.description = 'It takes a strong personality, ruthless cunning, and a silver tongue to keep a gang of bandits in line. The bandit captain has these qualities in spades.'
	monster.value = 750
	return monster
	
def create_berserker(x, y):
	fighter_component = Fighter(hp=67, strength=16, dexterity=12, constitution=17, intelligence=9, wisdom=11, charisma=9, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour', 'medium armour', 'heavy armour'], traits=['reckless'], spells=[], xp=450, death_function=monster_ko, ac=13, num_dmg_die=1, dmg_die=12, dmg_bonus=3, dmg_type = 'slashing', to_hit=5, challenge_rating=2, natural_weapon='Great axe')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'berserker', 'orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE268", 16)
	monster.small_char = int("0xE768", 16)
	monster.flavour_text = ["It has been far too long since the battle lust has consumed me."]
	monster.description = 'Hailing from uncivilized lands, unpredictable berserkers come together in war parties and seek conflict wherever they can find it.'
	monster.value = 450
	return monster
	
def create_commoner(x, y):
	fighter_component = Fighter(hp=4, strength=10, dexterity=10, constitution=10, intelligence=10, wisdom=10, charisma=10, clevel=1, proficiencies=['simple weapons'], traits=[], spells=[], xp=10, death_function=monster_ko, ac=10, num_dmg_die=1, dmg_die=4, dmg_bonus=0, dmg_type = 'bludgeoning', to_hit=2, challenge_rating=0, natural_weapon='Club')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'commoner', 'silver', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE269", 16)
	monster.small_char = int("0xE769", 16)
	monster.flavour_text = ["Good day sir, I'll just be on my way if that's alright by you."]
	monster.description = 'Commoners include peasants, serfs, slaves, servants, pilgrims, merchants, artisans, and hermits.'
	monster.value = 10
	return monster
	
def create_cultist(x, y):
	fighter_component = Fighter(hp=9, strength=11, dexterity=12, constitution=10, intelligence=10, wisdom=11, charisma=10, clevel=1, proficiencies=['simple weapons', 'light armour'], traits=[], spells=[], xp=25, death_function=monster_ko, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'slashing', to_hit=3, challenge_rating=0.125, natural_weapon='Scimitar')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'cultist', 'dark grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE270", 16)
	monster.small_char = int("0xE770", 16)
	monster.flavour_text = ["The whispers from the shadows haunt my dreams."]
	monster.description = 'Cultists swear allegiance to dark powers, and often show signs of insanity in their beliefs and practices.'
	monster.value = 100
	return monster
	
def create_cult_fanatic(x, y):
	fighter_component = Fighter(hp=33, strength=11, dexterity=14, constitution=12, intelligence=10, wisdom=13, charisma=14, clevel=4, proficiencies=['magic', 'simple weapons', 'light armour'], traits=['extra attack'], spells=['sacred flame', 'inflict wounds', 'shield of faith', 'hold person', 'spiritual weapon'], xp=450, death_function=monster_ko, ac=13, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=2, natural_weapon='Dagger')	
	ai_component = MagicMonster()
	monster = Object(x, y, '@', 'cult fanatic', 'darker orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.fighter.magic = True
	monster.big_char = int("0xE271", 16)
	monster.small_char = int("0xE771", 16)
	monster.flavour_text = ["You have no idea about the glorious dark things that I have seen."]
	monster.description = "Fanatics are often part of a cult's leadership, using their charisma and dogma to influence and prey on those of weak will. Most are interested in personal power above all else."
	monster.value = 500
	return monster
	
def create_gladiator(x, y):
	fighter_component = Fighter(hp=112, strength=18, dexterity=15, constitution=16, intelligence=10, wisdom=12, charisma=15, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour', 'medium armour', 'heavy armour', 'shields'], traits=['extra attack', 'extra attack', 'brave'], spells=[], xp=1800, death_function=monster_ko, ac=16, num_dmg_die=2, dmg_die=6, dmg_bonus=4, dmg_type = 'piercing', to_hit=7, challenge_rating=5, natural_weapon='Spear')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'gladiator', 'dark orange', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE272", 16)
	monster.small_char = int("0xE772", 16)
	monster.flavour_text = ["I have won many battles against greater odds than this."]
	monster.description = 'Gladiators battle for the entertainment of raucous crowds. Some gladiators are brutal pit fighters who treat each match as a life-or-death struggle, while others are professional duelists who command huge fees but rarely fight to the death.'
	monster.value = 2500
	return monster	
	
def create_guard(x, y):
	fighter_component = Fighter(hp=11, strength=13, dexterity=12, constitution=12, intelligence=10, wisdom=11, charisma=10, clevel=1, proficiencies=['perception', 'protection without shield', 'simple weapons', 'martial weapons', 'light armour', 'medium armour', 'heavy armour', 'shields'], traits=[], spells=[], xp=25, death_function=monster_ko, ac=16, num_dmg_die=1, dmg_die=6, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.125, natural_weapon='Spear')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'guard', 'yellow', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE273", 16)
	monster.small_char = int("0xE773", 16)
	monster.flavour_text = ["Through the strength of my arms, I dedicate myself to keeping those safe around me."]
	monster.description = 'Guards include members of a city watch, sentries in a citadel or fortified town, and the bodyguards of merchants and nobles.'
	monster.value = 150
	return monster
	
def create_knight(x, y):
	fighter_component = Fighter(hp=52, strength=16, dexterity=11, constitution=14, intelligence=11, wisdom=11, charisma=15, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour', 'medium armour', 'heavy armour', 'shields'], traits=['brave'], spells=[], xp=700, death_function=monster_ko, ac=18, num_dmg_die=2, dmg_die=6, dmg_bonus=3, dmg_type = 'slashing', to_hit=5, challenge_rating=3, natural_weapon='Greatsword')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'knight', 'sky', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE274", 16)
	monster.small_char = int("0xE774", 16)
	monster.flavour_text = ["It takes much more than being able to swing a sword to become a knight."]
	monster.description = "Knights are warriors who pledge service to rulers, religious orders, and noble causes. A knight's alignment determines the extent to which a pledge is honoured."
	monster.value = 1250
	return monster
	
def create_mage(x, y):
	fighter_component = Fighter(hp=40, strength=9, dexterity=14, constitution=11, intelligence=17, wisdom=12, charisma=11, clevel=9, proficiencies=['magic', 'simple weapons', 'light armour'], traits=[], spells=['fire bolt', 'magic missile', 'shield', 'fireball', 'ice storm', 'cone of cold'], xp=2300, death_function=monster_ko, ac=12, num_dmg_die=1, dmg_die=4, dmg_bonus=2, dmg_type = 'piercing', to_hit=5, challenge_rating=6, natural_weapon='Dagger')	
	ai_component = MagicMonster()
	monster = Object(x, y, '@', 'mage', 'fuchsia', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.fighter.magic = True
	monster.big_char = int("0xE275", 16)
	monster.small_char = int("0xE775", 16)
	monster.flavour_text = ["My studies of the mysteries of the arcane have granted me great power."]
	monster.description = 'Mages spend their lives in the study and practice of magic.'
	monster.value = 5000
	return monster
	
def create_noble(x, y):
	fighter_component = Fighter(hp=9, strength=11, dexterity=12, constitution=11, intelligence=12, wisdom=14, charisma=16, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour'], traits=[], spells=[], xp=25, death_function=monster_ko, ac=15, num_dmg_die=1, dmg_die=8, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.125, natural_weapon='Rapier')
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'noble', 'light green', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE276", 16)
	monster.small_char = int("0xE776", 16)
	monster.flavour_text = ["I have little time for the likes of you."]
	monster.description = 'Nobles wield great authority and influence as members of the upper class, possessing wealth and connections that can make them as powerful as monarchs and generals. A noble often travels in the company of guards, as well as servants who are commoners.'
	monster.value = 50000
	return monster
	
def create_priest(x, y):
	fighter_component = Fighter(hp=27, strength=10, dexterity=10, constitution=12, intelligence=13, wisdom=16, charisma=13, clevel=5, proficiencies=['magic', 'simple weapons', 'light armour', 'medium armour'], traits=[], spells=['sacred flame', 'cure wounds', 'lesser restoration', 'spiritual weapon', 'dispel magic', 'spirit guardians'], xp=450, death_function=monster_ko, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=0, dmg_type = 'bludgeoning', to_hit=2, challenge_rating=2, natural_weapon='Mace')	
	ai_component = MagicMonster()
	monster = Object(x, y, '@', 'priest', 'blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.fighter.magic = True
	monster.big_char = int("0xE277", 16)
	monster.small_char = int("0xE777", 16)
	monster.flavour_text = ["True wisdom comes from contemplation, meditation and prayer."]
	monster.description = 'Priests are the spiritual leaders of temples and shrines.'
	monster.value = 4000
	return monster
	
def create_scout(x, y):
	fighter_component = Fighter(hp=16, strength=11, dexterity=14, constitution=12, intelligence=11, wisdom=13, charisma=11, clevel=1, proficiencies=['perception', 'simple weapons', 'martial weapons', 'light armour'], traits=['extra attack'], spells=[], xp=100, death_function=monster_ko, ac=13, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=4, challenge_rating=0.5, natural_weapon='Short sword')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'scout', 'celadon', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE278", 16)
	monster.small_char = int("0xE778", 16)
	monster.flavour_text = ["I could hear you coming a mile away."]
	monster.description = 'Scouts are skilled hunters and trackers who offer their services for a fee. Most hunt wild game, but a few work as bounty hunters, serve as guides, or provide military reconnaissance.'
	monster.value = 250
	return monster
	
def create_spy(x, y):
	fighter_component = Fighter(hp=27, strength=10, dexterity=15, constitution=10, intelligence=12, wisdom=14, charisma=16, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour'], traits=['sneak attack', 'extra attack'], spells=[], xp=200, death_function=monster_ko, ac=12, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'piercing', to_hit=5, challenge_rating=1, natural_weapon='Short sword')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'spy', 'dark grey', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE279", 16)
	monster.small_char = int("0xE779", 16)
	monster.flavour_text = ["The best way to gain influence in this world is through intelligence and cunning."]
	monster.description = 'Rulers, nobles, merchants, guildmasters, and other wealthy individuals use spies to gain the upper hand in a world of cutthroat politics. A spy is trained to secretly gather information. Loyal spies would rather die than divulge information that could compromise them or their employers.'
	monster.value = 750
	return monster
	
def create_thug(x, y):
	fighter_component = Fighter(hp=32, strength=15, dexterity=11, constitution=14, intelligence=10, wisdom=10, charisma=11, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour', 'medium armour'], traits=['pack tactics', 'sneak attack'], spells=[], xp=100, death_function=monster_ko, ac=11, num_dmg_die=1, dmg_die=6, dmg_bonus=2, dmg_type = 'bludgeoning', to_hit=4, challenge_rating=0.5, natural_weapon='Thug')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'thug', 'dark red', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE280", 16)
	monster.small_char = int("0xE780", 16)
	monster.flavour_text = ["If you want anything for yourself in this world, then you've just got to take it."]
	monster.description = 'Thugs are ruthless enforcers skilled at intimidation and violence. They work for money and have few scruples.'
	monster.value = 350
	return monster
	
def create_tribal_warrior(x, y):
	fighter_component = Fighter(hp=11, strength=13, dexterity=11, constitution=12, intelligence=8, wisdom=11, charisma=8, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour', 'medium armour', 'heavy armour', 'shields'], traits=['pack tactics'], spells=[], xp=25, death_function=monster_ko, ac=12, num_dmg_die=1, dmg_die=8, dmg_bonus=1, dmg_type = 'piercing', to_hit=3, challenge_rating=0.5, natural_weapon='Spear')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'tribal warrior', 'flame', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE281", 16)
	monster.small_char = int("0xE781", 16)
	monster.flavour_text = ["To battle and die alongside my tribe is the highest honour of all."]
	monster.description = 'Tribal warriors live beyond civilization, most often subsisting on fishing and hunting. Each tribe acts in accordance with the wishes of its chief, who is the greatest or oldest warrior of the tribe or a tribe member blessed by the gods.'
	monster.value = 200
	return monster
	
def create_veteran(x, y):
	fighter_component = Fighter(hp=58, strength=16, dexterity=13, constitution=14, intelligence=10, wisdom=11, charisma=10, clevel=1, proficiencies=['simple weapons', 'martial weapons', 'light armour', 'medium armour', 'heavy armour', 'shields'], traits=['extra attack'], spells=[], xp=700, death_function=monster_ko, ac=17, num_dmg_die=1, dmg_die=8, dmg_bonus=3, dmg_type = 'slashing', to_hit=5, challenge_rating=3, natural_weapon='Longsword')	
	ai_component = BasicMonster()
	monster = Object(x, y, '@', 'veteran', 'light blue', blocks=True, fighter=fighter_component, ai=ai_component)
	monster.fighter.can_join = True
	monster.big_char = int("0xE282", 16)
	monster.small_char = int("0xE782", 16)
	monster.flavour_text = ["I have forgotten more battles than you've ever seen."]
	monster.description = 'Veterans are professional fighters that take up arms for pay or to protect something they believe in or value. Their ranks include soldiers retired from long service and warriors who never served anyone but themselves.'
	monster.value = 600
	return monster
	
###
### UNIQUE NPC GENERATION FUNCTIONS
###

def create_odette(x, y):
	monster = create_priest(x, y)
	monster.big_char = int("0xE263", 16)
	monster.small_char = int("0xE763", 16)
	monster.name = 'Odette'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["Welcome to North Warren traveller, you are safe here.", "The kobolds hide in the warrens nearby and have done so for generations.", "We have lost more good people to the kobolds than I care to remember.", "The kobolds would not dare to venture as far as North Warren but they plague my people nonetheless.", "We have sent for aid from Mirefield Keep but we are still waiting for a response."]
	return monster
	
def create_sunny(x, y):
	monster = create_mastiff(x, y)
	monster.name = 'Sunny'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.chatty = True
	monster.fighter.xp = -250
	monster.flavour_text = ['Woof!', 'Awooo!']
	return monster
	
def create_susie(x, y):
	monster = create_mastiff(x, y)
	monster.name = 'Susie'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.chatty = True
	monster.fighter.xp = -250
	monster.flavour_text = ['Woof!', 'Awooo!']
	return monster
	
def create_momo(x, y):
	monster = create_cat(x, y)
	monster.name = 'Momo'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.chatty = True
	monster.fighter.xp = -250
	monster.flavour_text = ['Meow.']
	return monster
	
def create_lord_wesley(x, y):
	monster = create_noble(x, y)
	monster.name = 'Lord Wesley'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["I appreciate you calling upon me but I have much better things to be doing.", "Please entertain yourselves, I have pressing matters of state to attend to.", "I am surrounded by incompetency; my kingdom for a sensible adviser!", "I could purge the Badbog with my own two hands if I only had the time.", "Even the brutes of Rage Hill are wise enough to fear my skill with the blade.", "I tire of feast after feast; I yearn for adventure!", "I have half a mind to take a few loyal men and personally put an end to those miserable bandits.", "My blade has brought an early death to all manner of goblinkin, orcs, ogres and even a dragon; I could teach you a thing or two."]
	return monster
	
def create_lady_cindemere(x, y):
	monster = create_archmage(x, y)
	monster.name = 'Lady Cindemere'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["We have heard all sorts of rumours of terrible beasts coming from the mountains to the south-east.", "We are doing what we can to quell the savages of Rage Hill, but we have enemies on all sides.", "We do what we must to ensure Cindemere's prominence.", "We have felt a disturbance in recent months; this region was previously serene and prosperous, but now we see danger everywhere we look.", "We are always recruiting new troops; we must have the strength of arms necessary to take back Vierfort.", "That fool Wesley at Mirefield would not last a single day outside of his walls."]
	return monster
	
def create_saint_barnabas(x, y):
	monster = create_veteran(x, y)
	monster.big_char = int("0xE277", 16) #make him look like a priest
	monster.small_char = int("0xE777", 16)
	monster.name = 'Saint Barnabas'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["We can not blame those who fail to see the truth! Our doom could not be foreseen but we still have hope!", "You must listen to me! It is only by swearing an oath of abstinence that we may have salvation!", "I care not about the sins of the flesh; it is the corrupting power of the healers who betray us!", "The path to salvation is a difficult one; listen to me and I will teach you the way, my children.", "Those among us who call upon the Gods for aid today are dooming us tomorrow! You must resist that temptation!", "This place was once a blessed and shining tribute to the Gods; we have lost our way and it has lost its glory.", "Please, I beg of you; abstain from your healing magics! They may seem like a boon from the False Gods but their taint grows within us!"]
	return monster
	
def create_saint_othmar(x, y):
	monster = create_veteran(x, y)
	monster.big_char = int("0xE277", 16) #make him look like a priest
	monster.small_char = int("0xE777", 16)
	monster.name = 'Saint Othmar'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["We can not blame those who fail to see the truth! Our doom could not be foreseen but we still have hope!", "You must listen to me! It is only by swearing an oath of abstinence that we may have salvation!", "I care not about the sins of the flesh; it is the corrupting power of the healers who betray us!", "The path to salvation is a difficult one; listen to me and I will teach you the way, my children.", "Those among us who call upon the Gods for aid today are dooming us tomorrow! You must resist that temptation!", "This place was once a blessed and shining tribute to the Gods; we have lost our way and it has lost its glory.", "Please, I beg of you; abstain from your healing magics! They may seem like a boon from the False Gods but their taint grows within us!"]
	return monster
	
def create_saint_hedwig(x, y):
	monster = create_veteran(x, y)
	monster.big_char = int("0xE277", 16) #make him look like a priest
	monster.small_char = int("0xE777", 16)
	monster.name = 'Saint Hedwig'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.can_join = False
	monster.fighter.true_faction = 'neutral'
	monster.chatty = True
	monster.flavour_text = ["We can not blame those who fail to see the truth! Our doom could not be foreseen but we still have hope!", "You must listen to me! It is only by swearing an oath of abstinence that we may have salvation!", "I care not about the sins of the flesh; it is the corrupting power of the healers who betray us!", "The path to salvation is a difficult one; listen to me and I will teach you the way, my children.", "Those among us who call upon the Gods for aid today are dooming us tomorrow! You must resist that temptation!", "This place was once a blessed and shining tribute to the Gods; we have lost our way and it has lost its glory.", "Please, I beg of you; abstain from your healing magics! They may seem like a boon from the False Gods but their taint grows within us!"]
	return monster
	
def create_cardinal_florian(x, y):
	monster = create_noble(x, y)
	monster.big_char = int("0xE264", 16)
	monster.small_char = int("0xE764", 16) #make him look like an archmage
	monster.name = 'Cardinal Florian'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["The Church of Black Hollow's doors are always open to pilgrims seeking wisdom.", "You are welcome within this place but you must follow our Order's teachings if you seek sanctuary.", "Saint Peregrine's Order has worked tirelessly for generations to cleanse the world of the taint of the False Gods; you would be wise to heed our Teachings.", "Each time a False Cleric uses their tainted powers to heal, the sickness spreads further; our Lord teaches that there is another way!", "Cast aside the vestments of the False Gods; their Word is hollow and evil at its core!", "I understand the temptation to seek the aid of the False Gods; their power is obvious but the true cost is not.", "Our Lord has a Path for all of us; it may seem cruel to ignore the pleas of the sick and dying, but the price of doing anything else is to doom us all!"]
	return monster
	
def create_aoife(x, y):
	monster = create_archmage(x, y)
	monster.name = 'Aoife'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["You are not welcome here; your destruction is assured.", "Your presence in these halls is an insult: begone!", "My minions surround you as we speak; surrender now and I will grant you a quick death.", "My power grows day by day and I will not allow a miscreant like you to distract me from my plans."]
	return monster
	
def create_nubnag(x, y):
	monster = create_kobold(x, y)
	monster.name = 'Nubnag'
	monster.unique = True
	monster.proper_noun = True
	monster.chatty = True
	monster.colour = 'red'
	monster.char = 'K'
	monster.fighter.xp = 100
	monster.fighter.max_hp = 50
	monster.fighter.hp = 50
	monster.fighter.strength = 18
	monster.fighter.constitution = 18
	monster.fighter.dmg_die = 8
	monster.fighter.traits.append('relentless')
	monster.fighter.traits.append('extra attack')
	monster.fighter.traits.append('savage')
	monster.flavour_text = ["Si geou sone dout yobolat ghoros nomeno kear ui ekik!", "Nomenoi re Nubnag ui ulph waereic vur shio intruders zklaen loreat!", "Wux tepoha authot vin phlita sin ini confnir ekess nomeno goawy!", "Nubnag rules this goawy!"]
	return monster
	
def create_saint_cormag(x, y):
	monster = create_priest(x, y)
	monster.big_char = int("0xE275", 16) #make him look like a mage
	monster.small_char = int("0xE775", 16)
	monster.name = 'Saint Cormag'
	monster.unique = True
	monster.proper_noun = True
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["Necromancy is not what you think, it is only the short-sighted that can not understand what I do.", "You have the chance to stand by my side forever; what greater boon could there be.", "There are many who desire everlasting life, and it is my plan to give it to those who desire it.", "It would be wise to submit without a fight; you will carry these ugly wounds for all eternity.", "I still follow the word of Saint Peregrine; it is only through necromancy that you can be healed without doing harm to others.", "I know that you think my path is an evil one but this is the only way to stay true to Saint Peregrine.", "Those fools in the Order of Saint Peregrine know the truth but lack the courage to follow me."]
	return monster
	
###
### NPC MERCHANT GENERATION FUNCTIONS
###

def create_merchant(x, y):
	monster = create_noble(x, y)
	monster.name = 'Merchant'
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["Nothing but the finest goods!", "Braised oxen! Steamed slime mold! Fried shrieker!", "Rations for sale! We've got the best pies this side of Beggar's Hole!", "Special prices for adventurers! Rations guaranteed to keep you going on even the longest journeys!", "Cheerio!"]
	monster.merchant = True
	monster.inventory.append(create_food_rations(random.randint(3, 5)))
	monster.inventory.append(create_bullets(random.randint(12, 25)))
	monster.inventory.append(create_arrows(random.randint(10, 15)))
	monster.inventory.append(create_bolts(random.randint(8, 12)))
	monster.inventory.append(create_dart(random.randint(5, 7)))
	for i in range(random.randint(3, 5)):
		func = random.choice(weapon_func_list)
		monster.inventory.append(func())
	for i in range(random.randint(1, 3)):
		func = random.choice(armour_func_list)
		monster.inventory.append(func())
	func = random.choice(common_magic_func_list)
	monster.inventory.append(func())
	merge_items_in_inventory(monster)
	### create follower to guard merchant in case of player aggression
	(follower_x, follower_y) = random_unblocked_spot_near(x, y)
	follower = create_gladiator(follower_x, follower_y)
	follower.name = 'bodyguard'
	follower.fighter.faction = 'neutral'
	follower.fighter.true_faction = 'neutral'
	follower_ai_component = CompanionMonster(monster, 2)
	follower_ai_component.owner = follower
	follower.ai = follower_ai_component
	follower.fighter.can_join = False
	monster.followers.append(follower)
	actors.append(follower)
	return monster
	
def create_godfrey(x, y):
	monster = create_noble(x, y)
	monster.name = 'Godfrey'
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["The most amazing magical items can be yours!", "Come! Examine my wares! I promise that you will be amazed!", "The deepest secrets! The most forbidden magics! Power beyond imagining!", "Do not miss this opportunity to purchase incredible artefacts!"]
	monster.merchant = True
	for i in range(random.randint(5, 8)):
		func = random.choice(common_magic_func_list)
		monster.inventory.append(func())
	for i in range(random.randint(3, 5)):
		func = random.choice(rare_magic_func_list)
		monster.inventory.append(func())
	merge_items_in_inventory(monster)
	### create follower to guard merchant in case of player aggression
	for i in range(2):
		(follower_x, follower_y) = random_unblocked_spot_near(x, y)
		follower = create_gladiator(follower_x, follower_y)
		follower.name = 'bodyguard'
		follower.fighter.faction = 'neutral'
		follower.fighter.true_faction = 'neutral'
		follower_ai_component = CompanionMonster(monster, 2)
		follower_ai_component.owner = follower
		follower.ai = follower_ai_component
		follower.fighter.can_join = False
		monster.followers.append(follower)
		actors.append(follower)
	return monster
	
def create_ingefred(x, y):
	monster = create_veteran(x, y)
	monster.name = 'Ingefred'
	monster.proper_noun = True
	monster.fighter.faction = 'neutral'
	monster.fighter.true_faction = 'neutral'
	monster.fighter.can_join = False
	monster.chatty = True
	monster.flavour_text = ["You there, come and speak to me about the North Warren Adventurer's Guild.", "There is not much more reliable in these troubled times than a strong arm with a sharp sword.", "Safety in numbers; truer words have never been spoken.", "Forget the empty prayers of cowardly priests, I can offer you real protection."]
	monster.guildmaster = [create_guard(0, 0), create_guard(0, 0), create_acolyte(0, 0), create_acolyte(0, 0), create_thug(0, 0), create_knight(0, 0), create_veteran(0, 0), create_scout(0, 0)]
	return monster
	
###
### ITEM GENERATION FUNCTIONS
###

### WEAPONS

def create_club():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=4, ac=0, weight=2, properties=['bludgeoning', 'light', 'simple weapon'])
	item = Object(0, 0, ')', 'club', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = .1
	item.always_visible = False
	item.big_char = int("0xE316", 16)
	item.small_char = int("0xE816", 16)
	return item
	
def create_dagger():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=4, ac=0, weight=1, properties=['piercing', 'finesse', 'light', 'thrown', 'simple weapon'])
	item = Object(0, 0, ')', 'dagger', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 2
	item.always_visible = False
	item.big_char = int("0xE317", 16)
	item.small_char = int("0xE817", 16)
	return item
	
def create_great_club():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=10, properties=['bludgeoning', 'two-handed', 'simple weapon'])
	item = Object(0, 0, ')', 'great club', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = .2
	item.always_visible = False
	item.big_char = int("0xE318", 16)
	item.small_char = int("0xE818", 16)
	return item
	
def create_handaxe():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=2, properties=['slashing', 'light', 'thrown', 'simple weapon'])
	item = Object(0, 0, ')', 'hand axe', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 5
	item.always_visible = False
	item.big_char = int("0xE319", 16)
	item.small_char = int("0xE819", 16)
	return item
	
def create_javelin():
	equipment_component = Equipment(slot='quiver', num_dmg_die=1, dmg_die=6, ac=0, weight=2, properties=['piercing', 'thrown', 'simple weapon'])
	item = Object(0, 0, ')', 'javelin', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = .5
	item.always_visible = False
	item.big_char = int("0xE320", 16)
	item.small_char = int("0xE820", 16)
	return item
	
def create_light_hammer():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=4, ac=0, weight=2, properties=['bludgeoning', 'light', 'thrown', 'simple weapon'])
	item = Object(0, 0, ')', 'light hammer', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 2
	item.always_visible = False
	item.big_char = int("0xE321", 16)
	item.small_char = int("0xE821", 16)
	return item
	
def create_mace():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=4, properties=['bludgeoning', 'simple weapon'])
	item = Object(0, 0, ')', 'mace', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 5
	item.always_visible = False
	item.big_char = int("0xE322", 16)
	item.small_char = int("0xE822", 16)
	return item
	
def create_quarterstaff():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=4, properties=['bludgeoning', 'versatile', 'simple weapon'])
	item = Object(0, 0, ')', 'quarterstaff', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = .2
	item.always_visible = False
	item.big_char = int("0xE323", 16)
	item.small_char = int("0xE823", 16)
	return item
	
def create_sickle():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=4, ac=0, weight=2, properties=['slashing', 'light', 'simple weapon'])
	item = Object(0, 0, ')', 'sickle', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 1
	item.always_visible = False
	item.big_char = int("0xE324", 16)
	item.small_char = int("0xE824", 16)
	return item
	
def create_spear():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=3, properties=['piercing', 'versatile', 'thrown', 'simple weapon'])
	item = Object(0, 0, ')', 'spear', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 1
	item.always_visible = False
	item.big_char = int("0xE325", 16)
	item.small_char = int("0xE825", 16)
	return item
	
def create_light_crossbow():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=5, properties=['piercing', 'loading', 'launcher', 'two-handed', 'simple weapon'])
	item = Object(0, 0, ')', 'light crossbow', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 25
	item.always_visible = False
	item.big_char = int("0xE326", 16)
	item.small_char = int("0xE826", 16)
	return item
	
def create_shortbow():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=2, properties=['piercing', 'launcher', 'two-handed', 'simple weapon'])
	item = Object(0, 0, ')', 'shortbow', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 25
	item.always_visible = False
	item.big_char = int("0xE328", 16)
	item.small_char = int("0xE828", 16)
	return item
	
def create_sling():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=4, ac=0, weight=1, properties=['bludgeoning', 'launcher', 'simple weapon'])
	item = Object(0, 0, ')', 'sling', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = .1
	item.always_visible = False
	item.big_char = int("0xE350", 16)
	item.small_char = int("0xE850", 16)
	return item
	
def create_battleaxe():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=4, properties=['slashing', 'versatile', 'martial weapon'])
	item = Object(0, 0, ')', 'battleaxe', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 10
	item.always_visible = False
	item.big_char = int("0xE329", 16)
	item.small_char = int("0xE829", 16)
	return item
	
def create_flail():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=2, properties=['bludgeoning', 'martial weapon'])
	item = Object(0, 0, ')', 'flail', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 10
	item.always_visible = False
	item.big_char = int("0xE330", 16)
	item.small_char = int("0xE830", 16)
	return item
	
def create_glaive():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=10, ac=0, weight=6, properties=['slashing', 'heavy', 'reach', 'two-handed', 'martial weapon'])
	item = Object(0, 0, ')', 'glaive', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 20
	item.always_visible = False
	item.big_char = int("0xE331", 16)
	item.small_char = int("0xE831", 16)
	return item
	
def create_greataxe():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=12, ac=0, weight=7, properties=['slashing', 'heavy', 'two-handed', 'martial weapon'])
	item = Object(0, 0, ')', 'greataxe', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 30
	item.always_visible = False
	item.big_char = int("0xE332", 16)
	item.small_char = int("0xE832", 16)
	return item
	
def create_greatsword():
	equipment_component = Equipment(slot='main hand', num_dmg_die=2, dmg_die=6, ac=0, weight=6, properties=['slashing', 'heavy', 'two-handed', 'martial weapon'])
	item = Object(0, 0, ')', 'greatsword', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 50
	item.always_visible = False
	item.big_char = int("0xE333", 16)
	item.small_char = int("0xE833", 16)
	return item
	
def create_halberd():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=10, ac=0, weight=6, properties=['slashing', 'heavy', 'reach', 'two-handed', 'martial weapon'])
	item = Object(0, 0, ')', 'halberd', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 20
	item.always_visible = False
	item.big_char = int("0xE334", 16)
	item.small_char = int("0xE834", 16)
	return item
	
def create_longsword():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=3, properties=['slashing', 'versatile', 'martial weapon'])
	item = Object(0, 0, ')', 'longsword', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 15
	item.always_visible = False
	item.big_char = int("0xE336", 16)
	item.small_char = int("0xE836", 16)
	return item
	
def create_maul():
	equipment_component = Equipment(slot='main hand', num_dmg_die=2, dmg_die=8, ac=0, weight=10, properties=['bludgeoning', 'heavy', 'two-handed', 'martial weapon'])
	item = Object(0, 0, ')', 'maul', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 10
	item.always_visible = False
	item.big_char = int("0xE337", 16)
	item.small_char = int("0xE837", 16)
	return item
	
def create_morningstar():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=4, properties=['piercing', 'martial weapon'])
	item = Object(0, 0, ')', 'morningstar', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 15
	item.always_visible = False
	item.big_char = int("0xE338", 16)
	item.small_char = int("0xE838", 16)
	return item
	
def create_pike():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=10, ac=0, weight=10, properties=['piercing', 'heavy', 'reach', 'two-handed', 'martial weapon'])
	item = Object(0, 0, ')', 'pike', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 5
	item.always_visible = False
	item.big_char = int("0xE339", 16)
	item.small_char = int("0xE839", 16)
	return item
	
def create_rapier():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=2, properties=['piercing', 'finesse', 'martial weapon'])
	item = Object(0, 0, ')', 'rapier', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 25
	item.always_visible = False
	item.big_char = int("0xE340", 16)
	item.small_char = int("0xE840", 16)
	return item
	
def create_scimitar():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=3, properties=['slashing', 'finesse', 'light', 'martial weapon'])
	item = Object(0, 0, ')', 'scimitar', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 25
	item.always_visible = False
	item.big_char = int("0xE341", 16)
	item.small_char = int("0xE841", 16)
	return item
	
def create_shortsword():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=2, properties=['piercing', 'finesse', 'light', 'martial weapon'])
	item = Object(0, 0, ')', 'shortsword', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 10
	item.always_visible = False
	item.big_char = int("0xE342", 16)
	item.small_char = int("0xE842", 16)
	return item
	
def create_trident():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=4, properties=['piercing', 'thrown', 'versatile', 'martial weapon'])
	item = Object(0, 0, ')', 'trident', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 5
	item.always_visible = False
	item.big_char = int("0xE343", 16)
	item.small_char = int("0xE843", 16)
	return item
	
def create_war_pick():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=2, properties=['piercing', 'martial weapon'])
	item = Object(0, 0, ')', 'war pick', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 5
	item.always_visible = False
	item.big_char = int("0xE344", 16)
	item.small_char = int("0xE844", 16)
	return item
	
def create_warhammer():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=2, properties=['bludgeoning', 'versatile', 'martial weapon'])
	item = Object(0, 0, ')', 'warhammer', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 15
	item.always_visible = False
	item.big_char = int("0xE345", 16)
	item.small_char = int("0xE845", 16)
	return item
	
def create_whip():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=4, ac=0, weight=3, properties=['slashing', 'finesse', 'reach', 'martial weapon'])
	item = Object(0, 0, ')', 'whip', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 2
	item.always_visible = False
	item.big_char = int("0xE346", 16)
	item.small_char = int("0xE846", 16)
	return item
	
def create_blowgun():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=1, ac=0, weight=1, properties=['piercing', 'launcher', 'loading', 'martial weapon'])
	item = Object(0, 0, ')', 'blowgun', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 10
	condition = Condition(name='poison', damage_on_hit=True, num_dmg_die=1, dmg_die=4, dmg_type='poison')
	condition.owner = item
	item.item.conditions.append(condition)
	item.always_visible = False
	item.big_char = int("0xE347", 16)
	item.small_char = int("0xE847", 16)
	return item
	
def create_hand_crossbow():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=3, properties=['piercing', 'launcher', 'loading', 'martial weapon'])
	item = Object(0, 0, ')', 'hand crossbow', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 75
	item.always_visible = False
	item.big_char = int("0xE326", 16)
	item.small_char = int("0xE826", 16)
	return item
	
def create_heavy_crossbow():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=10, ac=0, weight=18, properties=['piercing', 'launcher', 'loading', 'heavy', 'two-handed', 'martial weapon'])
	item = Object(0, 0, ')', 'heavy crossbow', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 50
	item.always_visible = False
	item.big_char = int("0xE348", 16)
	item.small_char = int("0xE848", 16)
	return item
	
def create_longbow():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=8, ac=0, weight=2, properties=['piercing', 'launcher', 'heavy', 'two-handed', 'martial weapon'])
	item = Object(0, 0, ')', 'longbow', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 50
	item.always_visible = False
	item.big_char = int("0xE349", 16)
	item.small_char = int("0xE849", 16)
	return item

### SHIELDS
	
def create_shield():
	equipment_component = Equipment(slot='off hand', num_dmg_die=0, dmg_die=0, ac=2, weight=6, properties=['shield'])
	item = Object(0, 0, '[', 'shield', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 10
	item.always_visible = False
	item.big_char = int("0xE315", 16)
	item.small_char = int("0xE815", 16)
	return item
	
### ARMOUR
	
def create_padded_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=11, weight=8, properties=['light armour', 'unstealthy'])
	item = Object(0, 0, '[', 'padded armour', OTHER_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 5
	item.always_visible = False
	item.big_char = int("0xE303", 16)
	item.small_char = int("0xE803", 16)
	return item
	
def create_leather_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=11, weight=10, properties=['light armour'])
	item = Object(0, 0, '[', 'leather armour', OTHER_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 10
	item.always_visible = False
	item.big_char = int("0xE304", 16)
	item.small_char = int("0xE804", 16)
	return item
	
def create_studded_leather_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=12, weight=13, properties=['light armour'])
	item = Object(0, 0, '[', 'studded leather', OTHER_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 45
	item.always_visible = False
	item.big_char = int("0xE305", 16)
	item.small_char = int("0xE805", 16)
	return item
	
def create_hide_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=12, weight=12, properties=['medium armour'])
	item = Object(0, 0, '[', 'hide armour', OTHER_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 10
	item.always_visible = False
	item.big_char = int("0xE306", 16)
	item.small_char = int("0xE806", 16)
	return item
	
def create_chain_shirt_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=13, weight=20, properties=['medium armour', 'metal'])
	item = Object(0, 0, '[', 'chain shirt', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 50
	item.always_visible = False
	item.big_char = int("0xE307", 16)
	item.small_char = int("0xE807", 16)
	return item
	
def create_scale_mail_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=14, weight=45, properties=['medium armour', 'unstealthy', 'metal'])
	item = Object(0, 0, '[', 'scale mail', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 50
	item.always_visible = False
	item.big_char = int("0xE308", 16)
	item.small_char = int("0xE808", 16)
	return item
	
def create_breastplate_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=14, weight=20, properties=['medium armour', 'metal'])
	item = Object(0, 0, '[', 'breastplate', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 400
	item.always_visible = False
	item.big_char = int("0xE309", 16)
	item.small_char = int("0xE809", 16)
	return item
	
def create_half_plate_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=15, weight=40, properties=['medium armour', 'unstealthy', 'metal'])
	item = Object(0, 0, '[', 'half plate armour', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 750
	item.always_visible = False
	item.big_char = int("0xE310", 16)
	item.small_char = int("0xE810", 16)
	return item
	
def create_ring_mail_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=14, weight=40, properties=['heavy armour', 'unstealthy', 'metal'])
	item = Object(0, 0, '[', 'ring mail', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 30
	item.always_visible = False
	item.big_char = int("0xE311", 16)
	item.small_char = int("0xE811", 16)
	return item
	
def create_chain_mail_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=16, weight=55, properties=['heavy armour', 'unstealthy', 'str 13', 'metal'])
	item = Object(0, 0, '[', 'chain mail', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 75
	item.always_visible = False
	item.big_char = int("0xE312", 16)
	item.small_char = int("0xE812", 16)
	return item
	
def create_splint_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=17, weight=60, properties=['heavy armour', 'unstealthy', 'str 15', 'metal'])
	item = Object(0, 0, '[', 'splint armour', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 200
	item.always_visible = False
	item.big_char = int("0xE313", 16)
	item.small_char = int("0xE813", 16)
	return item
	
def create_plate_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=18, weight=65, properties=['heavy armour', 'unstealthy', 'str 15', 'metal'])
	item = Object(0, 0, '[', 'plate armour', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 1500
	item.always_visible = False
	item.big_char = int("0xE314", 16)
	item.small_char = int("0xE814", 16)
	return item
	
### MISC ITEMS

def create_gold(quantity=None):
	if quantity is None: quantity = random.randint(5, 20)
	item = Object(0, 0, '$', 'gold coins', 'yellow', quantity=quantity)
	item.always_visible = False
	item.item = Item() 
	item.item.owner = item
	item.big_char = int("0xE378", 16)
	item.small_char = int("0xE878", 16)
	return item

def create_torch():
	equipment_component = Equipment(slot='off hand', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=['flammable'])
	item = Object(0, 0, '(', 'torch', OTHER_WEAPON_COLOUR, equipment=equipment_component)
	item.value = .1
	item.always_visible = False
	item.big_char = int("0xE355", 16)
	item.small_char = int("0xE855", 16)
	return item
	
def create_food_rations(quantity=None):
	if quantity is None: quantity = 1
	item = Object(0, 0, '%', 'food rations', OTHER_WEAPON_COLOUR, quantity=quantity)
	item.value = 10
	item.always_visible = False
	item.item = Item() #equipment takes care of this automatically but food is a weird special case because it doesn't do anything
	item.item.owner = item
	item.big_char = int("0xE356", 16)
	item.small_char = int("0xE856", 16)
	return item
	
def create_arrows(quantity=None):
	if quantity is None: quantity = random.randint(15, 20)
	equipment_component = Equipment(slot='quiver', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, ')', 'arrows', OTHER_WEAPON_COLOUR, equipment=equipment_component, quantity=quantity)
	item.value = .2
	item.always_visible = False
	item.big_char = int("0xE353", 16)
	item.small_char = int("0xE853", 16)
	return item
	
def create_bolts(quantity=None):
	if quantity is None: quantity = random.randint(15, 20)
	equipment_component = Equipment(slot='quiver', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, ')', 'bolts', METAL_WEAPON_COLOUR, equipment=equipment_component, quantity=quantity)
	item.value = .2
	item.always_visible = False
	item.big_char = int("0xE352", 16)
	item.small_char = int("0xE852", 16)
	return item
	
def create_bullets(quantity=None):
	if quantity is None: quantity = random.randint(15, 20)
	equipment_component = Equipment(slot='quiver', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, ')', 'bullets', OTHER_WEAPON_COLOUR, equipment=equipment_component, quantity=quantity)
	item.value = .1
	item.always_visible = False
	item.big_char = int("0xE354", 16)
	item.small_char = int("0xE854", 16)
	return item
	
def create_dart(quantity=None):
	if quantity is None: quantity = random.randint(15, 20)
	equipment_component = Equipment(slot='quiver', num_dmg_die=1, dmg_die=4, ac=0, weight=0, properties=['piercing', 'finesse', 'thrown', 'simple weapon'])
	item = Object(0, 0, ')', 'dart', METAL_WEAPON_COLOUR, equipment=equipment_component, quantity=quantity)
	item.value = .2
	item.always_visible = False
	item.big_char = int("0xE327", 16)
	item.small_char = int("0xE827", 16)
	return item
	
def create_needles(quantity=None):
	if quantity is None: quantity = random.randint(15, 20)
	equipment_component = Equipment(slot='quiver', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, ')', 'needles', METAL_WEAPON_COLOUR, equipment=equipment_component, quantity=quantity)
	item.value = .2
	item.always_visible = False
	item.big_char = int("0xE351", 16)
	item.small_char = int("0xE851", 16)
	return item
	
###
### MAGIC ITEMS
###
	
def create_potion_of_healing(quantity=None):
	if quantity is None: quantity = 1
	item_component = Item(use_function=use_potion_of_healing)
	item = Object(0, 0, '!', 'potion of healing', MISC_COLOUR, item=item_component, quantity=quantity)
	item.value = 50
	item.always_visible = False
	item.big_char = int("0xE357", 16)
	item.small_char = int("0xE857", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_vial_of_acid(quantity=None):
	if quantity is None: quantity = 1
	item_component = Item(use_function=use_vial_of_acid)
	item = Object(0, 0, '!', 'vial of acid', MISC_COLOUR, item=item_component, quantity=quantity)
	item.value = 25
	item.always_visible = False
	item.big_char = int("0xE359", 16)
	item.small_char = int("0xE859", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_oil_of_sharpness(quantity=None):
	if quantity is None: quantity = 1
	item_component = Item(use_function=use_oil_of_sharpness)
	item = Object(0, 0, '!', 'oil of sharpness', MISC_COLOUR, item=item_component, quantity=quantity)
	item.value = 250
	item.always_visible = False
	item.big_char = int("0xE358", 16)
	item.small_char = int("0xE858", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_potion_of_giant_strength(type=None, quantity=None):
	if quantity is None: quantity = 1
	if type is None:
		types = (('hill giant', 21), ('hill giant', 21), ('hill giant', 21), ('frost giant', 23), ('stone giant', 23), ('frost giant', 23), ('stone giant', 23), ('fire giant', 25), ('cloud giant', 27), ('storm giant', 29)) #duplicate values to make less powerful types more common
		type = random.choice(types)
	item_component = Item(use_function=use_potion_of_giant_strength)
	item_component.special = type[1]
	item = Object(0, 0, '!', 'potion of ' + type[0] + ' strength', MISC_COLOUR, item=item_component, quantity=quantity)
	item.value = 350
	item.always_visible = False
	item.big_char = int("0xE360", 16)
	item.small_char = int("0xE860", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_potion_of_heroism(quantity=None):
	if quantity is None: quantity = 1
	item_component = Item(use_function=use_potion_of_heroism)
	item = Object(0, 0, '!', 'potion of heroism', MISC_COLOUR, item=item_component, quantity=quantity)
	item.value = 250
	item.always_visible = False
	item.big_char = int("0xE361", 16)
	item.small_char = int("0xE861", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_ring_of_protection():
	equipment_component = Equipment(slot='finger', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '=', 'ring of protection', MISC_COLOUR, equipment=equipment_component)
	item.value = 500
	item.always_visible = False
	item.big_char = int("0xE372", 16)
	item.small_char = int("0xE872", 16)
	condition = Condition(name='protection', ac_bonus=1, saving_throw_bonus=1, colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_ring_of_invisibility():
	equipment_component = Equipment(slot='finger', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[], adds_trait=['use invisibility'])
	item = Object(0, 0, '=', 'ring of invisibility', MISC_COLOUR, equipment=equipment_component)
	item.value = 1000
	item.always_visible = False
	item.big_char = int("0xE373", 16)
	item.small_char = int("0xE873", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_ring_of_poison_resistance():
	equipment_component = Equipment(slot='finger', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '=', 'ring of poison resistance', MISC_COLOUR, equipment=equipment_component)
	item.value = 500
	item.always_visible = False
	item.big_char = int("0xE374", 16)
	item.small_char = int("0xE874", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('poison resistance')
	return item
	
def create_ring_of_the_forge():
	equipment_component = Equipment(slot='finger', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '=', 'ring of the forge', MISC_COLOUR, equipment=equipment_component)
	item.value = 250
	item.always_visible = False
	item.big_char = int("0xE375", 16)
	item.small_char = int("0xE875", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('fire resistance')
	return item
	
def create_ring_of_the_dancer():
	equipment_component = Equipment(slot='finger', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[], dex_bonus=1)
	item = Object(0, 0, '=', 'ring of the dancer', MISC_COLOUR, equipment=equipment_component)
	item.value = 450
	item.always_visible = False
	item.big_char = int("0xE376", 16)
	item.small_char = int("0xE876", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_ring_of_the_drow():
	equipment_component = Equipment(slot='finger', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[], cha_bonus=-2)
	item = Object(0, 0, '=', 'ring of the drow', MISC_COLOUR, equipment=equipment_component)
	item.value = 1000
	item.always_visible = False
	item.big_char = int("0xE372", 16)
	item.small_char = int("0xE872", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('darkvision')
	return item
	
def create_wand_of_magic_missiles():
	item_component = Item(use_function=use_wand_of_magic_missile, max_charges=7)
	item = Object(0, 0, '/', 'wand of magic missiles', MISC_COLOUR, item=item_component)
	item.value = 2500
	item.always_visible = False
	item.big_char = int("0xE316", 16)
	item.small_char = int("0xE816", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_wand_of_lightning_bolts():
	item_component = Item(use_function=use_wand_of_lightning_bolt, max_charges=7)
	item = Object(0, 0, '/', 'wand of lightning bolts', MISC_COLOUR, item=item_component)
	item.value = 5000
	item.always_visible = False
	item.big_char = int("0xE316", 16)
	item.small_char = int("0xE816", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_wand_of_fireballs():
	item_component = Item(use_function=use_wand_of_fireball, max_charges=7)
	item = Object(0, 0, '/', 'wand of fireballs', MISC_COLOUR, item=item_component)
	item.value = 4500
	item.always_visible = False
	item.big_char = int("0xE316", 16)
	item.small_char = int("0xE816", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_wand_of_web():
	item_component = Item(use_function=use_wand_of_web, max_charges=7)
	item = Object(0, 0, '/', 'wand of web', MISC_COLOUR, item=item_component)
	item.value = 2500
	item.always_visible = False
	item.big_char = int("0xE316", 16)
	item.small_char = int("0xE816", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_wand_of_humblesongs_gift():
	item_component = Item(use_function=use_wand_of_humblesongs_gift, max_charges=21)
	item = Object(0, 0, '/', "wand of humblesong's gift", MISC_COLOUR, item=item_component)
	item.value = 1000
	item.always_visible = False
	item.big_char = int("0xE316", 16)
	item.small_char = int("0xE816", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_dwarven_plate_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=18, weight=65, properties=['heavy armour', 'unstealthy', 'str 15'])
	item = Object(0, 0, '[', 'dwarven plate armour', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 10000
	item.always_visible = False
	item.big_char = int("0xE314", 16)
	item.small_char = int("0xE814", 16)
	condition = Condition(name='enchantment', ac_bonus=2, colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_dragon_scale_mail(type=None):
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=14, weight=45, properties=['medium armour', 'unstealthy'])
	item = Object(0, 0, '[', 'dragon scale mail', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 10000
	item.always_visible = False
	item.big_char = int("0xE308", 16)
	item.small_char = int("0xE808", 16)
	if type is None:
		types = (('black', 'acid resistance'), ('blue', 'lightning resistance'), ('brass', 'fire resistance'), ('bronze', 'lightning resistance'), ('copper', 'acid resistance'), ('gold', 'fire resistance'), ('green', 'poison resistance'), ('red', 'fire resistance'), ('silver', 'cold resistance'), ('white', 'cold resistance'))
		type = random.choice(types)
	condition = Condition(name='enchantment', ac_bonus=1, name_prefix=type[0] + ' ', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append(type[1])
	return item
	
def create_elven_chain_mail_armour():
	equipment_component = Equipment(slot='body', num_dmg_die=0, dmg_die=0, ac=13, weight=20, properties=['medium armour', 'metal'])
	item = Object(0, 0, '[', 'elven chain mail', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 7500
	item.always_visible = False
	item.big_char = int("0xE307", 16)
	item.small_char = int("0xE807", 16)
	condition = Condition(name='enchantment', ac_bonus=1, colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	if item.equipment.adds_proficiency is None: 
		item.equipment.adds_proficiency = []
	item.equipment.adds_proficiency.append('medium armour')
	return item
	
def create_mithral_armour(type=None):
	if type is None:
		types = (create_chain_shirt_armour, create_scale_mail_armour, create_breastplate_armour, create_half_plate_armour, create_ring_mail_armour, create_chain_mail_armour, create_splint_armour, create_plate_armour)
		type = random.choice(types)
	item = type()
	item.value = item.value * 50
	if 'unstealthy' in item.equipment.properties: item.equipment.properties.remove('unstealthy')
	for property in item.equipment.properties:
		if property[:3] == 'str':
			item.equipment.properties.remove(property)
	condition = Condition(name='', name_prefix='mithral ', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_scimitar_of_speed():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=6, ac=0, weight=3, properties=['slashing', 'finesse', 'light', 'martial weapon'])
	item = Object(0, 0, ')', 'scimitar', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 10000
	item.always_visible = False
	item.big_char = int("0xE341", 16)
	item.small_char = int("0xE841", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('extra attack')
	condition = Condition(name='enchantment', to_hit_bonus=2, damage_bonus=2, name_suffix=' of speed', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item

def create_quickblade():
	equipment_component = Equipment(slot='main hand', num_dmg_die=1, dmg_die=4, ac=0, weight=1, properties=['piercing', 'finesse', 'light', 'thrown', 'simple weapon'])
	item = Object(0, 0, ')', 'quickblade', METAL_WEAPON_COLOUR, equipment=equipment_component)
	item.value = 7500
	item.always_visible = False
	item.big_char = int("0xE317", 16)
	item.small_char = int("0xE817", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('extra attack')
	item.equipment.adds_trait.append('extra attack')
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_girdle_of_tenacity():
	equipment_component = Equipment(slot='belt', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[], con_bonus=1)
	item = Object(0, 0, '[', 'girdle of tenacity', MISC_COLOUR, equipment=equipment_component)
	item.value = 750
	item.always_visible = False
	item.big_char = int("0xE379", 16)
	item.small_char = int("0xE879", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_amulet_of_detection():
	equipment_component = Equipment(slot='neck', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '"', 'amulet of detection', MISC_COLOUR, equipment=equipment_component)
	item.value = 750
	item.always_visible = False
	item.big_char = int("0xE362", 16)
	item.small_char = int("0xE862", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('perception')
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_amulet_of_mystic_insight():
	equipment_component = Equipment(slot='neck', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[], wis_bonus=1)
	item = Object(0, 0, '"', 'amulet of mystic insight', MISC_COLOUR, equipment=equipment_component)
	item.value = 750
	item.always_visible = False
	item.big_char = int("0xE363", 16)
	item.small_char = int("0xE863", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_boots_of_the_winterlands():
	equipment_component = Equipment(slot='feet', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '[', 'boots of the winterlands', OTHER_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 500
	item.always_visible = False
	item.big_char = int("0xE380", 16)
	item.small_char = int("0xE880", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('cold resistance')
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_mantle_of_magic_resistance():
	equipment_component = Equipment(slot='cloak', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '[', 'mantle of magic resistance', OTHER_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 2500
	item.always_visible = False
	item.big_char = int("0xE382", 16)
	item.small_char = int("0xE882", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('magic resistance')
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_cloak_of_elvenkind():
	equipment_component = Equipment(slot='cloak', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '[', 'cloak of elvenkind', OTHER_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 2000
	item.always_visible = False
	item.big_char = int("0xE382", 16)
	item.small_char = int("0xE882", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('stealthy')
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_boots_of_elvenkind():
	equipment_component = Equipment(slot='feet', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '[', 'boots of elvenkind', OTHER_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 1750
	item.always_visible = False
	item.big_char = int("0xE380", 16)
	item.small_char = int("0xE880", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('stealthy')
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_periapt_of_proof_against_poisons():
	equipment_component = Equipment(slot='neck', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=[])
	item = Object(0, 0, '"', 'periapt of proof against poisons', MISC_COLOUR, equipment=equipment_component)
	item.value = 750
	item.always_visible = False
	item.big_char = int("0xE364", 16)
	item.small_char = int("0xE884", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('poison resistance')
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_gauntlets_of_ogrekind():
	equipment_component = Equipment(slot='hands', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=['metal'], str_bonus=2, con_bonus=2, int_bonus=-2, cha_bonus=-4)
	item = Object(0, 0, '[', 'gauntlets of ogrekind', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 5000
	item.always_visible = False
	item.big_char = int("0xE384", 16)
	item.small_char = int("0xE884", 16)
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
	
def create_helm_of_orcsblood():
	equipment_component = Equipment(slot='head', num_dmg_die=0, dmg_die=0, ac=0, weight=1, properties=['metal'], str_bonus=1, con_bonus=1, cha_bonus=-2)
	item = Object(0, 0, '[', 'helm of orcsblood', METAL_ARMOUR_COLOUR, equipment=equipment_component)
	item.value = 3500
	item.always_visible = False
	item.big_char = int("0xE385", 16)
	item.small_char = int("0xE885", 16)
	if item.equipment.adds_trait is None: 
		item.equipment.adds_trait = []
	item.equipment.adds_trait.append('relentless')
	condition = Condition(name='', colour_over_ride='light purple')
	condition.owner = item
	item.item.conditions.append(condition)
	return item
		
###
### MAGIC ITEM FUNCTIONS
###

def add_weapon_enchantment(weapon, modifier=1):
	condition = Condition(name='enchantment', to_hit_bonus=modifier, damage_bonus=modifier, name_tail=' +' + str(modifier), colour_over_ride='light purple')
	condition.owner = weapon
	weapon.item.conditions.append(condition)
	
def add_weapon_flaming(weapon):
	condition = Condition(name='flaming', name_prefix='flaming ', damage_on_hit=True, num_dmg_die=2, dmg_die=6, dmg_type='fire', colour_over_ride='light purple')
	condition.owner = weapon
	weapon.item.conditions.append(condition)
	#an extra condition is needed for the illumination effect
	condition = Condition(name='illumination')
	condition.owner = weapon
	weapon.item.conditions.append(condition)
	
def add_weapon_frost(weapon):
	condition = Condition(name='frost', name_suffix=' of frost', damage_on_hit=True, num_dmg_die=1, dmg_die=6, dmg_type='cold', colour_over_ride='light purple')
	condition.owner = weapon
	weapon.item.conditions.append(condition)
	
def add_weapon_venom(weapon):
	condition = Condition(name='venom', name_suffix=' of venom', damage_on_hit=True, damage_on_hit_save_type='constitution', damage_on_hit_save_dc=10, damage_on_hit_save_dmg_modifer=0, num_dmg_die=1, dmg_die=4, dmg_type='poison', colour_over_ride='light purple')
	condition.owner = weapon
	weapon.item.conditions.append(condition)
	
def add_armour_enchantment(armour, modifier=1):
	condition = Condition(name='enchantment', ac_bonus=modifier, name_tail=' +' + str(modifier), colour_over_ride='light purple')
	condition.owner = armour
	armour.item.conditions.append(condition)
	
def add_armour_resistance(armour, type=None):
	if type is None:
		types = ('acid resistance', 'cold resistance', 'fire resistance', 'force resistance', 'lightning resistance', 'necrotic resistance', 'poison resistance', 'psychic resistance', 'radiant resistance', 'thunder resistance')
		type = random.choice(types)
	if armour.equipment.adds_trait is None: 
		armour.equipment.adds_trait = []
	armour.equipment.adds_trait.append(type)
	condition = Condition(name='enchantment', name_suffix=' of ' + type, colour_over_ride='light purple')
	condition.owner = armour
	armour.item.conditions.append(condition)
	
def autoexplore():
	global dungeon_level, game_state, autoexplore_target, finished_exploring

	if game_state == 'exploring':
		for actor in actors: #check to see if rest was disturbed
			if player.can_see_object(actor) and player != actor:
				if player.fighter.faction != actor.fighter.faction:
					message('Exploration has been interrupted!')
					game_state = 'playing'
					return
	if game_state == 'autoplay':
		#hacky way of making it go forever
		player.fighter.hp = player.fighter.max_hp
		for actor in actors: #check to see if rest was disturbed
			if player.can_see_object(actor) and player != actor:
				if player.fighter.faction != actor.fighter.faction:
					if player.distance_to(actor) < 2:
						player.fighter.attack(actor)
						return
					else:
						player.move_towards(actor.x, actor.y)
						return
	if game_state == 'exploring' or game_state == 'autoplay': 
		#open all nearby doors so they don't mess with the algorithm
		try:
			if is_openable(player.x-1, player.y-1) and is_blocked(player.x-1, player.y-1): player_open_door(-1, -1)
			if is_openable(player.x-1, player.y) and is_blocked(player.x-1, player.y): player_open_door(-1, 0)
			if is_openable(player.x-1, player.y+1) and is_blocked(player.x-1, player.y+1): player_open_door(-1, 1)
			if is_openable(player.x, player.y-1) and is_blocked(player.x, player.y-1): player_open_door(0, -1)
			if is_openable(player.x, player.y+1) and is_blocked(player.x, player.y+1): player_open_door(0, 1)
			if is_openable(player.x+1, player.y+1) and is_blocked(player.x+1, player.y+1): player_open_door(1, 1)
			if is_openable(player.x+1, player.y) and is_blocked(player.x+1, player.y): player_open_door(1, 0)
			if is_openable(player.x+1, player.y+1) and is_blocked(player.x+1, player.y+1): player_open_door(1, 1)
		except:
			print('Autoexplore going out of bounds.')
		list_of_tiles = [] #this will be a list representing map x,y
		finished_list = []
		list_of_tiles.append((player.x, player.y)) #start with player location
		#loop through surrounding tiles looking for nearest unexplored tile
		unexplored_tile = None
		if autoexplore_target is not None:
			if map[autoexplore_target[0]][autoexplore_target[1]].explored:
				autoexplore_target = None
			else:
				unexplored_tile = autoexplore_target
		while unexplored_tile == None and not finished_exploring:
			made_progress = False
			for tile in list_of_tiles:
				list_of_tiles = list(set(list_of_tiles)) #this will remove duplicates and tidy up the list
				finished_list.append(tile)
				list_of_tiles.remove(tile)
				adjacent_tiles = []
				tiles_to_append = []
				adjacent_tiles.append((tile[0]-1, tile[1]-1))
				adjacent_tiles.append((tile[0], tile[1]-1))
				adjacent_tiles.append((tile[0]+1, tile[1]-1))
				adjacent_tiles.append((tile[0]-1, tile[1]))
				adjacent_tiles.append((tile[0]+1, tile[1]))
				adjacent_tiles.append((tile[0]-1, tile[1]+1))
				adjacent_tiles.append((tile[0], tile[1]+1))
				adjacent_tiles.append((tile[0]+1, tile[1]+1))
				for test_tile in adjacent_tiles:
					x = test_tile[0]
					y = test_tile[1]
					if 0 < x < MAP_WIDTH and 0 < y < MAP_HEIGHT:
						if (x, y) not in list_of_tiles:
							if (x, y) not in finished_list:
								if not map[x][y].blocked or map[x][y].openable:
									if not map[x][y].explored:
										unexplored_tile = (x, y)
									else:
										tiles_to_append.append((x, y))
				if len(tiles_to_append) > 0: made_progress = True
				list_of_tiles = list_of_tiles + tiles_to_append
			if not made_progress: break
		if unexplored_tile is None:
			finished_exploring = True
			if game_state == 'exploring':
				if dungeon_level == dungeon_branch.depth:
					message('Finished exploring.')
					game_state = 'playing'
				else:
					test = None
					for item in items:
						if item.links_to is not None:
							if player.x == item.x and player.y == item.y:
								test = item
					if item is not None:
						message('Finished exploring.')
						game_state = 'playing'
					else: 
						unexplored_tile = (down_stairs.x, down_stairs.y) #simulate the down stairs being unexplored to make the player walk there
			elif game_state == 'autoplay':
				if dungeon_level == dungeon_branch.depth:
					message('Finished exploring.')
					game_state = 'playing'
				else:
					test = None
					for item in items:
						if item.links_to is not None:
							if player.x == item.x and player.y == item.y:
								test = item
					if item is not None:
						change_level(item.links_to)
					else: 
						unexplored_tile = (down_stairs.x, down_stairs.y) #simulate the down stairs being unexplored to make the player walk there
				# else:
					# path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
					# tcod.path_compute(path, player.x, player.y, down_stairs.x, down_stairs.y)
					# (dx, dy) = tcod.path_walk(path, True)
					# if dx is not None and dy is not None:
						# if is_occupied_by_ally(dx, dy):
							# test_object = None
							# for actor in actors:
								# if actor.x == dx and actor.y == dy:
									# test_object = actor
							# if test_object is not None:
								# if test_object.fighter.faction == player.fighter.faction and test_object != player and not test_object.has_swapped:
									# player.swap_place(test_object)
									# test_object.has_swapped = True
						# else:
							# player.move_towards(dx, dy)
					# else:
						# message('Error in autoplay.')
						# game_state = 'playing'
		if unexplored_tile is not None:
			autoexplore_target = unexplored_tile
			path = tcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, path_func)
			tcod.path_compute(path, player.x, player.y, unexplored_tile[0], unexplored_tile[1])
			(dx, dy) = tcod.path_walk(path, True)
			if dx is not None and dy is not None:
				if is_occupied_by_ally(dx, dy):
					test_object = None
					for actor in actors:
						if actor.x == dx and actor.y == dy:
							test_object = actor
					if test_object is not None:
						if test_object.fighter.faction == player.fighter.faction and test_object != player and not test_object.has_swapped:
							player.swap_place(test_object)
							test_object.has_swapped = True
				else:
					player.move_towards(dx, dy)
			else:
				#we have failed to find a path despite having an unexplored tile so as a rough circuit breaker, let's move to a random empty square nearby so we can start over from there
				while True:
					x = random.randint(player.x-10, player.x+10)
					y = random.randint(player.y-10, player.y+10)
					if 1 < x < MAP_WIDTH-2 and 1 < y < MAP_HEIGHT-2:
						if not is_blocked(x, y):
							unexplored_tile = (x, y)
							break
				#message('Error in autoexplore.')
				#game_state = 'playing'

def macro_menu():
	global macros, game_state
	#create a list of all known spells, display them and let the player allocated numbers to them to use as macros to cast them
	list = player.fighter.spells
	selector = 1
	while True:
		blt.clear()
		blt.color('white')
		blt.puts(SCREEN_WIDTH // 2 - 15, SCREEN_HEIGHT // 2 - 5, '[font=log]Select a spell and assign a macro:')
		count = 0
		for spell in list:
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2 + (count*2)-2, '[font=log]' + list[count].capitalize())
			count += 1
		blt.puts(SCREEN_WIDTH//2-23, SCREEN_HEIGHT-3, '[font=log]Up/down to select and press a number to assign as macro')
		blt.color('red')
		blt.puts(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 - 4 + (selector*2), '[font=log]*')
		blt.refresh()
		key = blt.read()
		if key == blt.TK_CLOSE:
			if game_state == 'playing': save_game()
			blt.close()
			sys.exit()
		if blt.check(blt.TK_CHAR):
			key_char = chr(blt.state(blt.TK_CHAR))
		else: 
			key_char = None
		if key == blt.TK_RETURN:
			break
		elif key in [blt.TK_UP, blt.TK_KP_8] or key_char == 'k':
			if selector > 1:
				selector = selector - 1
		elif key in [blt.TK_DOWN, blt.TK_KP_2] or key_char == 'j':
			if selector < len(list):
				selector = selector + 1
		elif key_char == '0' or key_char == '1' or key_char == '2' or key_char == '3' or key_char == '4' or key_char == '5' or key_char == '6' or key_char == '7' or key_char == '8' or key_char == '9':
			try:
				macros[int(key_char)] = list[selector-1]
				message('Macro to cast ' + list[selector-1] + ' set as ' + key_char + '.')
			except IndexError:
				message('Failed to set macro.')
			break
		blt.refresh()
				
def save_level():
	#open a new empty shelve (possibly overwriting an old one) to write the game data
	global map, actors, items, effects, player, inventory, game_msgs, game_state, dungeon_level, dungeon_branch, display_mode, macros, quests, global_cooldown
	
	if not os.path.isdir('save'): os.mkdir('save')
	file = shelve.open('save/' + dungeon_branch.name + str(dungeon_level), 'n')
	file['map'] = map
	actors.remove(player)
	if not dungeon_branch.overworld:
		for actor in player.followers:
			actors.remove(actor)
	file['actors'] = actors
	file['items'] = items
	file['effects'] = effects
	file.close()
  
def load_level():
	#open the previously saved shelve and load the game data
	global map, actors, items, effects, player, inventory, game_msgs, game_state, dungeon_level, dungeon_branch, display_mode, macros, quests, global_cooldown

	file = shelve.open('save/' + dungeon_branch.name + str(dungeon_level), 'r')
	map = file['map']
	actors = file['actors']
	items = file['items']
	effects = file['effects']
	actors.insert(0, player)
	if not dungeon_branch.overworld:
		for actor in player.followers:
			actors.append(actor)
	file.close()

def save_game():
	#open a new empty shelve (possibly overwriting an old one) to write the game data
	global map, actors, items, effects, player, inventory, game_msgs, game_state, dungeon_level, dungeon_branch, display_mode, macros, quests, global_cooldown, journal, familiar
	
	if not os.path.isdir('save'): os.mkdir('save')
	file = shelve.open('save/savegame', 'n')
	file['map'] = map
	file['actors'] = actors
	file['items'] = items
	file['effects'] = effects
	file['player_index'] = actors.index(player)	 #index of player in objects list
	file['game_msgs'] = game_msgs
	file['game_state'] = game_state
	file['dungeon_level'] = dungeon_level
	file['dungeon_branch'] = dungeon_branch
	file['display_mode'] = display_mode
	file['macros'] = macros
	file['quests'] = quests
	file['journal'] = journal
	file['global_cooldown'] = global_cooldown
	if familiar is not None:
		file['familiar_index'] = actors.index(familiar)
	else:
		file['familiar_index'] = None
	file.close()
 
def load_game():
	#open the previously saved shelve and load the game data
	global map, actors, items, effects, player, inventory, game_msgs, game_state, dungeon_level, dungeon_branch, display_mode, macros, quests, global_cooldown, journal, fov_map, fov_map_fam, familiar
 
	file = shelve.open('save/savegame', 'r')
	map = file['map']
	actors = file['actors']
	items = file['items']
	effects = file['effects']
	player = actors[file['player_index']]	#get index of player in objects list and access it
	game_msgs = file['game_msgs']
	game_state = file['game_state']
	dungeon_level = file['dungeon_level']
	dungeon_branch = file['dungeon_branch']
	display_mode = file['display_mode']
	macros = file['macros']
	quests = file['quests']
	journal = file['journal']
	global_cooldown = file['global_cooldown']
	familiar_index = file['familiar_index']
	if familiar_index is not None:
		familiar = actors[familiar_index]
	else:
		familiar = None
	file.close() 
	fov_map = initialize_fov()
	fov_map_fam = initialize_fov()
	reset_globals()
	
def delete_saved_game():
	#used to clear old saved game files upon player death
	folder = 'save'
	for the_file in os.listdir(folder):
		file_path = os.path.join(folder, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			print(e)
	
def select_avatar():
	global game_state
	list_of_chars = []
	list_of_chars.append(int("0xE900", 16))
	list_of_chars.append(int("0xE901", 16))
	list_of_chars.append(int("0xE902", 16))
	list_of_chars.append(int("0xE903", 16))
	list_of_chars.append(int("0xE904", 16))
	list_of_chars.append(int("0xE905", 16))
	list_of_chars.append(int("0xE906", 16))
	list_of_chars.append(int("0xE907", 16))
	list_of_chars.append(int("0xE908", 16))
	list_of_chars.append(int("0xE909", 16))
	list_of_chars.append(int("0xE910", 16))
	list_of_chars.append(int("0xE911", 16))
	list_of_chars.append(int("0xE912", 16))
	list_of_chars.append(int("0xE913", 16))
	list_of_chars.append(int("0xE914", 16))
	list_of_chars.append(int("0xE915", 16))
	list_of_chars.append(int("0xE916", 16))
	list_of_chars.append(int("0xE917", 16))
	list_of_chars.append(int("0xE918", 16))
	list_of_chars.append(int("0xE919", 16))
	list_of_chars.append(int("0xE920", 16))
	list_of_chars.append(int("0xE921", 16))
	list_of_chars.append(int("0xE922", 16))
	list_of_chars.append(int("0xE923", 16))
	list_of_chars.append(int("0xE924", 16))
	list_of_chars.append(int("0xE925", 16))
	list_of_chars.append(int("0xE926", 16))
	list_of_chars.append(int("0xE927", 16))
	list_of_chars.append(int("0xE928", 16))
	list_of_chars.append(int("0xE929", 16))
	list_of_chars.append(int("0xE930", 16))
	list_of_chars.append(int("0xE931", 16))
	list_of_chars.append(int("0xE932", 16))
	list_of_chars.append(int("0xE933", 16))
	list_of_chars.append(int("0xE934", 16))
	list_of_chars.append(int("0xE935", 16))
	list_of_chars.append(int("0xE936", 16))
	list_of_chars.append(int("0xE937", 16))
	list_of_chars.append(int("0xE938", 16))
	list_of_chars.append(int("0xE939", 16))
	list_of_chars.append(int("0xE940", 16))
	list_of_chars.append(int("0xE941", 16))
	list_of_chars.append(int("0xE942", 16))
	list_of_chars.append(int("0xE943", 16))
	list_of_chars.append(int("0xE944", 16))
	list_of_chars.append(int("0xE945", 16))
	list_of_chars.append(int("0xE946", 16))
	list_of_chars.append(int("0xE947", 16))
	list_of_chars.append(int("0xE948", 16))
	list_of_chars.append(int("0xE949", 16))
	selector_x = 1
	selector_y = 1
	while True:
		blt.clear()
		blt.color('white')
		blt.puts(SCREEN_WIDTH//2-8, 5, '[font=log]Choose your avatar:')
		count = 0
		for x in range(5):
			for y in range(10):
				blt.put(27 + (x * 20), 15 + (y * 6), list_of_chars[count])
				count += 1
		blt.puts(SCREEN_WIDTH//2-23, SCREEN_HEIGHT-3, '[font=log]Up/down/left/right to select and enter to confirm')
		blt.color('red')
		blt.put(30 + ((selector_x - 1) * 20), 14 + ((selector_y - 1) * 6), chr(191))
		blt.put(30 + ((selector_x - 1) * 20), 15 + ((selector_y - 1) * 6), chr(179))
		blt.put(30 + ((selector_x - 1) * 20), 16 + ((selector_y - 1) * 6), chr(179))
		blt.put(30 + ((selector_x - 1) * 20), 17 + ((selector_y - 1) * 6), chr(179))
		blt.put(30 + ((selector_x - 1) * 20), 18 + ((selector_y - 1) * 6), chr(217))
		blt.put(29 + ((selector_x - 1) * 20), 18 + ((selector_y - 1) * 6), chr(196))
		blt.put(28 + ((selector_x - 1) * 20), 18 + ((selector_y - 1) * 6), chr(196))
		blt.put(27 + ((selector_x - 1) * 20), 18 + ((selector_y - 1) * 6), chr(196))
		blt.put(26 + ((selector_x - 1) * 20), 18 + ((selector_y - 1) * 6), chr(192))
		blt.put(26 + ((selector_x - 1) * 20), 17 + ((selector_y - 1) * 6), chr(179))
		blt.put(26 + ((selector_x - 1) * 20), 16 + ((selector_y - 1) * 6), chr(179))
		blt.put(26 + ((selector_x - 1) * 20), 15 + ((selector_y - 1) * 6), chr(179))
		blt.put(26 + ((selector_x - 1) * 20), 14 + ((selector_y - 1) * 6), chr(218))
		blt.put(27 + ((selector_x - 1) * 20), 14 + ((selector_y - 1) * 6), chr(196))
		blt.put(28 + ((selector_x - 1) * 20), 14 + ((selector_y - 1) * 6), chr(196))
		blt.put(29 + ((selector_x - 1) * 20), 14 + ((selector_y - 1) * 6), chr(196))
		blt.refresh()
		key = blt.read()
		if key == blt.TK_CLOSE:
			if game_state == 'playing': save_game()
			blt.close()
			sys.exit()
		if blt.check(blt.TK_CHAR):
			key_char = chr(blt.state(blt.TK_CHAR))
		else: 
			key_char = None
		if key == blt.TK_RETURN:
			break
		elif key in [blt.TK_UP, blt.TK_KP_8] or key_char == 'k':
			if selector_y > 1:
				selector_y -= 1
		elif key in [blt.TK_DOWN, blt.TK_KP_2] or key_char == 'j':
			if selector_y < 10:
				selector_y += 1
		elif key in [blt.TK_LEFT, blt.TK_KP_4] or key_char == 'h':
			if selector_x > 1:
				selector_x -= 1
		elif key in [blt.TK_RIGHT, blt.TK_KP_6] or key_char == 'l':
			if selector_x < 5:
				selector_x += 1
	selector = (selector_x - 1) * 10 + selector_y - 1
	return list_of_chars[selector]

def generate_character():
	global player, inventory, game_msgs, game_state, dungeon_level, dungeon_branch, fov_map, familiar
	player = None
	familiar = None
	blt.clear()
	blt.refresh()
	template = None
	choice = menu('Choose an option:', ['Custom character', 'Pre-made character'], 24)
	blt.clear()
	blt.refresh()
	if choice == None: return 'back-to-menu'
	
	if choice == 1:
		template_choice = menu('Choose a template:', ['Mountain Dwarf Fighter', 'Wood Elf Rogue', 'Stoutheart Cleric', 'Human Wizard', 'Tiefling Druid', 'Aasimar Warlock'], 26)
		if template_choice == 0: template = 'MDFi'
		if template_choice == 1: template = 'WERo'
		if template_choice == 2: template = 'StCl'
		if template_choice == 3: template = 'HuWi'
		if template_choice == 4: template = 'TiDr'
		if template_choice == 5: template = 'AaWa'
		if template_choice == None: return 'did-not-generate'
	blt.clear()
	blt.refresh()
	
	if template is not None:
		if template == 'MDFi': player_race = 'Mountain Dwarf'
		if template == 'WERo': player_race = 'Wood Elf'
		if template == 'StCl': player_race = 'Stoutheart'
		if template == 'HuWi': player_race = 'Human'
		if template == 'TiDr': player_race = 'Tiefling'
		if template == 'AaWa': player_race = 'Aasimar'
	else:
		race_choice = menu('Choose a race:', ['Human', 'Hill Dwarf', 'Mountain Dwarf', 'High Elf', 'Wood Elf', 'Lightfoot', 'Stoutheart', 'Half-elf', 'Half-orc', 'Tiefling', 'Aasimar', 'Kobold', 'Bugbear'], 24)
		if race_choice == 0: player_race = 'Human'
		if race_choice == 1: player_race = 'Hill Dwarf'
		if race_choice == 2: player_race = 'Mountain Dwarf'
		if race_choice == 3: player_race = 'High Elf'
		if race_choice == 4: player_race = 'Wood Elf' 
		if race_choice == 5: player_race = 'Lightfoot'
		if race_choice == 6: player_race = 'Stoutheart'
		if race_choice == 7: player_race = 'Half-elf'
		if race_choice == 8: player_race = 'Half-orc'
		if race_choice == 9: player_race = 'Tiefling'
		if race_choice == 10: player_race = 'Aasimar'
		if race_choice == 11: player_race = 'Kobold'
		if race_choice == 12: player_race = 'Bugbear'
		if race_choice == None: return 'did-not-generate'

	blt.clear()
	blt.refresh()
	
	if template is not None:
		if template == 'MDFi': player_class = 'Fighter'
		if template == 'WERo': player_class = 'Rogue'
		if template == 'StCl': player_class = 'Cleric'
		if template == 'HuWi': player_class = 'Wizard'
		if template == 'TiDr': player_class = 'Druid'
		if template == 'AaWa': player_class = 'Warlock'
	else:
		class_choice = menu('Choose a class:', ['Cleric', 'Fighter', 'Rogue', 'Wizard', 'Druid', 'Warlock'], 24)
		if class_choice == 0: player_class = 'Cleric'
		if class_choice == 1: player_class = 'Fighter'
		if class_choice == 2: player_class = 'Rogue'
		if class_choice == 3: player_class = 'Wizard'
		if class_choice == 4: player_class = 'Druid'
		if class_choice == 5: player_class = 'Warlock'
		if class_choice == None: return 'did-not-generate'
	blt.clear()
	blt.refresh()
	
	#background_choice = menu('Choose a background:', ['Acolyte', 'Criminal', 'Folk Hero', 'Noble', 'Sage', 'Soldier'], 24)
	#if background_choice == 0: player_background = 'Acolyte'
	#if background_choice == 1: player_background = 'Criminal' 
	#if background_choice == 2: player_background = 'Folk Hero'
	#if background_choice == 3: player_background = 'Noble'
	#if background_choice == 4: player_background = 'Sage'
	#if background_choice == 5: player_background = 'Soldier'
	
	#code for the menu to select attributes
	#it needs to loop around while the character selects from four options
	#and allocates the points among them, it's not very clean but who cares
	#i could define this menu in its own function but it'll only be used 
	#once so i'll just do it here and crappily, sorry!!!!!!!
	selector = 1
	points = 27
	str_select = 8
	dex_select = 8
	con_select = 8
	int_select = 8
	wis_select = 8
	cha_select = 8
	str_racial_bonus = 0
	dex_racial_bonus = 0
	con_racial_bonus = 0
	int_racial_bonus = 0
	wis_racial_bonus = 0
	cha_racial_bonus = 0
	point_cost = {8:0, 9:1, 10:1, 11:1, 12:1, 13:1, 14:2, 15:2} #point cost to go from each attribute to the next - total cost of 9 points to reach 15
	#vary attributes for race
	if player_race == 'Hill Dwarf':
		con_racial_bonus = 2
		wis_racial_bonus = 1
	if player_race == 'Mountain Dwarf':
		str_racial_bonus = 2
		con_racial_bonus = 2
	if player_race == 'High Elf':
		dex_racial_bonus = 2
		int_racial_bonus = 1
	if player_race == 'Wood Elf':
		dex_racial_bonus = 2
		wis_racial_bonus = 1
	if player_race == 'Lightfoot':
		dex_racial_bonus = 2
		cha_racial_bonus = 1
	if player_race == 'Stoutheart':
		dex_racial_bonus = 2
		con_racial_bonus = 1
	if player_race == 'Human':
		str_racial_bonus = 1
		dex_racial_bonus = 1
		con_racial_bonus = 1
		int_racial_bonus = 1
		wis_racial_bonus = 1
		cha_racial_bonus = 1
	if player_race == 'Half-elf':
		cha_racial_bonus = 2
		points += 2
	if player_race == 'Half-orc':
		str_racial_bonus = 2
		con_racial_bonus = 1
	if player_race == 'Tiefling':
		int_racial_bonus = 1
		cha_racial_bonus = 2
	if player_race == 'Aasimar':
		cha_racial_bonus = 2
	if player_race == 'Kobold':
		str_racial_bonus = -2
		dex_racial_bonus = 2
	if player_race == 'Bugbear':
		str_racial_bonus = 2
		dex_racial_bonus = 1
	if template is not None:
		if template == 'MDFi':
			str_select = 14
			dex_select = 10
			con_select = 15
			int_select = 8
			wis_select = 13
			cha_select = 12
		if template == 'WERo':
			str_select = 8
			dex_select = 15
			con_select = 12
			int_select = 14
			wis_select = 10
			cha_select = 13		
		if template == 'StCl':
			str_select = 12
			dex_select = 10
			con_select = 14
			int_select = 8
			wis_select = 15
			cha_select = 13
		if template == 'HuWi': 
			str_select = 8
			dex_select = 13
			con_select = 10
			int_select = 15
			wis_select = 12
			cha_select = 14
		if template == 'TiDr':
			str_select = 10
			dex_select = 13
			con_select = 14
			int_select = 12
			wis_select = 15
			cha_select = 8
		if template == 'AaWa':
			str_select = 8
			dex_select = 12
			con_select = 13
			int_select = 10
			wis_select = 14
			cha_select = 15
	else:
		while True:
			stat_change = 0
			blt.clear()
			blt.color('white')
			blt.puts(SCREEN_WIDTH//2-15, SCREEN_HEIGHT//2-10, '[font=log]Choose your attributes:')
			blt.puts(SCREEN_WIDTH//2-14, SCREEN_HEIGHT//2-5, '[font=log]Points remaining - ' + str(points))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2-2, '[font=log]Strength     - ' + str(str_select+str_racial_bonus))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2, '[font=log]Dexterity    - ' + str(dex_select+dex_racial_bonus))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2+2, '[font=log]Constitution - ' + str(con_select+con_racial_bonus))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2+4, '[font=log]Intelligence - ' + str(int_select+int_racial_bonus))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2+6, '[font=log]Wisdom       - ' + str(wis_select+wis_racial_bonus))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2+8, '[font=log]Charisma     - ' + str(cha_select+cha_racial_bonus))
			blt.puts(SCREEN_WIDTH//2-23, SCREEN_HEIGHT-3, '[font=log]Up/down to select and left/right to change values')
			blt.color('red')
			blt.puts(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 + (selector * 2) - 4, '[font=log]*')
			blt.refresh()
			key = blt.read()
			if key == blt.TK_CLOSE:
				if game_state == 'playing': save_game()
				blt.close()
				sys.exit()
			if blt.check(blt.TK_CHAR):
				key_char = chr(blt.state(blt.TK_CHAR))
			else: 
				key_char = None
			if key == blt.TK_ESCAPE:
				return 'did-not-generate'
			elif key == blt.TK_RETURN:
				break
			elif key in [blt.TK_UP, blt.TK_KP_8] or key_char == 'k':
				if selector > 1:
					selector = selector - 1
			elif key in [blt.TK_DOWN, blt.TK_KP_2] or key_char == 'j':
				if selector < 6:
					selector = selector + 1
			elif key in [blt.TK_LEFT, blt.TK_KP_4] or key_char == 'h':
				stat_change = -1
			elif key in [blt.TK_RIGHT, blt.TK_KP_6] or key_char == 'l':
				stat_change = 1	  
			if stat_change != 0:
				if selector == 1: 
					if str_select + stat_change >= 8 and str_select + stat_change <= 15: 
						if stat_change > 0: cost = point_cost[str_select + stat_change]
						if stat_change < 0: cost = point_cost[str_select]
						if (points >= cost and stat_change > 0) or stat_change < 0:
							str_select = str_select + stat_change
							points = points - (cost * stat_change)
				elif selector == 2: 
					if dex_select + stat_change >= 8 and dex_select + stat_change <= 15: 
						if stat_change > 0: cost = point_cost[dex_select + stat_change]
						if stat_change < 0: cost = point_cost[dex_select]
						if (points >= cost and stat_change > 0) or stat_change < 0:
							dex_select = dex_select + stat_change
							points = points - (cost * stat_change)
				elif selector == 3: 
					if con_select + stat_change >= 8 and con_select + stat_change <= 15: 
						if stat_change > 0: cost = point_cost[con_select + stat_change]
						if stat_change < 0: cost = point_cost[con_select]
						if (points >= cost and stat_change > 0) or stat_change < 0:
							con_select = con_select + stat_change
							points = points - (cost * stat_change)
				elif selector == 4: 
					if int_select + stat_change >= 8 and int_select + stat_change <= 15: 
						if stat_change > 0: cost = point_cost[int_select + stat_change]
						if stat_change < 0: cost = point_cost[int_select]
						if (points >= cost and stat_change > 0) or stat_change < 0:
							int_select = int_select + stat_change
							points = points - (cost * stat_change)
				elif selector == 5: 
					if wis_select + stat_change >= 8 and wis_select + stat_change <= 15: 
						if stat_change > 0: cost = point_cost[wis_select + stat_change]
						if stat_change < 0: cost = point_cost[wis_select]
						if (points >= cost and stat_change > 0) or stat_change < 0:
							wis_select = wis_select + stat_change
							points = points - (cost * stat_change)
				elif selector == 6: 
					if cha_select + stat_change >= 8 and cha_select + stat_change <= 15: 
						if stat_change > 0: cost = point_cost[cha_select + stat_change]
						if stat_change < 0: cost = point_cost[cha_select]
						if (points >= cost and stat_change > 0) or stat_change < 0:
							cha_select = cha_select + stat_change
							points = points - (cost * stat_change)
	blt.clear()
	blt.refresh()
	str_select += str_racial_bonus
	dex_select += dex_racial_bonus
	con_select += con_racial_bonus
	int_select += int_racial_bonus
	wis_select += wis_racial_bonus
	cha_select += cha_racial_bonus
	blt.refresh()
	
	proficiencies = []
	traits = []
	spells = []
	hp = 0
	bonus_hp = 0
	
	#apply race and class benefits
	if player_race == 'Hill Dwarf':
		proficiencies.append('battleaxe')
		proficiencies.append('handaxe')
		proficiencies.append('light hammer') 
		proficiencies.append('warhammer')
		traits.append('darkvision')
		traits.append('resilience')
		traits.append('dwarvern toughness')
		bonus_hp += 1 #effect of dwarvern toughness - easiest just to do it here for level 1
	if player_race == 'Mountain Dwarf':
		proficiencies.append('battleaxe')
		proficiencies.append('handaxe')
		proficiencies.append('light hammer') 
		proficiencies.append('warhammer')
		proficiencies.append('light armour') 
		proficiencies.append('medium armour')
		traits.append('darkvision')
		traits.append('resilience')
	if player_race == 'High Elf':
		proficiencies.append('perception')
		proficiencies.append('longsword')
		proficiencies.append('shortsword')
		proficiencies.append('shortbow')
		proficiencies.append('longbow')
		traits.append('darkvision')
		traits.append('sleep immune')
	if player_race == 'Wood Elf':
		proficiencies.append('perception')
		proficiencies.append('longsword')
		proficiencies.append('shortsword')
		proficiencies.append('shortbow')
		proficiencies.append('longbow')
		traits.append('mask of the wild')
		traits.append('darkvision')
		traits.append('sleep immune')
	if player_race == 'Lightfoot':
		traits.append('lucky')
		traits.append('brave')
		traits.append('stealthy')
	if player_race == 'Stoutheart':
		traits.append('lucky')
		traits.append('brave')
		traits.append('resilience')
	if player_race == 'Human':
		pass
	if player_race == 'Half-elf':
		traits.append('darkvision')
		traits.append('sleep immune')
	if player_race == 'Half-orc':
		traits.append('darkvision')
		traits.append('relentless')
		traits.append('savage')
	if player_race == 'Tiefling':
		traits.append('darkvision')
		traits.append('fire resistance')
	if player_race == 'Aasimar':
		traits.append('darkvision')
		spells.append('light')
		traits.append('healing hands')
		traits.append('necrotic resistance')
		traits.append('radiant resistance')
	if player_race == 'Kobold':
		traits.append('darkvision')
		traits.append('pack tactics')
	if player_race == 'Bugbear':
		traits.append('darkvision')
		traits.append('reach')
		traits.append('stealthy')
		
	if player_class == 'Cleric':
		hp += 8 
		bonus_hp += ABILITY_MODIFIER[con_select]
		proficiencies.append('light armour') 
		proficiencies.append('medium armour')
		proficiencies.append('heavy armour')
		proficiencies.append('shields') 
		proficiencies.append('simple weapons')
		proficiencies.append('magic')
		traits.append('wisdom save')
		traits.append('charisma save')
	
	if player_class == 'Fighter':
		hp += 10
		bonus_hp += ABILITY_MODIFIER[con_select]
		proficiencies.append('light armour') 
		proficiencies.append('medium armour')
		proficiencies.append('heavy armour') 
		proficiencies.append('shields')
		proficiencies.append('simple weapons')
		proficiencies.append('martial weapons')
		traits.append('strength save')
		traits.append('constitution save')
		traits.append('second wind')
		
	if player_class == 'Rogue':
		hp += 8
		bonus_hp + ABILITY_MODIFIER[con_select]
		proficiencies.append('light armour')
		proficiencies.append('simple weapons')
		proficiencies.append('hand crossbow')
		proficiencies.append('longsword')
		proficiencies.append('rapier')
		proficiencies.append('shortsword')
		traits.append('dexterity save')
		traits.append('intelligence save')
		traits.append('sneak attack')
	
	if player_class == 'Wizard':
		hp += 6 
		bonus_hp += ABILITY_MODIFIER[con_select]
		proficiencies.append('dagger')
		proficiencies.append('dart')
		proficiencies.append('sling')
		proficiencies.append('quarterstaff')
		proficiencies.append('light crossbow')
		proficiencies.append('magic')
		traits.append('intelligence save')
		traits.append('wisdom save')
		
	if player_class == 'Druid':
		hp += 8 
		bonus_hp += ABILITY_MODIFIER[con_select]
		proficiencies.append('light armour') 
		proficiencies.append('medium armour')
		proficiencies.append('shields')
		proficiencies.append('club')
		proficiencies.append('dagger')
		proficiencies.append('dart')
		proficiencies.append('javelin')
		proficiencies.append('mace')
		proficiencies.append('quarterstaff')
		proficiencies.append('scimitar')
		proficiencies.append('sickle')
		proficiencies.append('spear')
		proficiencies.append('magic')
		traits.append('intelligence save')
		traits.append('wisdom save')
		
	if player_class == 'Warlock':
		hp += 8 
		bonus_hp += ABILITY_MODIFIER[con_select]
		proficiencies.append('light armour') 
		proficiencies.append('simple weapons')
		proficiencies.append('magic')
		traits.append('charisma save')
		traits.append('wisdom save')
		
	if player_class == 'Fighter':
		if template is not None:
			if template == 'MDFi':
				style_choice = 2
		else:
			blt.clear()
			style_choice = menu('As a Fighter, choose a fighting style:', ['Archery', 'Defence', 'Dueling', 'Great weapon fighting', 'Protection', 'Two-weapon fighting'], 36)
		if style_choice == 0: proficiencies.append('archery')
		if style_choice == 1: proficiencies.append('defence')
		if style_choice == 2: proficiencies.append('dueling')
		if style_choice == 3: proficiencies.append('great weapon fighting')
		if style_choice == 4: proficiencies.append('protection')
		if style_choice == 5: proficiencies.append('two-weapon fighting')
		if style_choice == None: return 'did-not-generate'

	if player_race == 'High Elf': #racial bonus for high elf
		if template is not None:
			#no templates involve high elves just yet
			spell_choice = 'fire bolt'
		else:
			starting_cantrips = ['acid splash', 'chill touch', 'fire bolt', 'light', 'poison spray', 'ray of frost', 'shocking grasp']
			available_spells = []
			for spell in starting_cantrips:
				if spell not in spells: available_spells.append(spell)
			blt.clear()
			spell_choice = menu('As a High Elf, choose a cantrip:', available_spells, 30, return_option=True)
		if spell_choice == None: return 'did-not-generate'
		spells.append(spell_choice)
		blt.clear()
		blt.refresh()
		
	if player_class == 'Wizard':
		if template is not None:
			if template == 'HuWi':
				spells.append('acid splash')
				spells.append('light')
				spells.append('ray of frost')
				spells.append('magic missile')
				spells.append('sleep')
				spells.append('burning hands') 
		else:
			for _ in range(3): 
				starting_cantrips = ['acid splash', 'chill touch', 'fire bolt', 'light', 'poison spray', 'ray of frost', 'shocking grasp']
				available_spells = []
				for spell in starting_cantrips:
					if spell not in spells: available_spells.append(spell)
				spell_choice = menu('As a Wizard, choose 3 cantrips:', available_spells, 30, return_option=True)
				if spell_choice == None: return 'did-not-generate'
				spells.append(spell_choice)
				blt.clear()
				blt.refresh()
			for _ in range(3):
				starting_spells = ['burning hands', 'magic missile', 'mage armour', 'charm person', 'shield', 'sleep', 'thunderwave']
				available_spells = []
				for spell in starting_spells:
					if spell not in spells: available_spells.append(spell)
				spell_choice = menu('As a Wizard, choose 3 first level spells:', available_spells, 40, return_option=True)
				if spell_choice == None: return 'did-not-generate'
				spells.append(spell_choice)
				blt.clear()
				blt.refresh()
			
	if player_class == 'Cleric':
		cleric_spells = ['light', 'resistance', 'sacred flame', 'bless', 'cure wounds', 'healing word', 'inflict wounds', 'shield of faith']
		for spell in cleric_spells:
			spells.append(spell)
			
	if player_class == 'Druid':
		druid_spells = ['poison spray', 'resistance', 'charm person', 'cure wounds', 'healing word', 'thunderwave', 'fog cloud']
		for spell in druid_spells:
			spells.append(spell)
			
	if player_class == 'Warlock':
		if template is not None:
			if template == 'AaWa':
				spells.append('poison spray')
				spells.append('eldritch blast')
				spells.append('charm person')
				spells.append('hellish rebuke')
		else:
			for _ in range(2): 
				starting_cantrips = ['chill touch', 'poison spray', 'eldritch blast']
				available_spells = []
				for spell in starting_cantrips:
					if spell not in spells: available_spells.append(spell)
				spell_choice = menu('As a Warlock, choose 2 cantrips:', available_spells, 30, return_option=True)
				if spell_choice == None: return 'did-not-generate'
				spells.append(spell_choice)
				blt.clear()
				blt.refresh()
			for _ in range(2):
				starting_spells = ['charm person', 'hellish rebuke']
				available_spells = []
				for spell in starting_spells:
					if spell not in spells: available_spells.append(spell)
				spell_choice = menu('As a Warlock, choose 2 first level spells:', available_spells, 40, return_option=True)
				if spell_choice == None: return 'did-not-generate'
				spells.append(spell_choice)
				blt.clear()
				blt.refresh()

	#select the graphic for the player
	if template is not None:
		if template == 'MDFi':
			big_char = int("0xE901", 16)
		if template == 'WERo':
			big_char = int("0xE902", 16)
		if template == 'StCl':
			big_char = int("0xE900", 16)
		if template == 'HuWi': 
			big_char = int("0xE903", 16)
		if template == 'TiDr':
			big_char = int("0xE922", 16)
		if template == 'AaWa':
			big_char = int("0xE937", 16)
	else:
		big_char = select_avatar()
	#create object representing the player
	fighter_component = Fighter(hp=hp+bonus_hp, strength=str_select, dexterity=dex_select, constitution=con_select, intelligence=int_select, wisdom=wis_select, charisma=cha_select, clevel=1, proficiencies=proficiencies, traits=traits, spells=spells, xp=PLAYER_STARTING_XP, death_function=player_ko, race=player_race, role=player_class)
	fighter_component.base_max_hp = hp #store the value of this without any bonuses for recalculation later 
	fighter_component.monster = False
	fighter_component.faction = 'player'
	fighter_component.true_faction = 'player'
	if player_class == 'Wizard': fighter_component.casting_stat = 'intelligence'
	if player_class == 'Cleric': fighter_component.casting_stat = 'wisdom'
	if player_class == 'Druid': fighter_component.casting_stat = 'wisdom'
	if player_class == 'Warlock': fighter_component.casting_stat = 'charisma'
	
	### name generation
	tcod.namegen_parse('data/names.cfg')
	if player_race == 'Human': name = tcod.namegen_generate('human')
	if player_race == 'Hill Dwarf': name = tcod.namegen_generate('dwarf')
	if player_race == 'Mountain Dwarf': name = tcod.namegen_generate('dwarf')
	if player_race == 'High Elf': name = tcod.namegen_generate('elf')
	if player_race == 'Wood Elf': name = tcod.namegen_generate('elf')
	if player_race == 'Lightfoot': name = tcod.namegen_generate('halfling')
	if player_race == 'Stoutheart': name = tcod.namegen_generate('halfling')
	if player_race == 'Half-elf': 
		if random.randint(1, 2) == 2: #half elves can have either human or elven names
			name = tcod.namegen_generate('human')
		else:
			name = tcod.namegen_generate('elf')
	if player_race == 'Half-orc': name = tcod.namegen_generate('orc')
	if player_race == 'Tiefling': name = tcod.namegen_generate('infernal')
	if player_race == 'Aasimar': name = tcod.namegen_generate('human')
	if player_race == 'Kobold': name = tcod.namegen_generate('kobold')
	if player_race == 'Bugbear': name = tcod.namegen_generate('orc')
	
	### custom name generation 
	if template is None:
		while True:
			blt.clear()
			blt.refresh()
			name_choice = menu('Suggested name: ' + name, ['Accept suggested name', 'Generate new suggested name', 'Enter custom name'], 40)
			if name_choice == 0: break
			if name_choice == 1:
				if player_race == 'Human': name = tcod.namegen_generate('human')
				if player_race == 'Hill Dwarf': name = tcod.namegen_generate('dwarf')
				if player_race == 'Mountain Dwarf': name = tcod.namegen_generate('dwarf')
				if player_race == 'High Elf': name = tcod.namegen_generate('elf')
				if player_race == 'Wood Elf': name = tcod.namegen_generate('elf')
				if player_race == 'Lightfoot': name = tcod.namegen_generate('halfling')
				if player_race == 'Stoutheart': name = tcod.namegen_generate('halfling')
				if player_race == 'Half-elf': 
					if random.randint(1, 2) == 2: #half elves can have either human or elven names
						name = tcod.namegen_generate('human')
					else:
						name = tcod.namegen_generate('elf')
				if player_race == 'Half-orc': name = tcod.namegen_generate('orc')
				if player_race == 'Tiefling': name = tcod.namegen_generate('infernal')
				if player_race == 'Aasimar': name = tcod.namegen_generate('human')
				if player_race == 'Kobold': name = tcod.namegen_generate('kobold')
				if player_race == 'Bugbear': name = tcod.namegen_generate('orc')
			if name_choice == 2:
				name = text_input('Enter your name:', max_length=26)
				break
			if name_choice == None: return 'did-not-generate'
	
	player = Object(0, 0, '@', name, 'white', big_char=big_char, blocks=True, fighter=fighter_component)
	player.proper_noun = True
	
	### movement speed 
	if player_race in ['Lightfoot', 'Stoutheart', 'Hill Dwarf', 'Mountain Dwarf']: #base speed 25'
		player.move_cost = 120
	elif player_race in ['Wood Elf']: #base speed 35'
		player.move_cost = 85
	else: #everyone else, base speed 30'
		player.move_cost = 100 
 
	#create the list of game messages and their colours, starts empty
	game_msgs = []
	
	#starting inventory with some random choices
	
	if player_class == 'Cleric':
		obj = create_mace()
		player.inventory.append(obj)
		obj.equipment.equip(player)
		obj = create_leather_armour()
		player.inventory.append(obj)
		obj.equipment.equip(player)

	if player_class == 'Fighter':
		if 'two-weapon fighting' in proficiencies: #give two light weapons and equip one
			func_list = (create_dagger, create_shortsword, create_handaxe, create_club, create_scimitar)
			func = random.choice(func_list) 
			obj = func()
			player.inventory.append(obj)
			obj.equipment.equip(player)
			func = random.choice(func_list) 
			obj = func()
			player.inventory.append(obj)
		else:
			if player.fighter.strength >= player.fighter.dexterity: #choose starting kit based on main stat
				func_list = (create_longsword, create_battleaxe, create_spear) #list of starting main weapons for strong fighter
			else:
				func_list = (create_shortsword, create_scimitar, create_whip) #list of starting main weapons for high dex fighter
			func = random.choice(func_list) 
			obj = func()
			player.inventory.append(obj)
			obj.equipment.equip(player)
		if player.fighter.strength >= player.fighter.dexterity: #choose starting kit based on main stat
			obj = create_ring_mail_armour()
		else:
			obj = create_leather_armour()
		player.inventory.append(obj)
		obj.equipment.equip(player)
		obj = create_shortbow()
		player.inventory.append(obj)
		obj = create_arrows()
		player.inventory.append(obj)
		obj.equipment.equip(player)
		if 'protection' in proficiencies:
			obj = create_shield()
			player.inventory.append(obj)
			obj.equipment.equip(player)
			
	if player_class == 'Rogue':
		obj = create_dagger()
		player.inventory.append(obj)
		obj.equipment.equip(player)
		obj = create_blowgun()
		player.inventory.append(obj)
		obj = create_needles()
		player.inventory.append(obj)
		obj.equipment.equip(player)

	if player_class == 'Wizard':
		func_list = (create_quarterstaff, create_dagger)
		func = random.choice(func_list) 
		obj = func()
		player.inventory.append(obj)
		obj.equipment.equip(player)
			
	if player_class == 'Druid':
		func_list = (create_quarterstaff, create_club, create_scimitar)
		func = random.choice(func_list) 
		obj = func()
		player.inventory.append(obj)
		obj.equipment.equip(player)
		
	if player_class == 'Warlock':
		func_list = (create_quarterstaff, create_dagger)
		func = random.choice(func_list) 
		obj = func()
		player.inventory.append(obj)
		obj.equipment.equip(player)
			
	#all players get a torch and some food
	obj = create_torch()
	player.inventory.append(obj)
	obj = create_food_rations(5)
	player.inventory.append(obj)
	
	#all players get some gold based on charisma
	gold_amount = 100.0 + (ABILITY_MODIFIER[player.fighter.charisma] * 20)
	gold_amount = random.uniform(gold_amount - 5, gold_amount + 5)
	player.gold = round(gold_amount, 2)
	
	#items to be given for testing purposes
	#obj = create_helm_of_orcsblood()
	#player.inventory.append(obj)
	#obj = create_cloak_of_elvenkind()
	#player.inventory.append(obj)
	#obj = create_boots_of_elvenkind()
	#player.inventory.append(obj)
	#obj = create_boots_of_the_winterlands()
	#player.inventory.append(obj)
	#obj = create_wand_of_humblesongs_gift()
	#player.inventory.append(obj)
	
	#generate map (at this point it's not drawn to the screen)
	dungeon_level = STARTING_DUNGEON_LEVEL
	for branch in dungeon:
		if branch.name == STARTING_DUNGEON_BRANCH:
			dungeon_branch = branch
	make_map()
	fov_map = initialize_fov()
	fov_map_fam = initialize_fov()
	blt.clear()
	blt.refresh()

	#create a companion for the player - has to be done after map generation
	#code for the menu to select the party
	#much like the attribute selection process, this is a unique and messy implementation so i'm just doing it here
	if template is not None:
		guard = 0
		knight = 1
		thug = 0 
		acolyte = 1
		priest = 0
		mage = 0
	else:
		selector = 1
		points = 5
		guard = 0
		guard_cost = 1
		knight = 0
		knight_cost = 3
		thug = 0
		thug_cost = 2
		acolyte = 0
		acolyte_cost = 2
		priest = 0
		priest_cost = 4
		mage = 0
		mage_cost = 4
		while True:
			change = 0
			blt.clear()
			blt.color('white')
			blt.puts(SCREEN_WIDTH // 2 - 15, SCREEN_HEIGHT // 2 - 10, '[font=log]Choose your party:')
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2 - 5, '[font=log]Points remaining - ' + str(points))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2 - 2, '[font=log]Guard (1)   - ' + str(guard))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2, '[font=log]Knight (3)  - ' + str(knight))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2 + 2, '[font=log]Thug (2)    - ' + str(thug))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2 + 4, '[font=log]Acolyte (2) - ' + str(acolyte))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2 + 6, '[font=log]Priest (4)  - ' + str(priest))
			blt.puts(SCREEN_WIDTH // 2 - 14, SCREEN_HEIGHT // 2 + 8, '[font=log]Mage (4)    - ' + str(mage))
			blt.puts(SCREEN_WIDTH//2-23, SCREEN_HEIGHT-3, '[font=log]Up/down to select and left/right to change values')
			blt.color('red')
			blt.puts(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 - 4 + (selector*2), '[font=log]*')
			blt.refresh()
			key = blt.read()
			if key == blt.TK_CLOSE:
				if game_state == 'playing': save_game()
				blt.close()
				sys.exit()
			if blt.check(blt.TK_CHAR):
				key_char = chr(blt.state(blt.TK_CHAR))
			else: 
				key_char = None
			if key == blt.TK_ESCAPE:
				return 'did-not-generate'
			elif key == blt.TK_RETURN:
				break
			elif key in [blt.TK_UP, blt.TK_KP_8] or key_char == 'k':
				if selector > 1:
					selector = selector - 1
			elif key in [blt.TK_DOWN, blt.TK_KP_2] or key_char == 'j':
				if selector < 6:
					selector = selector + 1
			elif key in [blt.TK_LEFT, blt.TK_KP_4] or key_char == 'h':
				change = -1
			elif key in [blt.TK_RIGHT, blt.TK_KP_6] or key_char == 'l':
				change = 1	  
			if change != 0:
				if selector == 1: 
					if (points >= guard_cost and change > 0) or (guard > 0 and change < 0):
						guard = guard + change
						points = points - (guard_cost * change)
				elif selector == 2: 
					if (points >= knight_cost and change > 0) or (knight > 0 and change < 0):
						knight = knight + change
						points = points - (knight_cost * change)
				elif selector == 3: 
					if (points >= thug_cost and change > 0) or (thug > 0 and change < 0):
						thug = thug + change
						points = points - (thug_cost * change)
				elif selector == 4: 
					if (points >= acolyte_cost and change > 0) or (acolyte > 0 and change < 0):
						acolyte = acolyte + change
						points = points - (acolyte_cost * change)
				elif selector == 5: 
					if (points >= priest_cost and change > 0) or (priest > 0 and change < 0):
						priest = priest + change
						points = points - (priest_cost * change)
				elif selector == 6: 
					if (points >= mage_cost and change > 0) or (mage > 0 and change < 0):
						mage = mage + change
						points = points - (mage_cost * change)
		blt.refresh()
	
	companions = []
	for i in range(guard):
		companion = create_guard(0,0)
		companions.append(companion)
	for i in range(knight):
		companion = create_knight(0,0)
		companions.append(companion)
	for i in range(thug):
		companion = create_thug(0,0)
		companions.append(companion)
	for i in range(acolyte):
		companion = create_acolyte(0,0)
		companions.append(companion)	
	for i in range(priest):
		companion = create_priest(0,0)
		companions.append(companion)	
	for i in range(mage):
		companion = create_mage(0,0)
		companions.append(companion)	
	
	for companion in companions:
		companion.has_been_seen = True
		companion.fighter.faction = player.fighter.faction
		companion.fighter.true_faction = player.fighter.faction
		companion.old_ai = companion.ai #store the old ai to deal with instances of being dismissed
		if 'magic' in companion.fighter.proficiencies:
			companion_ai_component = CompanionMagicMonster(player, 5)
		else:
			companion_ai_component = CompanionMonster(player, 5)
		companion.ai = companion_ai_component
		companion_ai_component.owner = companion
		player.followers.append(companion)
		#actors.append(companion)
		
	#move_followers(player)

def reset_globals():
	global rest_counter, light_map, autoexplore_target, finished_exploring, last_target, last_spell, lookup_map
	
	light_map = [[0 for i in range(MAP_HEIGHT)] for j in range(MAP_WIDTH)]
	update_lookup_map()
	rest_counter = 0
	autoexplore_target = None
	finished_exploring = False
	last_target = None
	last_spell = None
	
def new_game():
	global player, inventory, game_msgs, game_state, dungeon_level, dungeon_branch, rest_counter, autoexplore_target, finished_exploring, display_mode, last_target, last_spell, macros, quests, global_cooldown, journal
	
	global_cooldown = STANDARD_TURN_LENGTH
	autoexplore_target = None
	finished_exploring = False
	last_target = None
	last_spell = None
	macros = [None, None, None, None, None, None, None, None, None, None]
	journal = []
	quests = master_quests.quests
	#clear save directory to avoid overlap
	if not os.path.isdir('save'): os.mkdir('save')
	folder = 'save/'
	files = os.listdir(folder)
	for the_file in files:
		file_path = os.path.join(folder, the_file)
		os.unlink(file_path)
	
	while True:
		result = generate_character()
		if result != 'did-not-generate': break
	if result != 'back-to-menu':
		game_state = 'playing'
		display_mode = 'ascii small'
		toggle_display_mode()
		rest_counter = 0
	 
		#a warm welcoming message!
		message('Welcome to The Red Prison!', 'red')
		message('Press "?" for help.', 'white')
		
		check_level_up()
		
		blt.clear()
		render_all()
		blt.refresh()
	
def change_level(links_to):
	#advance to the next level
	global dungeon_branch, dungeon_level, map, autoexplore_target, finished_exploring, fov_map, familiar, fov_map_fam

	target_branch = links_to[0]
	target_level = links_to[1]
	
	old_branch = dungeon_branch
	old_level = dungeon_level
	
	save_level() 
	autoexplore_target = None
	finished_exploring = False
	for branch in dungeon:
		if branch.name == target_branch:
			dungeon_branch = branch
	dungeon_level = target_level
	if os.path.exists('save/' + dungeon_branch.name + str(dungeon_level)):
		load_level()
		for item in items:
			if item.links_to is not None:
				if item.links_to[0] == old_branch.name and item.links_to[1] == old_level:
					player.x = item.x
					player.y = item.y
		if not dungeon_branch.overworld: move_followers(player)
	else:
		make_map(old_branch, old_level) #create a fresh new level!
		for item in items:
			if item.links_to is not None:
				if item.links_to[0] == old_branch.name and item.links_to[1] == old_level:
					player.x = item.x
					player.y = item.y
		if not dungeon_branch.overworld:
			for actor in player.followers:
				actors.append(actor)
			move_followers(player)
	fov_map = initialize_fov()
	if familiar: fov_map_fam = initialize_fov()
 
def initialize_fov():
	global fov_recompute
	fov_recompute = True
 
	#create the FOV map, according to the generated map
	fov = tcod.map.Map(MAP_WIDTH, MAP_HEIGHT)
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			fov.transparent[y, x] = not map[x][y].block_sight
			fov.walkable[y, x] = not map[x][y].blocked
	for effect in effects:
		if effect.effect:
			if effect.effect.block_sight:
				fov.transparent[effect.y, effect.x] = False
	return fov
	blt.clear()
	
def calculate_lowest_cooldown():
	global global_cooldown
	
	lowest_cooldown = STANDARD_TURN_LENGTH #we don't want this to go any longer than the standard turn because we will want to go through all conditions and effects every set number of ticks to trigger them
	
	if global_cooldown < lowest_cooldown: 
		lowest_cooldown = global_cooldown
	
	for actor in actors:
		if actor.cooldown < lowest_cooldown:
			lowest_cooldown = actor.cooldown
			
	return lowest_cooldown
			
def process_cooldowns(time_delay):
	global global_cooldown
	
	global_cooldown -= time_delay
	#if global_cooldown < 0: global_cooldown = 0 #this is just a safeguard against weird bugs
	for actor in actors:
		actor.cooldown -= time_delay
		#if actor.cooldown < 0: actor.cooldown = 0 #this is just a safeguard against weird bugs
		
def play_game():
	global key, game_state, rest_counter, global_cooldown, fov_map, familiar, fov_map_fam
 
	player_action = None
 
	#blt.clear()
	#render_all()
	#blt.refresh()
	key = blt.peek()
	#main loop
	while key != blt.TK_CLOSE:
		fov_map = initialize_fov()
		if familiar: fov_map_fam = initialize_fov()
		calc_light_map()
		update_lookup_map()
		#render the screen
		#blt.clear()
		#render_all()
		#blt.refresh()
 
		#level up if needed
		check_level_up()
 
		#erase all objects at their old locations, before they move
		for item in items:
			clear(item)
		for effect in effects:
			clear(effect)
		for actor in actors:
			clear(actor)
			actor.record_last_action(None)
			if actor.fighter:
				actor.fighter.opportunity_attack = False #reset this for the new round
				
		# this is where the work takes place in relation to maintaining the speed system
		
		time_delay = calculate_lowest_cooldown() #this should be the lowest cooldown variable amongst all of the actors - ignores conditions and effects
		process_cooldowns(time_delay) #this should reduce every single actor's value by that lowest value - it should result in the actors who can make a move having a zero value cooldown, the others have to wait
		
		#handle keys and exit game if needed
		
		if game_state == 'dead':
			player_action = handle_keys()
			if player_action == 'exit':
				delete_saved_game()
				break
				
		if player.cooldown <= 0:
			#render the screen only on player's turn
			blt.clear()
			render_all()
			blt.refresh()
			if game_state == 'playing':
				player.has_swapped = False
				player_action = handle_keys()
				if player_action != 'didnt-take-turn':
					player.add_cooldown()
				if player_action == 'exit':
					save_game()
					break
			if game_state == 'exploring' or game_state == 'autoplay': 
				if blt.has_input() is False:
					autoexplore()
					player.add_cooldown()
				else:
					game_state = 'playing'
				
		#let monsters take their turn
		if (game_state == 'playing' and player_action != 'didnt-take-turn') or game_state == 'resting' or game_state == 'exploring' or game_state == 'autoplay':
			for actor in actors:
				if actor.ai and actor.cooldown <= 0:
					#print(actor.name)
					actor.ai.take_turn()
					actor.add_cooldown()
				if global_cooldown <= 0:
					for item in actor.inventory:
						if item.item:
							for condition in item.item.conditions:
								#print(condition.name)
								condition.take_turn()
			if global_cooldown <= 0:
				for actor in actors:
					if actor.fighter:
						for condition in actor.fighter.conditions:
							#print(condition.name)
							condition.take_turn()
				for item in items:
					if item.item:
						for condition in item.item.conditions:
							#print(condition.name)
							condition.take_turn()
				for effect in effects:
					#print(effect.name)
					effect.effect.take_turn()
		
		if global_cooldown <= 0: #this means that we have triggered all of the conditions and effects which act on standard turn lengths, so we want to reset this
			global_cooldown = STANDARD_TURN_LENGTH
					
		if rest_counter > 0:
			rest_counter -= 1
			for actor in actors: #check to see if rest was disturbed
				if player.can_see_object(actor) and player != actor:
					if player.fighter.faction != actor.fighter.faction:
						message('Your rest is interrupted!')
						rest_counter = 0
			if rest_counter == 0:
				game_state = 'playing'
 
def main_menu():
	global game_state, display_mode, player, minimap, monster_func_list, npc_func_list, weapon_func_list, armour_func_list, misc_func_list, common_func_list, common_magic_func_list, rare_magic_func_list, fov_map
	
	display_mode = None
	
	minimap = Image.new("RGB", (MAP_WIDTH*2 + MINIMAP_OFFSET, MAP_HEIGHT*2 + MINIMAP_OFFSET), 0x000000)
	if not os.path.isdir('save'): os.mkdir('save')
	minimap.save('save/minimap.png')
	
	monster_func_list = [create_adult_red_dragon, create_air_elemental, create_allosaurus, create_allosaurus, create_ankylosaurus, create_ape, create_axe_beak, create_baboon, create_badger, create_banshee, create_bat, create_basilisk, create_black_bear, create_blink_dog, create_blood_hawk, create_boar, create_brown_bear, create_bugbear, create_cat, create_centaur, create_chimera, create_cockatrice, create_constrictor_snake, create_crab, create_crocodile, create_cyclops, create_death_dog, create_deer, create_dire_wolf, create_doppelganger, create_draft_horse, create_eagle, create_earth_elemental, create_elephant, create_elk, create_fire_elemental, create_fire_giant, create_flameskull, create_flesh_golem, create_flying_snake, create_flying_sword, create_frog, create_frost_giant, create_gargoyle, create_ghost, create_ghoul, create_giant_ape, create_giant_badger, create_giant_bat, create_giant_boar, create_giant_centipede, create_giant_constrictor_snake, create_giant_crab, create_giant_crocodile, create_giant_eagle, create_giant_elk, create_giant_fire_beetle, create_giant_frog, create_giant_goat, create_giant_hyena, create_giant_lizard, create_giant_octopus, create_giant_owl, create_giant_poisonous_snake, create_giant_rat, create_giant_scorpion, create_giant_sea_horse, create_giant_shark, create_giant_spider, create_giant_toad, create_giant_vulture, create_giant_wasp, create_giant_weasel, create_giant_wolf_spider, create_gnoll, create_goat, create_goblin, create_grick, create_griffon, create_harpy, create_hawk, create_hell_hound, create_hill_giant, create_hippogriff, create_hobgoblin, create_hunter_shark, create_hydra, create_hyena, create_jackal, create_killer_whale, create_kobold, create_lion, create_lizard, create_lizardfolk, create_mammoth, create_manticore, create_mastiff, create_medusa, create_merfolk, create_minotaur, create_mule, create_mummy, create_nothic, create_ochre_jelly, create_octopus, create_ogre, create_orc, create_owl, create_owlbear, create_panther, create_pegasus, create_phase_spider, create_plesiosaurus, create_poisonous_snake, create_polar_bear, create_pony, create_pteranodon, create_quipper, create_rat, create_raven, create_reef_shark, create_rhinoceros, create_riding_horse, create_sabre_toothed_tiger, create_satyr, create_scorpion, create_sea_horse, create_skeleton, create_spectator, create_spider, create_stirge, create_stone_golem, create_swarm_of_bats, create_swarm_of_insects, create_swarm_of_poisonous_snakes, create_swarm_of_quippers, create_swarm_of_rats, create_swarm_of_ravens, create_tiger, create_triceratops, create_troll, create_twig_blight, create_tyrannosaurus_rex, create_vulture, create_warhorse, create_water_elemental, create_weasel, create_werewolf, create_wight, create_winter_wolf, create_wolf, create_worg, create_wyvern, create_yeti, create_young_green_dragon, create_zombie]

	npc_func_list = [create_acolyte, create_archmage, create_assassin, create_bandit, create_bandit_captain, create_berserker, create_commoner, create_cultist, create_cult_fanatic, create_gladiator, create_guard, create_knight, create_mage, create_noble, create_priest, create_scout, create_spy, create_thug, create_tribal_warrior, create_veteran]

	weapon_func_list = [create_club, create_dagger, create_great_club, create_handaxe, create_javelin, create_light_hammer, create_mace, create_quarterstaff, create_sickle, create_spear, create_light_crossbow, create_dart, create_shortbow, create_sling, create_battleaxe, create_flail, create_glaive, create_greataxe, create_greatsword, create_halberd, create_longsword, create_maul, create_morningstar, create_pike, create_rapier, create_scimitar, create_shortsword, create_trident, create_war_pick, create_warhammer, create_whip, create_blowgun, create_hand_crossbow, create_heavy_crossbow, create_longbow]

	armour_func_list = [create_shield, create_padded_armour, create_leather_armour, create_studded_leather_armour, create_hide_armour, create_chain_shirt_armour, create_scale_mail_armour, create_breastplate_armour, create_half_plate_armour, create_ring_mail_armour, create_chain_mail_armour, create_splint_armour, create_plate_armour]

	misc_func_list = [create_torch, create_arrows, create_bolts, create_bullets, create_needles]

	common_func_list = [create_food_rations, create_gold]

	common_magic_func_list = [create_potion_of_healing, create_vial_of_acid, create_oil_of_sharpness, create_potion_of_giant_strength]

	rare_magic_func_list = [create_ring_of_protection, create_ring_of_invisibility, create_ring_of_poison_resistance, create_wand_of_web, create_wand_of_magic_missiles, create_wand_of_lightning_bolts, create_wand_of_fireballs, create_dwarven_plate_armour, create_dragon_scale_mail, create_elven_chain_mail_armour, create_mithral_armour, create_scimitar_of_speed, create_girdle_of_tenacity, create_amulet_of_detection, create_quickblade, create_amulet_of_mystic_insight, create_ring_of_the_forge, create_boots_of_the_winterlands, create_ring_of_the_dancer, create_cloak_of_elvenkind, create_boots_of_elvenkind, create_periapt_of_proof_against_poisons, create_gauntlets_of_ogrekind, create_helm_of_orcsblood, create_ring_of_the_drow, create_wand_of_humblesongs_gift]

	
	while True:

		blt.clear()
		blt.put(0, 0, background_menu_char)
		blt.color(blt.color_from_argb(150,255,255,255))
		blt.put(SCREEN_WIDTH//2-16, SCREEN_HEIGHT//2+4, black_menu_char)
		blt.color('white')
		blt.puts(SCREEN_WIDTH//2-23, SCREEN_HEIGHT-3, '[font=log]Press F1 in-game to switch between ascii/graphics')
		#show options and wait for the player's choice
		game_state = 'initialise'
		choice = menu(' THE RED PRISON ', ['Play a new game', 'Continue last game', 'Quit'], 24, can_exit_without_option=False, y_adjust=5, header_colour='red')
		blt.clear()
		blt.refresh()

		if choice == 0:	 #new game
			new_game()
			if player is not None: play_game()
		if choice == 1:	 #load last game
			#try:
			load_game()
			#except:
			#	simplemsgbox('No saved game to load',)
			#	continue
			play_game()
		elif choice == 2:  #quit
			break
 
blt.open()
# we need nonstandard size to fit the test map
blt.set("window: size=135x90, cellsize=auto, title='The Red Prison'; font: data/8x8.png, size=8x8; map font: data/16x16.png, size=16x16; log font: data/8x16.png, size=8x16")
blt.set('input: filter = [keyboard]')

# BACKGROUND

blt.set("0xE999: data/background.png")
background_menu_char = int("0xE999", 16)
blt.set("0xE998: data/black.png")
black_menu_char = int("0xE998", 16)

# ENVIRONMENT

blt.set("0xE001: data/tiles/light_wall.png, resize=24x24")
blt.set("0xE002: data/tiles/dark_wall.png, resize=24x24")
blt.set("0xE003: data/tiles/light_ground.png, resize=24x24")
blt.set("0xE004: data/tiles/dark_ground.png, resize=24x24")
blt.set("0xE005: data/tiles/closed_door.png, resize=24x24, transparent=black")
blt.set("0xE006: data/tiles/open_door.png, resize=24x24, transparent=black")
blt.set("0xE007: data/tiles/stairs_down.png, resize=24x24")
blt.set("0xE507: data/tiles/stairs_down.png, resize=12x12")
blt.set("0xE008: data/tiles/stairs_up.png, resize=24x24")
blt.set("0xE508: data/tiles/stairs_up.png, resize=12x12")
blt.set("0xE009: data/tiles/old_torch_wall.png, resize=24x24")
blt.set("0xE010: data/tiles/corpse.png, resize=24x24, transparent=black")
blt.set("0xE510: data/tiles/corpse.png, resize=12x12, transparent=black")
blt.set("0xE011: data/tiles/web.png, resize=24x24, transparent=black")
blt.set("0xE511: data/tiles/web.png, resize=12x12, transparent=black")
blt.set("0xE012: data/tiles/magic_blue.png, resize=24x24, transparent=black")
blt.set("0xE512: data/tiles/magic_blue.png, resize=12x12, transparent=black")
blt.set("0xE013: data/tiles/magic_green.png, resize=24x24, transparent=black")
blt.set("0xE513: data/tiles/magic_green.png, resize=12x12, transparent=black")
blt.set("0xE014: data/tiles/magic_purple.png, resize=24x24, transparent=black")
blt.set("0xE514: data/tiles/magic_purple.png, resize=12x12, transparent=black")
blt.set("0xE015: data/tiles/magic_red.png, resize=24x24, transparent=black")
blt.set("0xE515: data/tiles/magic_red.png, resize=12x12, transparent=black")
blt.set("0xE016: data/tiles/magic_yellow.png, resize=24x24, transparent=black")
blt.set("0xE516: data/tiles/magic_yellow.png, resize=12x12, transparent=black")
blt.set("0xE017: data/tiles/magic_grey.png, resize=24x24, transparent=black")
blt.set("0xE517: data/tiles/magic_grey.png, resize=12x12, transparent=black")
blt.set("0xE018: data/tiles/wall1.png, resize=24x24")
blt.set("0xE019: data/tiles/wall2.png, resize=24x24")
blt.set("0xE020: data/tiles/wall3.png, resize=24x24")
blt.set("0xE021: data/tiles/wall4.png, resize=24x24")
blt.set("0xE022: data/tiles/wall5.png, resize=24x24")
blt.set("0xE023: data/tiles/wall6.png, resize=24x24")
blt.set("0xE024: data/tiles/wall7.png, resize=24x24")
blt.set("0xE025: data/tiles/wall8.png, resize=24x24")
blt.set("0xE026: data/tiles/wall9.png, resize=24x24")
blt.set("0xE027: data/tiles/wall10.png, resize=24x24")
blt.set("0xE028: data/tiles/wall11.png, resize=24x24")
blt.set("0xE029: data/tiles/wall12.png, resize=24x24")
blt.set("0xE030: data/tiles/wall13.png, resize=24x24")
blt.set("0xE031: data/tiles/wall14.png, resize=24x24")
blt.set("0xE032: data/tiles/wall15.png, resize=24x24")
blt.set("0xE033: data/tiles/wall16.png, resize=24x24")
blt.set("0xE034: data/tiles/town_wall1.png, resize=24x24")
blt.set("0xE035: data/tiles/town_wall2.png, resize=24x24")
blt.set("0xE036: data/tiles/town_wall3.png, resize=24x24")
blt.set("0xE037: data/tiles/town_wall4.png, resize=24x24")
blt.set("0xE038: data/tiles/red_wall1.png, resize=24x24")
blt.set("0xE039: data/tiles/red_wall2.png, resize=24x24")
blt.set("0xE040: data/tiles/red_wall3.png, resize=24x24")
blt.set("0xE041: data/tiles/red_wall4.png, resize=24x24")
blt.set("0xE042: data/tiles/red_wall5.png, resize=24x24")
blt.set("0xE043: data/tiles/red_wall6.png, resize=24x24")
blt.set("0xE044: data/tiles/red_wall7.png, resize=24x24")
blt.set("0xE045: data/tiles/red_wall8.png, resize=24x24")
blt.set("0xE046: data/tiles/red_wall9.png, resize=24x24")
blt.set("0xE047: data/tiles/red_wall10.png, resize=24x24")
blt.set("0xE048: data/tiles/torch_wall.png, resize=24x24, transparent=black")
blt.set("0xE049: data/tiles/tree1.png, resize=24x24")
blt.set("0xE050: data/tiles/tree2.png, resize=24x24")
blt.set("0xE051: data/tiles/mountain1.png, resize=24x24")
blt.set("0xE052: data/tiles/mountain2.png, resize=24x24")
blt.set("0xE053: data/tiles/mountain3.png, resize=24x24")
blt.set("0xE054: data/tiles/mountain4.png, resize=24x24")
blt.set("0xE055: data/tiles/water1.png, resize=24x24")
blt.set("0xE056: data/tiles/water2.png, resize=24x24")
blt.set("0xE057: data/tiles/shrub1.png, resize=24x24")
blt.set("0xE058: data/tiles/shrub2.png, resize=24x24")
blt.set("0xE059: data/tiles/ground1.png, resize=24x24")
blt.set("0xE060: data/tiles/ground2.png, resize=24x24")
blt.set("0xE061: data/tiles/ground3.png, resize=24x24")
blt.set("0xE062: data/tiles/grass1.png, resize=24x24")
blt.set("0xE063: data/tiles/grass2.png, resize=24x24")
blt.set("0xE064: data/tiles/grass3.png, resize=24x24")
blt.set("0xE065: data/tiles/indoors1.png, resize=24x24")
blt.set("0xE066: data/tiles/castle.png, resize=24x24, transparent=white")
blt.set("0xE566: data/tiles/castle.png, resize=12x12, transparent=white")
blt.set("0xE067: data/tiles/village.png, resize=24x24, transparent=white")
blt.set("0xE567: data/tiles/village.png, resize=12x12, transparent=white")
blt.set("0xE068: data/tiles/cave.png, resize=24x24, transparent=white")
blt.set("0xE568: data/tiles/cave.png, resize=12x12, transparent=white")



# PLAYER

blt.set("0xE900: data/tiles/player_1.png, resize=24x24, transparent=black")
blt.set("0xE901: data/tiles/player_2.png, resize=24x24, transparent=black")
blt.set("0xE902: data/tiles/player_3.png, resize=24x24, transparent=black")
blt.set("0xE903: data/tiles/player_4.png, resize=24x24, transparent=black")
blt.set("0xE904: data/tiles/player_5.png, resize=24x24, transparent=black")
blt.set("0xE905: data/tiles/player_6.png, resize=24x24, transparent=black")
blt.set("0xE906: data/tiles/player_7.png, resize=24x24, transparent=black")
blt.set("0xE907: data/tiles/player_8.png, resize=24x24, transparent=black")
blt.set("0xE908: data/tiles/player_9.png, resize=24x24, transparent=black")
blt.set("0xE909: data/tiles/player_10.png, resize=24x24, transparent=black")
blt.set("0xE910: data/tiles/player_11.png, resize=24x24, transparent=black")
blt.set("0xE911: data/tiles/player_12.png, resize=24x24, transparent=black")
blt.set("0xE912: data/tiles/player_13.png, resize=24x24, transparent=black")
blt.set("0xE913: data/tiles/player_14.png, resize=24x24, transparent=black")
blt.set("0xE914: data/tiles/player_15.png, resize=24x24, transparent=black")
blt.set("0xE915: data/tiles/player_16.png, resize=24x24, transparent=black")
blt.set("0xE916: data/tiles/player_17.png, resize=24x24, transparent=black")
blt.set("0xE917: data/tiles/player_18.png, resize=24x24, transparent=black")
blt.set("0xE918: data/tiles/player_19.png, resize=24x24, transparent=black")
blt.set("0xE919: data/tiles/player_20.png, resize=24x24, transparent=black")
blt.set("0xE920: data/tiles/player_21.png, resize=24x24, transparent=black")
blt.set("0xE921: data/tiles/player_22.png, resize=24x24, transparent=black")
blt.set("0xE922: data/tiles/player_23.png, resize=24x24, transparent=black")
blt.set("0xE923: data/tiles/player_24.png, resize=24x24, transparent=black")
blt.set("0xE924: data/tiles/player_25.png, resize=24x24, transparent=black")
blt.set("0xE925: data/tiles/player_26.png, resize=24x24, transparent=black")
blt.set("0xE926: data/tiles/player_27.png, resize=24x24, transparent=black")
blt.set("0xE927: data/tiles/player_28.png, resize=24x24, transparent=black")
blt.set("0xE928: data/tiles/player_29.png, resize=24x24, transparent=black")
blt.set("0xE929: data/tiles/player_30.png, resize=24x24, transparent=black")
blt.set("0xE930: data/tiles/player_31.png, resize=24x24, transparent=black")
blt.set("0xE931: data/tiles/player_32.png, resize=24x24, transparent=black")
blt.set("0xE932: data/tiles/player_33.png, resize=24x24, transparent=black")
blt.set("0xE933: data/tiles/player_34.png, resize=24x24, transparent=black")
blt.set("0xE934: data/tiles/player_35.png, resize=24x24, transparent=black")
blt.set("0xE935: data/tiles/player_36.png, resize=24x24, transparent=black")
blt.set("0xE936: data/tiles/player_37.png, resize=24x24, transparent=black")
blt.set("0xE937: data/tiles/player_38.png, resize=24x24, transparent=black")
blt.set("0xE938: data/tiles/player_39.png, resize=24x24, transparent=black")
blt.set("0xE939: data/tiles/player_40.png, resize=24x24, transparent=black")
blt.set("0xE940: data/tiles/player_41.png, resize=24x24, transparent=black")
blt.set("0xE941: data/tiles/player_42.png, resize=24x24, transparent=black")
blt.set("0xE942: data/tiles/player_43.png, resize=24x24, transparent=black")
blt.set("0xE943: data/tiles/player_44.png, resize=24x24, transparent=black")
blt.set("0xE944: data/tiles/player_45.png, resize=24x24, transparent=black")
blt.set("0xE945: data/tiles/player_46.png, resize=24x24, transparent=black")
blt.set("0xE946: data/tiles/player_47.png, resize=24x24, transparent=black")
blt.set("0xE947: data/tiles/player_48.png, resize=24x24, transparent=black")
blt.set("0xE948: data/tiles/player_49.png, resize=24x24, transparent=black")
blt.set("0xE949: data/tiles/player_50.png, resize=24x24, transparent=black")

# MONSTERS

blt.set("0xE104: data/tiles/adult_red_dragon.png, resize=24x24, transparent=black")
blt.set("0xE105: data/tiles/air_elemental.png, resize=24x24, transparent=black")
blt.set("0xE106: data/tiles/allosaurus.png, resize=24x24, transparent=black")
blt.set("0xE107: data/tiles/animated_armour.png, resize=24x24, transparent=black")
blt.set("0xE108: data/tiles/ankylosaurus.png, resize=24x24, transparent=black")
blt.set("0xE109: data/tiles/ape.png, resize=24x24, transparent=black")
blt.set("0xE110: data/tiles/awakened_shrub.png, resize=24x24, transparent=black")
blt.set("0xE111: data/tiles/awakened_tree.png, resize=24x24, transparent=black")
blt.set("0xE112: data/tiles/axe_beak.png, resize=24x24, transparent=black")
blt.set("0xE113: data/tiles/baboon.png, resize=24x24, transparent=black")
blt.set("0xE114: data/tiles/badger.png, resize=24x24, transparent=black")
blt.set("0xE115: data/tiles/banshee.png, resize=24x24, transparent=black")
blt.set("0xE116: data/tiles/bat.png, resize=24x24, transparent=black")
blt.set("0xE117: data/tiles/basilisk.png, resize=24x24, transparent=black")
blt.set("0xE118: data/tiles/black_bear.png, resize=24x24, transparent=black")
blt.set("0xE119: data/tiles/blink_dog.png, resize=24x24, transparent=black")
blt.set("0xE120: data/tiles/blood_hawk.png, resize=24x24, transparent=black")
blt.set("0xE121: data/tiles/boar.png, resize=24x24, transparent=black")
blt.set("0xE122: data/tiles/brown_bear.png, resize=24x24, transparent=black")
blt.set("0xE123: data/tiles/bugbear.png, resize=24x24, transparent=black")
blt.set("0xE124: data/tiles/camel.png, resize=24x24, transparent=black")
blt.set("0xE125: data/tiles/cat.png, resize=24x24, transparent=black")
blt.set("0xE126: data/tiles/centaur.png, resize=24x24, transparent=black")
blt.set("0xE127: data/tiles/chimera.png, resize=24x24, transparent=black")
blt.set("0xE128: data/tiles/cockatrice.png, resize=24x24, transparent=black")
blt.set("0xE129: data/tiles/constrictor_snake.png, resize=24x24, transparent=black")
blt.set("0xE130: data/tiles/crab.png, resize=24x24, transparent=black")
blt.set("0xE131: data/tiles/crocodile.png, resize=24x24, transparent=black")
blt.set("0xE132: data/tiles/cyclops.png, resize=24x24, transparent=black")
blt.set("0xE133: data/tiles/death_dog.png, resize=24x24, transparent=black")
blt.set("0xE134: data/tiles/deer.png, resize=24x24, transparent=black")
blt.set("0xE135: data/tiles/dire_wolf.png, resize=24x24, transparent=black")
blt.set("0xE136: data/tiles/doppelganger.png, resize=24x24, transparent=black")
blt.set("0xE137: data/tiles/draft_horse.png, resize=24x24, transparent=black")
blt.set("0xE138: data/tiles/eagle.png, resize=24x24, transparent=black")
blt.set("0xE139: data/tiles/earth_elemental.png, resize=24x24, transparent=black")
blt.set("0xE140: data/tiles/elephant.png, resize=24x24, transparent=black")
blt.set("0xE141: data/tiles/elk.png, resize=24x24, transparent=black")
blt.set("0xE142: data/tiles/fire_elemental.png, resize=24x24, transparent=black")
blt.set("0xE143: data/tiles/fire_giant.png, resize=24x24, transparent=black")
blt.set("0xE144: data/tiles/flameskull.png, resize=24x24, transparent=black")
blt.set("0xE145: data/tiles/flesh_golem.png, resize=24x24, transparent=black")
blt.set("0xE146: data/tiles/flying_snake.png, resize=24x24, transparent=black")
blt.set("0xE147: data/tiles/flying_sword.png, resize=24x24, transparent=black")
blt.set("0xE148: data/tiles/frog.png, resize=24x24, transparent=black")
blt.set("0xE149: data/tiles/frost_giant.png, resize=24x24, transparent=black")
blt.set("0xE150: data/tiles/gargoyle.png, resize=24x24, transparent=black")
blt.set("0xE151: data/tiles/ghost.png, resize=24x24, transparent=black")
blt.set("0xE152: data/tiles/ghoul.png, resize=24x24, transparent=black")
blt.set("0xE153: data/tiles/giant_ape.png, resize=24x24, transparent=black")
blt.set("0xE154: data/tiles/giant_badger.png, resize=24x24, transparent=black")
blt.set("0xE155: data/tiles/giant_bat.png, resize=24x24, transparent=black")
blt.set("0xE156: data/tiles/giant_boar.png, resize=24x24, transparent=black")
blt.set("0xE157: data/tiles/giant_centipede.png, resize=24x24, transparent=black")
blt.set("0xE158: data/tiles/giant_constrictor_snake.png, resize=24x24, transparent=black")
blt.set("0xE159: data/tiles/giant_crab.png, resize=24x24, transparent=black")
blt.set("0xE160: data/tiles/giant_crocodile.png, resize=24x24, transparent=black")
blt.set("0xE161: data/tiles/giant_eagle.png, resize=24x24, transparent=black")
blt.set("0xE162: data/tiles/giant_elk.png, resize=24x24, transparent=black")
blt.set("0xE163: data/tiles/giant_fire_beetle.png, resize=24x24, transparent=black")
blt.set("0xE164: data/tiles/giant_frog.png, resize=24x24, transparent=black")
blt.set("0xE165: data/tiles/giant_goat.png, resize=24x24, transparent=black")
blt.set("0xE166: data/tiles/giant_hyena.png, resize=24x24, transparent=black")
blt.set("0xE167: data/tiles/giant_lizard.png, resize=24x24, transparent=black")
blt.set("0xE168: data/tiles/giant_octopus.png, resize=24x24, transparent=black")
blt.set("0xE169: data/tiles/giant_owl.png, resize=24x24, transparent=black")
blt.set("0xE170: data/tiles/giant_poisonous_snake.png, resize=24x24, transparent=black")
blt.set("0xE171: data/tiles/giant_rat.png, resize=24x24, transparent=black")
blt.set("0xE172: data/tiles/giant_scorpion.png, resize=24x24, transparent=black")
blt.set("0xE173: data/tiles/giant_sea_horse.png, resize=24x24, transparent=black")
blt.set("0xE174: data/tiles/giant_shark.png, resize=24x24, transparent=black")
blt.set("0xE175: data/tiles/giant_spider.png, resize=24x24, transparent=black")
blt.set("0xE176: data/tiles/giant_toad.png, resize=24x24, transparent=black")
blt.set("0xE177: data/tiles/giant_vulture.png, resize=24x24, transparent=black")
blt.set("0xE178: data/tiles/giant_wasp.png, resize=24x24, transparent=black")
blt.set("0xE179: data/tiles/giant_weasel.png, resize=24x24, transparent=black")
blt.set("0xE180: data/tiles/giant_wolf_spider.png, resize=24x24, transparent=black")
blt.set("0xE181: data/tiles/gnoll.png, resize=24x24, transparent=black")
blt.set("0xE182: data/tiles/goat.png, resize=24x24, transparent=black")
blt.set("0xE183: data/tiles/goblin.png, resize=24x24, transparent=black")
blt.set("0xE184: data/tiles/grick.png, resize=24x24, transparent=black")
blt.set("0xE185: data/tiles/griffon.png, resize=24x24, transparent=black")
blt.set("0xE186: data/tiles/harpy.png, resize=24x24, transparent=black")
blt.set("0xE187: data/tiles/hawk.png, resize=24x24, transparent=black")
blt.set("0xE188: data/tiles/hell_hound.png, resize=24x24, transparent=black")
blt.set("0xE189: data/tiles/hill_giant.png, resize=24x24, transparent=black")
blt.set("0xE190: data/tiles/hippogriff.png, resize=24x24, transparent=black")
blt.set("0xE191: data/tiles/hobgoblin.png, resize=24x24, transparent=black")
blt.set("0xE192: data/tiles/hunter_shark.png, resize=24x24, transparent=black")
blt.set("0xE193: data/tiles/hydra.png, resize=24x24, transparent=black")
blt.set("0xE194: data/tiles/hyena.png, resize=24x24, transparent=black")
blt.set("0xE195: data/tiles/jackal.png, resize=24x24, transparent=black")
blt.set("0xE196: data/tiles/killer_whale.png, resize=24x24, transparent=black")
blt.set("0xE197: data/tiles/kobold.png, resize=24x24, transparent=black")
blt.set("0xE198: data/tiles/lion.png, resize=24x24, transparent=black")
blt.set("0xE199: data/tiles/lizard.png, resize=24x24, transparent=black")
blt.set("0xE200: data/tiles/lizardfolk.png, resize=24x24, transparent=black")
blt.set("0xE201: data/tiles/mammoth.png, resize=24x24, transparent=black")
blt.set("0xE202: data/tiles/manticore.png, resize=24x24, transparent=black")
blt.set("0xE203: data/tiles/mastiff.png, resize=24x24, transparent=black")
blt.set("0xE204: data/tiles/medusa.png, resize=24x24, transparent=black")
blt.set("0xE205: data/tiles/merfolk.png, resize=24x24, transparent=black")
blt.set("0xE206: data/tiles/minotaur.png, resize=24x24, transparent=black")
blt.set("0xE207: data/tiles/mule.png, resize=24x24, transparent=black")
blt.set("0xE208: data/tiles/mummy.png, resize=24x24, transparent=black")
blt.set("0xE209: data/tiles/nothic.png, resize=24x24, transparent=black")
blt.set("0xE210: data/tiles/ochre_jelly.png, resize=24x24, transparent=black")
blt.set("0xE211: data/tiles/octopus.png, resize=24x24, transparent=black")
blt.set("0xE212: data/tiles/ogre.png, resize=24x24, transparent=black")
blt.set("0xE213: data/tiles/orc.png, resize=24x24, transparent=black")
blt.set("0xE214: data/tiles/owl.png, resize=24x24, transparent=black")
blt.set("0xE215: data/tiles/owlbear.png, resize=24x24, transparent=black")
blt.set("0xE216: data/tiles/panther.png, resize=24x24, transparent=black")
blt.set("0xE217: data/tiles/pegasus.png, resize=24x24, transparent=black")
blt.set("0xE218: data/tiles/phase_spider.png, resize=24x24, transparent=black")
blt.set("0xE219: data/tiles/plesiosaurus.png, resize=24x24, transparent=black")
blt.set("0xE220: data/tiles/poisonous_snake.png, resize=24x24, transparent=black")
blt.set("0xE221: data/tiles/polar_bear.png, resize=24x24, transparent=black")
blt.set("0xE222: data/tiles/pony.png, resize=24x24, transparent=black")
blt.set("0xE223: data/tiles/pteranodon.png, resize=24x24, transparent=black")
blt.set("0xE224: data/tiles/quipper.png, resize=24x24, transparent=black")
blt.set("0xE225: data/tiles/rat.png, resize=24x24, transparent=black")
blt.set("0xE226: data/tiles/raven.png, resize=24x24, transparent=black")
blt.set("0xE227: data/tiles/reef_shark.png, resize=24x24, transparent=black")
blt.set("0xE228: data/tiles/rhinoceros.png, resize=24x24, transparent=black")
blt.set("0xE229: data/tiles/riding_horse.png, resize=24x24, transparent=black")
blt.set("0xE230: data/tiles/sabre-toothed_tiger.png, resize=24x24, transparent=black")
blt.set("0xE231: data/tiles/satyr.png, resize=24x24, transparent=black")
blt.set("0xE232: data/tiles/scorpion.png, resize=24x24, transparent=black")
blt.set("0xE233: data/tiles/sea_horse.png, resize=24x24, transparent=black")
blt.set("0xE234: data/tiles/skeleton.png, resize=24x24, transparent=black")
blt.set("0xE235: data/tiles/spectator.png, resize=24x24, transparent=black")
blt.set("0xE236: data/tiles/spider.png, resize=24x24, transparent=black")
blt.set("0xE237: data/tiles/stirge.png, resize=24x24, transparent=black")
blt.set("0xE238: data/tiles/stone_golem.png, resize=24x24, transparent=black")
blt.set("0xE239: data/tiles/swarm_of_bats.png, resize=24x24, transparent=black")
blt.set("0xE240: data/tiles/swarm_of_insects.png, resize=24x24, transparent=black")
blt.set("0xE241: data/tiles/swarm_of_poisonous_snakes.png, resize=24x24, transparent=black")
blt.set("0xE242: data/tiles/swarm_of_quippers.png, resize=24x24, transparent=black")
blt.set("0xE243: data/tiles/swarm_of_rats.png, resize=24x24, transparent=black")
blt.set("0xE244: data/tiles/swarm_of_ravens.png, resize=24x24, transparent=black")
blt.set("0xE245: data/tiles/tiger.png, resize=24x24, transparent=black")
blt.set("0xE246: data/tiles/triceratops.png, resize=24x24, transparent=black")
blt.set("0xE247: data/tiles/troll.png, resize=24x24, transparent=black")
blt.set("0xE248: data/tiles/twig_blight.png, resize=24x24, transparent=black")
blt.set("0xE249: data/tiles/tyrannosaurus_rex.png, resize=24x24, transparent=black")
blt.set("0xE250: data/tiles/vulture.png, resize=24x24, transparent=black")
blt.set("0xE251: data/tiles/warhorse.png, resize=24x24, transparent=black")
blt.set("0xE252: data/tiles/water_elemental.png, resize=24x24, transparent=black")
blt.set("0xE253: data/tiles/weasel.png, resize=24x24, transparent=black")
blt.set("0xE254: data/tiles/werewolf.png, resize=24x24, transparent=black")
blt.set("0xE255: data/tiles/wight.png, resize=24x24, transparent=black")
blt.set("0xE256: data/tiles/winter_wolf.png, resize=24x24, transparent=black")
blt.set("0xE257: data/tiles/wolf.png, resize=24x24, transparent=black")
blt.set("0xE258: data/tiles/worg.png, resize=24x24, transparent=black")
blt.set("0xE259: data/tiles/wyvern.png, resize=24x24, transparent=black")
blt.set("0xE260: data/tiles/yeti.png, resize=24x24, transparent=black")
blt.set("0xE261: data/tiles/young_green_dragon.png, resize=24x24, transparent=black")
blt.set("0xE262: data/tiles/zombie.png, resize=24x24, transparent=black")

# SMALL MONSTERS

blt.set("0xE604: data/tiles/adult_red_dragon.png, resize=12x12, transparent=black")
blt.set("0xE605: data/tiles/air_elemental.png, resize=12x12, transparent=black")
blt.set("0xE606: data/tiles/allosaurus.png, resize=12x12, transparent=black")
blt.set("0xE607: data/tiles/animated_armour.png, resize=12x12, transparent=black")
blt.set("0xE608: data/tiles/ankylosaurus.png, resize=12x12, transparent=black")
blt.set("0xE609: data/tiles/ape.png, resize=12x12, transparent=black")
blt.set("0xE610: data/tiles/awakened_shrub.png, resize=12x12, transparent=black")
blt.set("0xE611: data/tiles/awakened_tree.png, resize=12x12, transparent=black")
blt.set("0xE612: data/tiles/axe_beak.png, resize=12x12, transparent=black")
blt.set("0xE613: data/tiles/baboon.png, resize=12x12, transparent=black")
blt.set("0xE614: data/tiles/badger.png, resize=12x12, transparent=black")
blt.set("0xE615: data/tiles/banshee.png, resize=12x12, transparent=black")
blt.set("0xE616: data/tiles/bat.png, resize=12x12, transparent=black")
blt.set("0xE617: data/tiles/basilisk.png, resize=12x12, transparent=black")
blt.set("0xE618: data/tiles/black_bear.png, resize=12x12, transparent=black")
blt.set("0xE619: data/tiles/blink_dog.png, resize=12x12, transparent=black")
blt.set("0xE620: data/tiles/blood_hawk.png, resize=12x12, transparent=black")
blt.set("0xE621: data/tiles/boar.png, resize=12x12, transparent=black")
blt.set("0xE622: data/tiles/brown_bear.png, resize=12x12, transparent=black")
blt.set("0xE623: data/tiles/bugbear.png, resize=12x12, transparent=black")
blt.set("0xE624: data/tiles/camel.png, resize=12x12, transparent=black")
blt.set("0xE625: data/tiles/cat.png, resize=12x12, transparent=black")
blt.set("0xE626: data/tiles/centaur.png, resize=12x12, transparent=black")
blt.set("0xE627: data/tiles/chimera.png, resize=12x12, transparent=black")
blt.set("0xE628: data/tiles/cockatrice.png, resize=12x12, transparent=black")
blt.set("0xE629: data/tiles/constrictor_snake.png, resize=12x12, transparent=black")
blt.set("0xE630: data/tiles/crab.png, resize=12x12, transparent=black")
blt.set("0xE631: data/tiles/crocodile.png, resize=12x12, transparent=black")
blt.set("0xE632: data/tiles/cyclops.png, resize=12x12, transparent=black")
blt.set("0xE633: data/tiles/death_dog.png, resize=12x12, transparent=black")
blt.set("0xE634: data/tiles/deer.png, resize=12x12, transparent=black")
blt.set("0xE635: data/tiles/dire_wolf.png, resize=12x12, transparent=black")
blt.set("0xE636: data/tiles/doppelganger.png, resize=12x12, transparent=black")
blt.set("0xE637: data/tiles/draft_horse.png, resize=12x12, transparent=black")
blt.set("0xE638: data/tiles/eagle.png, resize=12x12, transparent=black")
blt.set("0xE639: data/tiles/earth_elemental.png, resize=12x12, transparent=black")
blt.set("0xE640: data/tiles/elephant.png, resize=12x12, transparent=black")
blt.set("0xE641: data/tiles/elk.png, resize=12x12, transparent=black")
blt.set("0xE642: data/tiles/fire_elemental.png, resize=12x12, transparent=black")
blt.set("0xE643: data/tiles/fire_giant.png, resize=12x12, transparent=black")
blt.set("0xE644: data/tiles/flameskull.png, resize=12x12, transparent=black")
blt.set("0xE645: data/tiles/flesh_golem.png, resize=12x12, transparent=black")
blt.set("0xE646: data/tiles/flying_snake.png, resize=12x12, transparent=black")
blt.set("0xE647: data/tiles/flying_sword.png, resize=12x12, transparent=black")
blt.set("0xE648: data/tiles/frog.png, resize=12x12, transparent=black")
blt.set("0xE649: data/tiles/frost_giant.png, resize=12x12, transparent=black")
blt.set("0xE650: data/tiles/gargoyle.png, resize=12x12, transparent=black")
blt.set("0xE651: data/tiles/ghost.png, resize=12x12, transparent=black")
blt.set("0xE652: data/tiles/ghoul.png, resize=12x12, transparent=black")
blt.set("0xE653: data/tiles/giant_ape.png, resize=12x12, transparent=black")
blt.set("0xE654: data/tiles/giant_badger.png, resize=12x12, transparent=black")
blt.set("0xE655: data/tiles/giant_bat.png, resize=12x12, transparent=black")
blt.set("0xE656: data/tiles/giant_boar.png, resize=12x12, transparent=black")
blt.set("0xE657: data/tiles/giant_centipede.png, resize=12x12, transparent=black")
blt.set("0xE658: data/tiles/giant_constrictor_snake.png, resize=12x12, transparent=black")
blt.set("0xE659: data/tiles/giant_crab.png, resize=12x12, transparent=black")
blt.set("0xE660: data/tiles/giant_crocodile.png, resize=12x12, transparent=black")
blt.set("0xE661: data/tiles/giant_eagle.png, resize=12x12, transparent=black")
blt.set("0xE662: data/tiles/giant_elk.png, resize=12x12, transparent=black")
blt.set("0xE663: data/tiles/giant_fire_beetle.png, resize=12x12, transparent=black")
blt.set("0xE664: data/tiles/giant_frog.png, resize=12x12, transparent=black")
blt.set("0xE665: data/tiles/giant_goat.png, resize=12x12, transparent=black")
blt.set("0xE666: data/tiles/giant_hyena.png, resize=12x12, transparent=black")
blt.set("0xE667: data/tiles/giant_lizard.png, resize=12x12, transparent=black")
blt.set("0xE668: data/tiles/giant_octopus.png, resize=12x12, transparent=black")
blt.set("0xE669: data/tiles/giant_owl.png, resize=12x12, transparent=black")
blt.set("0xE670: data/tiles/giant_poisonous_snake.png, resize=12x12, transparent=black")
blt.set("0xE671: data/tiles/giant_rat.png, resize=12x12, transparent=black")
blt.set("0xE672: data/tiles/giant_scorpion.png, resize=12x12, transparent=black")
blt.set("0xE673: data/tiles/giant_sea_horse.png, resize=12x12, transparent=black")
blt.set("0xE674: data/tiles/giant_shark.png, resize=12x12, transparent=black")
blt.set("0xE675: data/tiles/giant_spider.png, resize=12x12, transparent=black")
blt.set("0xE676: data/tiles/giant_toad.png, resize=12x12, transparent=black")
blt.set("0xE677: data/tiles/giant_vulture.png, resize=12x12, transparent=black")
blt.set("0xE678: data/tiles/giant_wasp.png, resize=12x12, transparent=black")
blt.set("0xE679: data/tiles/giant_weasel.png, resize=12x12, transparent=black")
blt.set("0xE680: data/tiles/giant_wolf_spider.png, resize=12x12, transparent=black")
blt.set("0xE681: data/tiles/gnoll.png, resize=12x12, transparent=black")
blt.set("0xE682: data/tiles/goat.png, resize=12x12, transparent=black")
blt.set("0xE683: data/tiles/goblin.png, resize=12x12, transparent=black")
blt.set("0xE684: data/tiles/grick.png, resize=12x12, transparent=black")
blt.set("0xE685: data/tiles/griffon.png, resize=12x12, transparent=black")
blt.set("0xE686: data/tiles/harpy.png, resize=12x12, transparent=black")
blt.set("0xE687: data/tiles/hawk.png, resize=12x12, transparent=black")
blt.set("0xE688: data/tiles/hell_hound.png, resize=12x12, transparent=black")
blt.set("0xE689: data/tiles/hill_giant.png, resize=12x12, transparent=black")
blt.set("0xE690: data/tiles/hippogriff.png, resize=12x12, transparent=black")
blt.set("0xE691: data/tiles/hobgoblin.png, resize=12x12, transparent=black")
blt.set("0xE692: data/tiles/hunter_shark.png, resize=12x12, transparent=black")
blt.set("0xE693: data/tiles/hydra.png, resize=12x12, transparent=black")
blt.set("0xE694: data/tiles/hyena.png, resize=12x12, transparent=black")
blt.set("0xE695: data/tiles/jackal.png, resize=12x12, transparent=black")
blt.set("0xE696: data/tiles/killer_whale.png, resize=12x12, transparent=black")
blt.set("0xE697: data/tiles/kobold.png, resize=12x12, transparent=black")
blt.set("0xE698: data/tiles/lion.png, resize=12x12, transparent=black")
blt.set("0xE699: data/tiles/lizard.png, resize=12x12, transparent=black")
blt.set("0xE700: data/tiles/lizardfolk.png, resize=12x12, transparent=black")
blt.set("0xE701: data/tiles/mammoth.png, resize=12x12, transparent=black")
blt.set("0xE702: data/tiles/manticore.png, resize=12x12, transparent=black")
blt.set("0xE703: data/tiles/mastiff.png, resize=12x12, transparent=black")
blt.set("0xE704: data/tiles/medusa.png, resize=12x12, transparent=black")
blt.set("0xE705: data/tiles/merfolk.png, resize=12x12, transparent=black")
blt.set("0xE706: data/tiles/minotaur.png, resize=12x12, transparent=black")
blt.set("0xE707: data/tiles/mule.png, resize=12x12, transparent=black")
blt.set("0xE708: data/tiles/mummy.png, resize=12x12, transparent=black")
blt.set("0xE709: data/tiles/nothic.png, resize=12x12, transparent=black")
blt.set("0xE710: data/tiles/ochre_jelly.png, resize=12x12, transparent=black")
blt.set("0xE711: data/tiles/octopus.png, resize=12x12, transparent=black")
blt.set("0xE712: data/tiles/ogre.png, resize=12x12, transparent=black")
blt.set("0xE713: data/tiles/orc.png, resize=12x12, transparent=black")
blt.set("0xE714: data/tiles/owl.png, resize=12x12, transparent=black")
blt.set("0xE715: data/tiles/owlbear.png, resize=12x12, transparent=black")
blt.set("0xE716: data/tiles/panther.png, resize=12x12, transparent=black")
blt.set("0xE717: data/tiles/pegasus.png, resize=12x12, transparent=black")
blt.set("0xE718: data/tiles/phase_spider.png, resize=12x12, transparent=black")
blt.set("0xE719: data/tiles/plesiosaurus.png, resize=12x12, transparent=black")
blt.set("0xE720: data/tiles/poisonous_snake.png, resize=12x12, transparent=black")
blt.set("0xE721: data/tiles/polar_bear.png, resize=12x12, transparent=black")
blt.set("0xE722: data/tiles/pony.png, resize=12x12, transparent=black")
blt.set("0xE723: data/tiles/pteranodon.png, resize=12x12, transparent=black")
blt.set("0xE724: data/tiles/quipper.png, resize=12x12, transparent=black")
blt.set("0xE725: data/tiles/rat.png, resize=12x12, transparent=black")
blt.set("0xE726: data/tiles/raven.png, resize=12x12, transparent=black")
blt.set("0xE727: data/tiles/reef_shark.png, resize=12x12, transparent=black")
blt.set("0xE728: data/tiles/rhinoceros.png, resize=12x12, transparent=black")
blt.set("0xE729: data/tiles/riding_horse.png, resize=12x12, transparent=black")
blt.set("0xE730: data/tiles/sabre-toothed_tiger.png, resize=12x12, transparent=black")
blt.set("0xE731: data/tiles/satyr.png, resize=12x12, transparent=black")
blt.set("0xE732: data/tiles/scorpion.png, resize=12x12, transparent=black")
blt.set("0xE733: data/tiles/sea_horse.png, resize=12x12, transparent=black")
blt.set("0xE734: data/tiles/skeleton.png, resize=12x12, transparent=black")
blt.set("0xE735: data/tiles/spectator.png, resize=12x12, transparent=black")
blt.set("0xE736: data/tiles/spider.png, resize=12x12, transparent=black")
blt.set("0xE737: data/tiles/stirge.png, resize=12x12, transparent=black")
blt.set("0xE738: data/tiles/stone_golem.png, resize=12x12, transparent=black")
blt.set("0xE739: data/tiles/swarm_of_bats.png, resize=12x12, transparent=black")
blt.set("0xE740: data/tiles/swarm_of_insects.png, resize=12x12, transparent=black")
blt.set("0xE741: data/tiles/swarm_of_poisonous_snakes.png, resize=12x12, transparent=black")
blt.set("0xE742: data/tiles/swarm_of_quippers.png, resize=12x12, transparent=black")
blt.set("0xE743: data/tiles/swarm_of_rats.png, resize=12x12, transparent=black")
blt.set("0xE744: data/tiles/swarm_of_ravens.png, resize=12x12, transparent=black")
blt.set("0xE745: data/tiles/tiger.png, resize=12x12, transparent=black")
blt.set("0xE746: data/tiles/triceratops.png, resize=12x12, transparent=black")
blt.set("0xE747: data/tiles/troll.png, resize=12x12, transparent=black")
blt.set("0xE748: data/tiles/twig_blight.png, resize=12x12, transparent=black")
blt.set("0xE749: data/tiles/tyrannosaurus_rex.png, resize=12x12, transparent=black")
blt.set("0xE750: data/tiles/vulture.png, resize=12x12, transparent=black")
blt.set("0xE751: data/tiles/warhorse.png, resize=12x12, transparent=black")
blt.set("0xE752: data/tiles/water_elemental.png, resize=12x12, transparent=black")
blt.set("0xE753: data/tiles/weasel.png, resize=12x12, transparent=black")
blt.set("0xE754: data/tiles/werewolf.png, resize=12x12, transparent=black")
blt.set("0xE755: data/tiles/wight.png, resize=12x12, transparent=black")
blt.set("0xE756: data/tiles/winter_wolf.png, resize=12x12, transparent=black")
blt.set("0xE757: data/tiles/wolf.png, resize=12x12, transparent=black")
blt.set("0xE758: data/tiles/worg.png, resize=12x12, transparent=black")
blt.set("0xE759: data/tiles/wyvern.png, resize=12x12, transparent=black")
blt.set("0xE760: data/tiles/yeti.png, resize=12x12, transparent=black")
blt.set("0xE761: data/tiles/young_green_dragon.png, resize=12x12, transparent=black")
blt.set("0xE762: data/tiles/zombie.png, resize=12x12, transparent=black")

# NPCs

blt.set("0xE263: data/tiles/acolyte.png, resize=24x24, transparent=black")
blt.set("0xE264: data/tiles/archmage.png, resize=24x24, transparent=black")
blt.set("0xE265: data/tiles/assassin.png, resize=24x24, transparent=black")
blt.set("0xE266: data/tiles/bandit.png, resize=24x24, transparent=black")
blt.set("0xE267: data/tiles/bandit_captain.png, resize=24x24, transparent=black")
blt.set("0xE268: data/tiles/berserker.png, resize=24x24, transparent=black")
blt.set("0xE269: data/tiles/commoner.png, resize=24x24, transparent=black")
blt.set("0xE270: data/tiles/cultist.png, resize=24x24, transparent=black")
blt.set("0xE271: data/tiles/cult_fanatic.png, resize=24x24, transparent=black")
blt.set("0xE272: data/tiles/gladiator.png, resize=24x24, transparent=black")
blt.set("0xE273: data/tiles/guard.png, resize=24x24, transparent=black")
blt.set("0xE274: data/tiles/knight.png, resize=24x24, transparent=black")
blt.set("0xE275: data/tiles/mage.png, resize=24x24, transparent=black")
blt.set("0xE276: data/tiles/noble.png, resize=24x24, transparent=black")
blt.set("0xE277: data/tiles/priest.png, resize=24x24, transparent=black")
blt.set("0xE278: data/tiles/scout.png, resize=24x24, transparent=black")
blt.set("0xE279: data/tiles/spy.png, resize=24x24, transparent=black")
blt.set("0xE280: data/tiles/thug.png, resize=24x24, transparent=black")
blt.set("0xE281: data/tiles/tribal_warrior.png, resize=24x24, transparent=black")
blt.set("0xE282: data/tiles/veteran.png, resize=24x24, transparent=black")

# SMALL NPCs

blt.set("0xE763: data/tiles/acolyte.png, resize=12x12, transparent=black")
blt.set("0xE764: data/tiles/archmage.png, resize=12x12, transparent=black")
blt.set("0xE765: data/tiles/assassin.png, resize=12x12, transparent=black")
blt.set("0xE766: data/tiles/bandit.png, resize=12x12, transparent=black")
blt.set("0xE767: data/tiles/bandit_captain.png, resize=12x12, transparent=black")
blt.set("0xE768: data/tiles/berserker.png, resize=12x12, transparent=black")
blt.set("0xE769: data/tiles/commoner.png, resize=12x12, transparent=black")
blt.set("0xE770: data/tiles/cultist.png, resize=12x12, transparent=black")
blt.set("0xE771: data/tiles/cult_fanatic.png, resize=12x12, transparent=black")
blt.set("0xE772: data/tiles/gladiator.png, resize=12x12, transparent=black")
blt.set("0xE773: data/tiles/guard.png, resize=12x12, transparent=black")
blt.set("0xE774: data/tiles/knight.png, resize=12x12, transparent=black")
blt.set("0xE775: data/tiles/mage.png, resize=12x12, transparent=black")
blt.set("0xE776: data/tiles/noble.png, resize=12x12, transparent=black")
blt.set("0xE777: data/tiles/priest.png, resize=12x12, transparent=black")
blt.set("0xE778: data/tiles/scout.png, resize=12x12, transparent=black")
blt.set("0xE779: data/tiles/spy.png, resize=12x12, transparent=black")
blt.set("0xE780: data/tiles/thug.png, resize=12x12, transparent=black")
blt.set("0xE781: data/tiles/tribal_warrior.png, resize=12x12, transparent=black")
blt.set("0xE782: data/tiles/veteran.png, resize=12x12, transparent=black")

#ITEMS

blt.set("0xE300: data/tiles/weapon.png, resize=24x24, transparent=black")
blt.set("0xE301: data/tiles/armour.png, resize=24x24, transparent=black")
blt.set("0xE302: data/tiles/other.png, resize=24x24, transparent=black")
blt.set("0xE303: data/tiles/padded.png, resize=24x24, transparent=black")
blt.set("0xE304: data/tiles/leather.png, resize=24x24, transparent=black")
blt.set("0xE305: data/tiles/studded_leather.png, resize=24x24, transparent=black")
blt.set("0xE306: data/tiles/hide.png, resize=24x24, transparent=black")
blt.set("0xE307: data/tiles/chain_shirt.png, resize=24x24, transparent=black")
blt.set("0xE308: data/tiles/scale_mail.png, resize=24x24, transparent=black")
blt.set("0xE309: data/tiles/breastplate.png, resize=24x24, transparent=black")
blt.set("0xE310: data/tiles/half_plate.png, resize=24x24, transparent=black")
blt.set("0xE311: data/tiles/ring_mail.png, resize=24x24, transparent=black")
blt.set("0xE312: data/tiles/chain_mail.png, resize=24x24, transparent=black")
blt.set("0xE313: data/tiles/splint.png, resize=24x24, transparent=black")
blt.set("0xE314: data/tiles/plate.png, resize=24x24, transparent=black")
blt.set("0xE315: data/tiles/shield.png, resize=24x24, transparent=black")
blt.set("0xE316: data/tiles/club.png, resize=24x24, transparent=black")
blt.set("0xE317: data/tiles/dagger.png, resize=24x24, transparent=black")
blt.set("0xE318: data/tiles/greatclub.png, resize=24x24, transparent=black")
blt.set("0xE319: data/tiles/handaxe.png, resize=24x24, transparent=black")
blt.set("0xE320: data/tiles/javelin.png, resize=24x24, transparent=black")
blt.set("0xE321: data/tiles/light_hammer.png, resize=24x24, transparent=black")
blt.set("0xE322: data/tiles/mace.png, resize=24x24, transparent=black")
blt.set("0xE323: data/tiles/quarterstaff.png, resize=24x24, transparent=black")
blt.set("0xE324: data/tiles/sickle.png, resize=24x24, transparent=black")
blt.set("0xE325: data/tiles/spear.png, resize=24x24, transparent=black")
blt.set("0xE326: data/tiles/light_crossbow.png, resize=24x24, transparent=black")
blt.set("0xE327: data/tiles/dart.png, resize=24x24, transparent=black")
blt.set("0xE328: data/tiles/shortbow.png, resize=24x24, transparent=black")
blt.set("0xE329: data/tiles/battleaxe.png, resize=24x24, transparent=black")
blt.set("0xE330: data/tiles/flail.png, resize=24x24, transparent=black")
blt.set("0xE331: data/tiles/glaive.png, resize=24x24, transparent=black")
blt.set("0xE332: data/tiles/greataxe.png, resize=24x24, transparent=black")
blt.set("0xE333: data/tiles/greatsword.png, resize=24x24, transparent=black")
blt.set("0xE334: data/tiles/halberd.png, resize=24x24, transparent=black")
blt.set("0xE335: data/tiles/lance.png, resize=24x24, transparent=black")
blt.set("0xE336: data/tiles/longsword.png, resize=24x24, transparent=black")
blt.set("0xE337: data/tiles/maul.png, resize=24x24, transparent=black")
blt.set("0xE338: data/tiles/morningstar.png, resize=24x24, transparent=black")
blt.set("0xE339: data/tiles/pike.png, resize=24x24, transparent=black")
blt.set("0xE340: data/tiles/rapier.png, resize=24x24, transparent=black")
blt.set("0xE341: data/tiles/scimitar.png, resize=24x24, transparent=black")
blt.set("0xE342: data/tiles/shortsword.png, resize=24x24, transparent=black")
blt.set("0xE343: data/tiles/trident.png, resize=24x24, transparent=black")
blt.set("0xE344: data/tiles/war_pick.png, resize=24x24, transparent=black")
blt.set("0xE345: data/tiles/warhammer.png, resize=24x24, transparent=black")
blt.set("0xE346: data/tiles/whip.png, resize=24x24, transparent=black")
blt.set("0xE347: data/tiles/blowgun.png, resize=24x24, transparent=black")
blt.set("0xE348: data/tiles/heavy_crossbow.png, resize=24x24, transparent=black")
blt.set("0xE349: data/tiles/longbow.png, resize=24x24, transparent=black")
blt.set("0xE350: data/tiles/sling.png, resize=24x24, transparent=black")
blt.set("0xE351: data/tiles/needle.png, resize=24x24, transparent=black")
blt.set("0xE352: data/tiles/bolt.png, resize=24x24, transparent=black")
blt.set("0xE353: data/tiles/arrow.png, resize=24x24, transparent=black")
blt.set("0xE354: data/tiles/bullet.png, resize=24x24, transparent=black")
blt.set("0xE355: data/tiles/torch.png, resize=24x24, transparent=black")
blt.set("0xE356: data/tiles/food_ration.png, resize=24x24, transparent=black")
blt.set("0xE357: data/tiles/potion1.png, resize=24x24, transparent=black")
blt.set("0xE358: data/tiles/potion2.png, resize=24x24, transparent=black")
blt.set("0xE359: data/tiles/potion3.png, resize=24x24, transparent=black")
blt.set("0xE360: data/tiles/potion4.png, resize=24x24, transparent=black")
blt.set("0xE361: data/tiles/potion5.png, resize=24x24, transparent=black")
blt.set("0xE362: data/tiles/amulet1.png, resize=24x24, transparent=black")
blt.set("0xE363: data/tiles/amulet2.png, resize=24x24, transparent=black")
blt.set("0xE364: data/tiles/amulet3.png, resize=24x24, transparent=black")
blt.set("0xE365: data/tiles/amulet4.png, resize=24x24, transparent=black")
blt.set("0xE366: data/tiles/amulet5.png, resize=24x24, transparent=black")
blt.set("0xE367: data/tiles/book1.png, resize=24x24, transparent=black")
blt.set("0xE368: data/tiles/book2.png, resize=24x24, transparent=black")
blt.set("0xE369: data/tiles/book3.png, resize=24x24, transparent=black")
blt.set("0xE370: data/tiles/book4.png, resize=24x24, transparent=black")
blt.set("0xE371: data/tiles/book5.png, resize=24x24, transparent=black")
blt.set("0xE372: data/tiles/ring1.png, resize=24x24, transparent=black")
blt.set("0xE373: data/tiles/ring2.png, resize=24x24, transparent=black")
blt.set("0xE374: data/tiles/ring3.png, resize=24x24, transparent=black")
blt.set("0xE375: data/tiles/ring4.png, resize=24x24, transparent=black")
blt.set("0xE376: data/tiles/ring5.png, resize=24x24, transparent=black")
blt.set("0xE377: data/tiles/scroll.png, resize=24x24, transparent=black")
blt.set("0xE378: data/tiles/gold.png, resize=24x24, transparent=black")
blt.set("0xE379: data/tiles/belt.png, resize=24x24, transparent=black")
blt.set("0xE380: data/tiles/boots1.png, resize=24x24, transparent=black")
blt.set("0xE381: data/tiles/boots2.png, resize=24x24, transparent=black")
blt.set("0xE382: data/tiles/cloak.png, resize=24x24, transparent=black")
blt.set("0xE383: data/tiles/gloves.png, resize=24x24, transparent=black")
blt.set("0xE384: data/tiles/gauntlets.png, resize=24x24, transparent=black")
blt.set("0xE385: data/tiles/helmet.png, resize=24x24, transparent=black")
blt.set("0xE386: data/tiles/crown.png, resize=24x24, transparent=black")

#SMALL ITEMS

blt.set("0xE800: data/tiles/weapon.png, resize=12x12, transparent=black")
blt.set("0xE801: data/tiles/armour.png, resize=12x12, transparent=black")
blt.set("0xE802: data/tiles/other.png, resize=12x12, transparent=black")
blt.set("0xE803: data/tiles/padded.png, resize=12x12, transparent=black")
blt.set("0xE804: data/tiles/leather.png, resize=12x12, transparent=black")
blt.set("0xE805: data/tiles/studded_leather.png, resize=12x12, transparent=black")
blt.set("0xE806: data/tiles/hide.png, resize=12x12, transparent=black")
blt.set("0xE807: data/tiles/chain_shirt.png, resize=12x12, transparent=black")
blt.set("0xE808: data/tiles/scale_mail.png, resize=12x12, transparent=black")
blt.set("0xE809: data/tiles/breastplate.png, resize=12x12, transparent=black")
blt.set("0xE810: data/tiles/half_plate.png, resize=12x12, transparent=black")
blt.set("0xE811: data/tiles/ring_mail.png, resize=12x12, transparent=black")
blt.set("0xE812: data/tiles/chain_mail.png, resize=12x12, transparent=black")
blt.set("0xE813: data/tiles/splint.png, resize=12x12, transparent=black")
blt.set("0xE814: data/tiles/plate.png, resize=12x12, transparent=black")
blt.set("0xE815: data/tiles/shield.png, resize=12x12, transparent=black")
blt.set("0xE816: data/tiles/club.png, resize=12x12, transparent=black")
blt.set("0xE817: data/tiles/dagger.png, resize=12x12, transparent=black")
blt.set("0xE818: data/tiles/greatclub.png, resize=12x12, transparent=black")
blt.set("0xE819: data/tiles/handaxe.png, resize=12x12, transparent=black")
blt.set("0xE820: data/tiles/javelin.png, resize=12x12, transparent=black")
blt.set("0xE821: data/tiles/light_hammer.png, resize=12x12, transparent=black")
blt.set("0xE822: data/tiles/mace.png, resize=12x12, transparent=black")
blt.set("0xE823: data/tiles/quarterstaff.png, resize=12x12, transparent=black")
blt.set("0xE824: data/tiles/sickle.png, resize=12x12, transparent=black")
blt.set("0xE825: data/tiles/spear.png, resize=12x12, transparent=black")
blt.set("0xE826: data/tiles/light_crossbow.png, resize=12x12, transparent=black")
blt.set("0xE827: data/tiles/dart.png, resize=12x12, transparent=black")
blt.set("0xE828: data/tiles/shortbow.png, resize=12x12, transparent=black")
blt.set("0xE829: data/tiles/battleaxe.png, resize=12x12, transparent=black")
blt.set("0xE830: data/tiles/flail.png, resize=12x12, transparent=black")
blt.set("0xE831: data/tiles/glaive.png, resize=12x12, transparent=black")
blt.set("0xE832: data/tiles/greataxe.png, resize=12x12, transparent=black")
blt.set("0xE833: data/tiles/greatsword.png, resize=12x12, transparent=black")
blt.set("0xE834: data/tiles/halberd.png, resize=12x12, transparent=black")
blt.set("0xE835: data/tiles/lance.png, resize=12x12, transparent=black")
blt.set("0xE836: data/tiles/longsword.png, resize=12x12, transparent=black")
blt.set("0xE837: data/tiles/maul.png, resize=12x12, transparent=black")
blt.set("0xE838: data/tiles/morningstar.png, resize=12x12, transparent=black")
blt.set("0xE839: data/tiles/pike.png, resize=12x12, transparent=black")
blt.set("0xE840: data/tiles/rapier.png, resize=12x12, transparent=black")
blt.set("0xE841: data/tiles/scimitar.png, resize=12x12, transparent=black")
blt.set("0xE842: data/tiles/shortsword.png, resize=12x12, transparent=black")
blt.set("0xE843: data/tiles/trident.png, resize=12x12, transparent=black")
blt.set("0xE844: data/tiles/war_pick.png, resize=12x12, transparent=black")
blt.set("0xE845: data/tiles/warhammer.png, resize=12x12, transparent=black")
blt.set("0xE846: data/tiles/whip.png, resize=12x12, transparent=black")
blt.set("0xE847: data/tiles/blowgun.png, resize=12x12, transparent=black")
blt.set("0xE848: data/tiles/heavy_crossbow.png, resize=12x12, transparent=black")
blt.set("0xE849: data/tiles/longbow.png, resize=12x12, transparent=black")
blt.set("0xE850: data/tiles/sling.png, resize=12x12, transparent=black")
blt.set("0xE851: data/tiles/needle.png, resize=12x12, transparent=black")
blt.set("0xE852: data/tiles/bolt.png, resize=12x12, transparent=black")
blt.set("0xE853: data/tiles/arrow.png, resize=12x12, transparent=black")
blt.set("0xE854: data/tiles/bullet.png, resize=12x12, transparent=black")
blt.set("0xE855: data/tiles/torch.png, resize=12x12, transparent=black")
blt.set("0xE856: data/tiles/food_ration.png, resize=12x12, transparent=black")
blt.set("0xE857: data/tiles/potion1.png, resize=12x12, transparent=black")
blt.set("0xE858: data/tiles/potion2.png, resize=12x12, transparent=black")
blt.set("0xE859: data/tiles/potion3.png, resize=12x12, transparent=black")
blt.set("0xE860: data/tiles/potion4.png, resize=12x12, transparent=black")
blt.set("0xE861: data/tiles/potion5.png, resize=12x12, transparent=black")
blt.set("0xE862: data/tiles/amulet1.png, resize=12x12, transparent=black")
blt.set("0xE863: data/tiles/amulet2.png, resize=12x12, transparent=black")
blt.set("0xE864: data/tiles/amulet3.png, resize=12x12, transparent=black")
blt.set("0xE865: data/tiles/amulet4.png, resize=12x12, transparent=black")
blt.set("0xE866: data/tiles/amulet5.png, resize=12x12, transparent=black")
blt.set("0xE867: data/tiles/book1.png, resize=12x12, transparent=black")
blt.set("0xE868: data/tiles/book2.png, resize=12x12, transparent=black")
blt.set("0xE869: data/tiles/book3.png, resize=12x12, transparent=black")
blt.set("0xE870: data/tiles/book4.png, resize=12x12, transparent=black")
blt.set("0xE871: data/tiles/book5.png, resize=12x12, transparent=black")
blt.set("0xE872: data/tiles/ring1.png, resize=12x12, transparent=black")
blt.set("0xE873: data/tiles/ring2.png, resize=12x12, transparent=black")
blt.set("0xE874: data/tiles/ring3.png, resize=12x12, transparent=black")
blt.set("0xE875: data/tiles/ring4.png, resize=12x12, transparent=black")
blt.set("0xE876: data/tiles/ring5.png, resize=12x12, transparent=black")
blt.set("0xE877: data/tiles/scroll.png, resize=12x12, transparent=black")
blt.set("0xE878: data/tiles/gold.png, resize=12x12, transparent=black")
blt.set("0xE879: data/tiles/belt.png, resize=12x12, transparent=black")
blt.set("0xE880: data/tiles/boots1.png, resize=12x12, transparent=black")
blt.set("0xE881: data/tiles/boots2.png, resize=12x12, transparent=black")
blt.set("0xE882: data/tiles/cloak.png, resize=12x12, transparent=black")
blt.set("0xE883: data/tiles/gloves.png, resize=12x12, transparent=black")
blt.set("0xE884: data/tiles/gauntlets.png, resize=12x12, transparent=black")
blt.set("0xE885: data/tiles/helmet.png, resize=12x12, transparent=black")
blt.set("0xE886: data/tiles/crown.png, resize=12x12, transparent=black")

# we need composition to be able to draw tiles on top of other tiles
blt.composition(True)

# needed to avoid insta-close
blt.refresh()

main_menu()
sys.exit()