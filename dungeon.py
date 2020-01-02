class Dungeon_Branch:
	#a container class for dungeon branches
	def __init__(self, name, full_map=False, depth=1, theme=None, vault_type='vaults', random_populate=True, random_placement=True, overworld=False, always_lit=False, random_torches=True, special_vaults=True, random_quests=False, roughen_map=True, is_safe=False, can_recruit=True):
		self.name = name
		self.full_map = full_map
		self.depth = depth
		self.theme = theme
		self.vault_type=vault_type
		self.random_populate=random_populate
		self.random_placement=random_placement
		self.overworld=overworld #special flag which stops monster and item generation and prevents followers from spawning on this map
		self.always_lit=always_lit
		self.random_torches=random_torches
		self.special_vaults=special_vaults
		self.random_quests=random_quests
		self.roughen_map=roughen_map
		self.is_safe = is_safe
		self.can_recruit = can_recruit
		
		self.monsters = [None for i in range(depth)] #empty container for specifying monster types per dungeon level - should default to full monster generation if no corresponding entry for depth
		self.encounters = [None for i in range(depth)] #empty container for item types as above
		self.items = [None for i in range(depth)] #empty container for item types as above
		
		### NOTE: above containers need a dictionary for each level of the available depth even if it's empty, otherwise it'll default to generating all entity types. the key to the dictionary should be the entity type and the value associated with the key should be the weighting to use for generation
		
		### NOTE: the below containers work differently - you don't need to specify a dictionary for each level, rather the key is the dungeon level and the value is the function to use to generate that entity somewhere on the level
		
		self.must_generate_monster = {} #empty container which will force certain monsters to be generated on certain levels
		self.must_generate_encounter = {} #same, but for encounters
		self.must_generate_item = {} #same, but for items
		
dungeon = []

### NOTE: need to overwrite monster, item and encounter generation for each level with empty dictionaries if you do not want the default generator to apply. null values for any for that depth will default to the standard generator for that category

branch = Dungeon_Branch('overworld', full_map=True, theme='overworld', random_populate=False, random_placement=False, overworld=True, always_lit=True, random_torches=False)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)

branch = Dungeon_Branch('warrens', depth=3, vault_type='caves', special_vaults=False)
branch.monsters = [{'kobold':10, 'goblin':1, 'giant_bat':1, 'hyena':1, 'jackal':1}, #level 1
{'kobold':10, 'orc':1, 'hobgoblin':1, 'bugbear':1, 'hyena':1, 'jackal':1}, #level 2
{'kobold':5, 'orc':1, 'hobgoblin':1, 'bugbear':1, 'gnoll':1}] #level 3
branch.encounters = [{}, #level 1
{'basic kobold':1}, #level 2
{'basic kobold':3}] #level 3
#branch.items = []
#branch.must_generate_monster = {}
branch.must_generate_encounter = {3:['kobold horde']}
branch.must_generate_item = {3:['rare_magic']}
dungeon.append(branch)

branch = Dungeon_Branch('ancient_shrine', depth=3, vault_type='vaults', special_vaults=False)
branch.monsters = [{'skeleton':10, 'zombie':5}, #level 1
{'skeleton':5, 'zombie':10, 'ghoul':5}, #level 2
{'skeleton':3, 'zombie':3, 'ghoul':3, 'ghost':3}] #level 3
branch.encounters = [{}, #level 1
{'cultists':5, 'basic undead':1}, #level 2
{'basic undead':3, 'cultists':3}] #level 3
#branch.items = []
#branch.must_generate_monster = {}
branch.must_generate_encounter = {3:['necromancer horde']}
branch.must_generate_item = {3:['rare_magic']}
dungeon.append(branch)

branch = Dungeon_Branch('bandit_keep', depth=3, vault_type='vaults', special_vaults=False)
branch.monsters = [{'bandit':10, 'thug':3}, #level 1
{'bandit':10, 'thug':5, 'spy':2}, #level 2
{'bandit':5, 'thug':5, 'spy':5, 'assassin':5}] #level 3
branch.encounters = [{}, #level 1
{'basic bandit':3}, #level 2
{'basic bandit':5}] #level 3
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
branch.must_generate_item = {3:['rare_magic']}
dungeon.append(branch)

branch = Dungeon_Branch('sanctum', depth=3, vault_type='vaults', special_vaults=False)
branch.monsters = [
{'blink_dog':1, 'blood_hawk':1, 'giant_rat':1, 'hippogriff':1}, #level 1
{'flying_sword':1, 'flying_snake':1, 'animated_armour':1, 'gargoyle':1}, #level 2
{'mage':1, 'air_elemental':1, 'fire_elemental':1, 'earth_elemental':1}] #level 3
branch.encounters = [{},{},{}]
#branch.items = []
branch.must_generate_monster = {3:['archmage']}
#branch.must_generate_encounter = {}
branch.must_generate_item = {3:['rare_magic']}
dungeon.append(branch)

