# coding: utf8

class Encounter: #container class for list of monsters container class

	def __init__(self, name, faction, cr, special_encounter=False):
		self.name = name
		self.monsters = [] #this will be a list of monsters objects
		self.count = 0
		self.faction = faction
		self.cr = cr
		self.special_encounter = special_encounter
		
	def add_group(self, group):
		self.monsters.append(group)
		
	def next_group(self):
		if self.count < len(self.monsters):
			self.count += 1
			return self.monsters[self.count-1]
		else:
			self.count = 0
			return None
			
class Monsters: #container class for instructions to build each monster type in encounter

	def __init__(self, type, name=None, min=2, max=5, hp=None, str=None, dex=None, con=None, int=None, wis=None, cha=None, clvl=None, magic=False, spells=None, ranged=False, illumination_chance=0):
		self.type = type
		self.name = name
		self.min = min
		self.max = max
		self.hp = hp
		self.str = str
		self.dex = dex
		self.con = con
		self.int = int
		self.wis = wis
		self.cha = cha
		self.clvl = clvl
		self.magic = magic
		self.spells = spells
		self.ranged = ranged
		self.illumination_chance = illumination_chance #percentage chance to carry a torch
		
encounters = []

###
### CR 1 ENCOUNTERS
###

#kobold mob w/ mages, shamans and slingers
enc = Encounter('basic kobold', 'kobold', 1)
enc.add_group(Monsters(type='kobold', min=1, max=3))
enc.add_group(Monsters(type='kobold', name='kobold slinger', min=0, max=2, ranged=True))
enc.add_group(Monsters(type='kobold', name='kobold mage', min=0, max=1, int=12, clvl=4, magic=True, spells=['fire bolt', 'magic missile']))
enc.add_group(Monsters(type='kobold', name='kobold shaman', min=0, max=1, wis=14, clvl=4, magic=True, spells=['sacred flame', 'cure wounds']))
for mon in enc.monsters: mon.illumination_chance = 25
encounters.append(enc)

#simple bandit mob w/ a captain
enc = Encounter('basic bandit', 'bandit', 1)
enc.add_group(Monsters(type='bandit', min=2, max=4))
enc.add_group(Monsters(type='bandit_captain', min=1, max=1))
for mon in enc.monsters: mon.illumination_chance = 75
encounters.append(enc)
 
#group of cultists
enc = Encounter('cultists', 'undead', 1)
enc.add_group(Monsters(type='cultist', min=2, max=5))
enc.add_group(Monsters(type='cult_fanatic', min=1, max=2))
for mon in enc.monsters: mon.illumination_chance = 75
encounters.append(enc)

#simple undead mob with mix of skeletons, zombies and ghouls
enc = Encounter('basic undead', 'undead', 1)
enc.add_group(Monsters(type='skeleton', min=0, max=2))
enc.add_group(Monsters(type='zombie', min=0, max=2))
enc.add_group(Monsters(type='ghoul', min=0, max=2))
encounters.append(enc)

#lizard squad 
enc = Encounter('basic lizardfolk', 'lizardfolk', 1)
enc.add_group(Monsters(type='lizardfolk', min=1, max=2))
enc.add_group(Monsters(type='lizard', min=4, max=6))
encounters.append(enc)

###
### CR 2 ENCOUNTERS
###

#goblins w/ worgs

#orc mob w/ mages, shamans and chuckers
enc = Encounter('basic orc', 'orc', 2)
enc.add_group(Monsters(type='orc', min=1, max=3))
enc.add_group(Monsters(type='orc', name='orc chucker', min=0, max=2, ranged=True))
enc.add_group(Monsters(type='orc', name='orc mage', min=0, max=1, int=14, clvl=5, magic=True, spells=['fire bolt', 'magic missile']))
enc.add_group(Monsters(type='orc', name='orc shaman', min=0, max=1, wis=16, clvl=5, magic=True, spells=['sacred flame', 'cure wounds']))
for mon in enc.monsters: mon.illumination_chance = 25
encounters.append(enc)

#wights w/ zombies

###
### CR 3 ENCOUNTERS
###

#ogre with goblin followers
enc = Encounter('basic ogre', 'ogre', 3)
enc.add_group(Monsters(type='ogre', min=1, max=1))
enc.add_group(Monsters(type='goblin', min=2, max=4))
encounters.append(enc)

#ogre mage
enc = Encounter('solo ogre mage', 'ogre', 3)
enc.add_group(Monsters(type='ogre', name='ogre mage', min=1, max=1, int=14, clvl=8, magic=True, spells=['fire bolt', 'magic missile', 'fireball']))
encounters.append(enc)

#kobold horde
enc = Encounter('kobold horde', 'kobold', 3, special_encounter=True)
enc.add_group(Monsters(type='kobold', min=3, max=5))
enc.add_group(Monsters(type='kobold', name='kobold slinger', min=1, max=3, ranged=True))
enc.add_group(Monsters(type='kobold', name='kobold mage', min=1, max=2, int=12, clvl=4, magic=True, spells=['fire bolt', 'magic missile']))
enc.add_group(Monsters(type='kobold', name='kobold shaman', min=1, max=2, wis=14, clvl=4, magic=True, spells=['sacred flame', 'cure wounds']))
enc.add_group(Monsters(type='nubnag', min=1, max=1))
for mon in enc.monsters: mon.illumination_chance = 25
encounters.append(enc)

#necromancer horde
enc = Encounter('necromancer horde', 'undead', 3, special_encounter=True)
enc.add_group(Monsters(type='skeleton', min=2, max=5))
enc.add_group(Monsters(type='skeleton', name='skeleton archer', min=1, max=2, ranged=True))
enc.add_group(Monsters(type='zombie', min=2, max=5))
enc.add_group(Monsters(type='zombie', name='zombie brute', min=1, max=2, str=18, con=18, hp=44))
enc.add_group(Monsters(type='ghoul', min=1, max=4))
enc.add_group(Monsters(type='saint_cormag', min=1, max=1, illumination_chance=100))
encounters.append(enc)

#frost giant w/ winter wolves


