# coding: utf8

class Quest: #container class for quest details to be contained in a list

	def __init__(self, name):
		self.name = name
		self.quest_giver = None
		self.prereqs = []
		self.finish_condition = None
		self.incomplete_text = None
		self.complete_text = None
		self.reward = None
		self.priority = 1 #priority queue starts at 1 and works upwards

quests = []

quest = Quest('kill nubnag')
quest.quest_giver = 'Odette'
quest.finish_condition = 'killed nubnag'
quest.incomplete_text = "For all of our sakes, you must kill Nubnag. He rules the warrens to the south-west, but beware; he is a dangerous foe. We have suffered at his hands for too long."
quest.complete_text = "Can it really be true? Nubnag has perished? I can scarcely believe what you tell me. North Warren will be forever in your debt. Please take this as a token of our appreciation."
quest.reward = '50 gold'
quests.append(quest)

quest = Quest('kill saint cormag')
quest.quest_giver = 'Cardinal Florian'
quest.finish_condition = 'killed saint cormag'
quest.incomplete_text = "Our Lord can not abide the works of the Fallen Saint Cormag. Of all of the False Clerics, he is the most vile; he twists the words of the Teachings and performs depraved acts of despicable evil in the name of Our Lord. He hides in the Ancient Shrine and his taint must be purged."
quest.complete_text = "You must know that murder is always a Sin, but I must take solace in the fact that you are but a tool of Our Lord. I will not question his Wisdom no matter how distasteful I find this terrible business; certainly the world is a better place with Saint Cormag laid to rest. You must pray and meditate upon your deeds; but please take this as compensation for your time."
quest.reward = '150 gold'
quests.append(quest)