branch = Dungeon_Branch("haunt", depth=3, vault_type='vaults', special_vaults=False)
branch.monsters = [{'skeleton':3, 'zombie':3, 'raven':1, 'hyena':1, 'bat':1, 'spider':1, 'flying_sword':1}, #level 1
{'skeleton':2, 'zombie':2, 'animated_armour':1, 'flying_sword':1, 'death_dog':1, 'ghoul':2}, #level 2
{'animated_armour':1, 'flying_sword':1, 'flameskull':1, 'death_dog':1, 'hell_hound':1, 'ghoul':1, 'mummy':1}] #level 3
branch.encounters = [{}, #level 1
{'basic undead':1}, #level 2
{'basic undead':3}] #level 3
#branch.items = []
branch.must_generate_monster = {3:['aoife']}
#branch.must_generate_encounter = {}
branch.must_generate_item = {3:['rare_magic']}
dungeon.append(branch)

branch = Dungeon_Branch('badbog', depth=3, vault_type='caves', special_vaults=False)
branch.monsters = [{'boar':1, 'poisonous_snake':1, 'frog':1, 'scorpion':1, 'spider':1, 'stirge':1}, #level 1
{'boar':1, 'giant_boar':1, 'poisonous_snake':1, 'giant_poisonous_snake':1, 'giant_frog':1, 'giant_scorpion':1, 'giant_spider':1, 'giant_wolf_spider':1}, #level 2
{'giant_boar':1, 'giant_poisonous_snake':1, 'giant_frog':1, 'giant_toad':1, 'giant_spider':1, 'giant_wolf_spider':1, 'giant_crocodile':1}] #level 3
branch.encounters = [{}, {}, {}]
#branch.items = []
branch.must_generate_monster = {3:['hydra']}
#branch.must_generate_encounter = {}
branch.must_generate_item = {3:['rare_magic']}
dungeon.append(branch)

branch = Dungeon_Branch('vierfort', full_map=True, theme='town', always_lit=True, random_populate=False, random_torches=False)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)

branch = Dungeon_Branch('catacombs', depth=3, vault_type='vaults', special_vaults=False)
branch.monsters = [{'gnoll':2, 'bugbear':2, 'lizardfolk':5}, #level 1
{'gnoll':4, 'bugbear':4, 'lizardfolk':2}, #level 2
{'gnoll':4, 'bugbear':4, 'hill_giant':2}] #level 3
branch.encounters = [{}, {}, {}]
#branch.items = []
branch.must_generate_monster = {3:['flameskull', 'flameskull', 'flameskull']}
#branch.must_generate_encounter = {}
branch.must_generate_item = {3:['rare_magic']}
dungeon.append(branch)

branch = Dungeon_Branch('rage_hill', depth=3, vault_type='caves', special_vaults=False, can_recruit=False)
branch.monsters = [{'orc':2, 'goblin':2, 'hobgoblin':2, 'tribal_warrior':2, 'brown_bear':1},
{'orc':2, 'tribal_warrior':2, 'berserker':2, 'ogre':2, 'black_bear':1},
{'berserker':2, 'ogre':2, 'minotaur':2, 'sabre_toothed_tiger':1}]
branch.encounters = [{},{},{'solo ogre mage':1}]
#branch.items = []
branch.must_generate_monster = {3:['fire_giant', 'frost_giant', 'cyclops']}
#branch.must_generate_encounter = {}
branch.must_generate_item = {3:['rare_magic']}
dungeon.append(branch)

branch = Dungeon_Branch('red_outpost', full_map=True, theme='town', always_lit=True, random_populate=False, random_torches=False, is_safe=True)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)

branch = Dungeon_Branch('red_prison', theme='red', random_quests=True, depth=10)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
branch.must_generate_monster = {10:['adult_red_dragon']}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)

branch = Dungeon_Branch('north_warren', full_map=True, theme='town', always_lit=True, random_populate=False, random_torches=False, is_safe=True)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)

branch = Dungeon_Branch('mirefield_keep', full_map=True, theme='town', always_lit=True, random_populate=False, random_torches=False, is_safe=True)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)

branch = Dungeon_Branch('beggars_hole', full_map=True, always_lit=True, random_populate=False, random_torches=False, is_safe=True)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)

branch = Dungeon_Branch('black_hollow', full_map=True, theme='town', always_lit=True, random_populate=False, random_torches=False, is_safe=True)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)

branch = Dungeon_Branch('cindemere', full_map=True, theme='town', always_lit=True, random_populate=False, random_torches=False, is_safe=True)
#branch.monsters = []
#branch.encounters = []
#branch.items = []
#branch.must_generate_monster = {}
#branch.must_generate_encounter = {}
#branch.must_generate_item = {}
dungeon.append(branch)