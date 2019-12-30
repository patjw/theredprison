# coding: utf8

import random

### XX is the text that will be scanned for and replaced with the quest target name
### YY is the text that will be scanned for and replaced with the quest item name

KILL_REQUEST = {'I have been waiting for one such as you. I promise you a fabulous reward should you have the courage to slay XX. They have been a thorn in my side for far too long now. I urge you to make haste!', 'The evil XX lurks nearby. Defeat them and I will be in your debt.', 'I hold great power but I do not have time for distractions. XX is determined to thwart me. Do you have the willpower to confront them?'}
RETRIEVE_REQUEST = {'How fortunate that I have stumbled upon you! Lost within this place is something of great value to me. My YY is a family heirloom.', 'Please help me! I have lost my YY somewhere in this terrible place.', 'Somewhere within these halls is an item of great importance to me. Should you find my YY and bring it back to me, I promise that you will be rewarded.'}
RECOVER_REQUEST = {'You might be able to help! The evil XX stole from me my irreplaceable YY. It will not be easy but if you come across them in your travels, you have to get it back for me!', 'I came into this place with something of great value to me, but alas, XX betrayed me. I do not care how you do it, but if you bring me back my YY, you will be rewarded.', 'Lost to me was my YY. I know that XX is to blame. Please, you must help me!'}
DIALOGUE_ON_INCOMPLETE_KILL = {'I am told that the scoundrel XX still lives!', 'I hope that your plans to destroy XX are progressing.', 'My spies tell me that XX is alive and well. That is unacceptable.'}
DIALOGUE_ON_INCOMPLETE_RETRIEVE = {'Hopefully soon you will manage to find the YY, you can not fail me!', 'Have you found me YY yet?', 'Please hurry, I can not be without my YY for much longer.'}
DIALOGUE_ON_INCOMPLETE_RECOVER = {'It pains me to know that XX still possesses my YY!', 'Soon I will have my YY back and XX will pay for their betrayal!', 'My YY is still in the hands of XX. I can not go on.'}
DIALOGUE_ON_COMPLETE_KILL = {'Word of your deeds have already reached me! Your courage and prowess deserve the richest of rewards.', 'You are a true hero! XX was no match for your skills.', 'Now, with XX finally dead, I can finally progress my plans.'}
DIALOGUE_ON_COMPLETE_RETRIEVE = {'I will be forever in your debt! I can not thank you enough, with the return of my YY I feel whole again.', 'My precious YY brings me such joy. You are my saviour.', 'Thank you so much, you have no idea how much my YY means to me.'}
DIALOGUE_ON_COMPLETE_RECOVER = {'You have performed a great task and I will praise your name forever. Truly you are a hero worthy of praise.', 'I am overjoyed at the return of my YY. Thank you for your help.', 'With my YY back in my possession, I can finally rest.'}

class Quest: #container class for a single quest goal

	def __init__(self, quest_type, quest_giver, quest_target, quest_item, quest_lvl):
		self.quest_type = quest_type #string which is either 'kill', 'retrieve', or 'recover'
		self.quest_giver = quest_giver
		self.quest_target = quest_target
		self.quest_item = quest_item
		self.quest_lvl = quest_lvl
		
		self.accepted = False
		self.completed = False
		self.reward = None
		
		if quest_type == 'kill':
			self.request_dialogue = random.choice(tuple(KILL_REQUEST))
			self.remind_dialogue = random.choice(tuple(DIALOGUE_ON_INCOMPLETE_KILL))
			self.reward_dialogue = random.choice(tuple(DIALOGUE_ON_COMPLETE_KILL))
		if quest_type == 'retrieve':
			self.request_dialogue = random.choice(tuple(RETRIEVE_REQUEST))
			self.remind_dialogue = random.choice(tuple(DIALOGUE_ON_INCOMPLETE_RETRIEVE))
			self.reward_dialogue = random.choice(tuple(DIALOGUE_ON_COMPLETE_RETRIEVE))
		if quest_type == 'recover':
			self.request_dialogue = random.choice(tuple(RECOVER_REQUEST))
			self.remind_dialogue = random.choice(tuple(DIALOGUE_ON_INCOMPLETE_RECOVER))
			self.reward_dialogue = random.choice(tuple(DIALOGUE_ON_COMPLETE_RECOVER))
			
		if quest_target: self.request_dialogue = self.request_dialogue.replace('XX', quest_target.name)
		if quest_item: self.request_dialogue = self.request_dialogue.replace('YY', quest_item.name)
		
		if quest_target: self.remind_dialogue = self.remind_dialogue.replace('XX', quest_target.name)
		if quest_item: self.remind_dialogue = self.remind_dialogue.replace('YY', quest_item.name)
		
		if quest_target: self.reward_dialogue = self.reward_dialogue.replace('XX', quest_target.name)
		if quest_item: self.reward_dialogue = self.reward_dialogue.replace('YY', quest_item.name)