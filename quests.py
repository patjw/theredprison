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
		self.priority = 1

quests = []

quest = Quest('kill nubnag')
quest.quest_giver = 'Odette'
quest.finish_condition = 'killed nubnag'
quest.incomplete_text = "For all of our sakes, you must kill Nubnag. He rules the warrens to the south-west, but beware; he is a dangerous foe. We have suffered at his hands for too long."
quest.complete_text = "Can it really true? Nubnag has perished? I can scarcely believe what you tell me. North Warren will be forever in your debt. Please take this as a token of our appreciation."
quest.reward = '50 gold'
quests.append(quest)