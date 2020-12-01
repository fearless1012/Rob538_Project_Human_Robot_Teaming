import numpy as np
import copy
import matplotlib.pyplot as plt
from collections import Counter
import random

class Human(object):
	def __init__(self, capability):
		skill = self.getSkill(capability)
		self.getParam(skill)
		self.cur_wl = 0.0
		self.cur_task_cnt = 0
		
	def getSkill(self, capability):
		skill = -1
		if capability == 'mixed':
			skill = np.random.randint(3) # 0, 1, 2
		
		elif capability == 'bad':
			skill = 0

		elif capability == 'avg':
			skill = 1

		elif capability == 'good':
			skill = 2

		else:
			print("Invalid capability in Human() class!")
		return skill
		
	def getParam(self, skill):
		if skill == 0: # Bad agent
			self.wl_decay = random.uniform(0.50, 0.75)
			self.task_perf = random.uniform(0.25, 0.5)

		elif skill == 1: # Avg agent
			self.wl_decay = random.uniform(0.25, 0.50)
			self.task_perf = random.uniform(0.5, 0.75)

		elif skill == 2: # Good agent
			self.wl_decay = random.uniform(0.1, 0.25)
			self.task_perf = random.uniform(0.75, 0.9)

		else:
			print("Invalid Skill!")

	def updateWorkload(self, n_tasks_assigned): # Update del_wl if needed
		del_wl = self.delWorkload(n_tasks_assigned)
		self.cur_wl = self.wl_decay*self.cur_wl + del_wl

	def delWorkload(self, n_tasks):
		K = 5.0
		del_wl = K*n_tasks
		return del_wl

class Robot(object):
	def __init__(self):
		self.task_assigned = 0 # 0 if task is not assigned at time T; 1 if task is assigned
		self.watch_pos = -1
		self.task_idx = 0

class Team(object):
	def __init__(self, n_teams, n_tasks, id_num, capability, W_ul, W_ol):
		skill = np.random.randint(3)
		self.human = Human(capability)
		self.robot = Robot()
		self.id = id_num
		self.n_teams = n_teams
		self.n_tasks = n_tasks

		self.W_ul = W_ul
		self.W_ol = W_ol
		self.W_nl = (W_ul+W_ol)/2.0
		
		self.cur_team_perf = 0.0

		self.z_i = np.zeros(n_teams*n_tasks, dtype=int)
		self.x_i = np.zeros(n_teams*n_tasks, dtype=int)
		self.b_i = np.zeros(n_teams*n_tasks)
		self.y_i = np.zeros(n_teams*n_tasks)
		self.y_previous = np.zeros(n_teams*n_tasks)

	def updateWorkload(self):
		total_task_cnt = sum(self.x_i) 
		human_cnt = total_task_cnt - self.robot.task_assigned
		self.human.updateWorkload(human_cnt)
		self.cur_team_perf = total_task_cnt*self.human.task_perf

	def clearParams(self, reset_workload):
		self.z_i = np.zeros(self.n_teams*self.n_tasks, dtype=int)
		self.x_i = np.zeros(self.n_teams*self.n_tasks, dtype=int)
		self.b_i = np.zeros(self.n_teams*self.n_tasks)
		self.y_i = np.zeros(self.n_teams*self.n_tasks)
		self.y_previous = np.zeros(self.n_teams*self.n_tasks)

		self.robot.watch_pos = -1

		if reset_workload == True:
			self.human.cur_wl = 0.0
			self.human.cur_task_cnt = 0

			self.robot.task_assigned = 0 
			self.robot.task_idx = 0

	def updateZ(self, G, task_mat, n_tasks):
		z = []
		for j in range(len(G)):
			if G[j] == 1:
				z += list(task_mat[j])
			else:
				z += list(np.zeros(n_tasks, dtype=int))

		# Sanity Check
		if np.shape(self.z_i) == np.shape(z):
			self.z_i = z
		else:
			print("Invalid shape Z")

	def updateB(self, task_mat, n_tasks):
		b_i = []

		# Update robot.task_assigned
		if self.robot.watch_pos >= 0:
			if self.x_i[self.robot.watch_pos] == 1:
				self.robot.task_assigned = 1
			else:
				self.robot.task_assigned = 0

		for j in range(len(self.z_i)):
			if self.z_i[j] == 1:
				human_task_cnt = sum(self.x_i) - self.robot.task_assigned
				w_oj = self.human.cur_wl + self.human.delWorkload(human_task_cnt + 1)
				a_ij = self.human.task_perf*(self.W_ol - abs(self.W_nl - w_oj))
				p_ij = (1.-self.human.task_perf)*abs(w_oj - self.human.cur_wl)
				b_ij = a_ij - p_ij
				b_i.append(b_ij)

			elif self.z_i[j] == 0:
				b_ij = 0.0
				b_i.append(b_ij)

			else:
				print("Invalid z value in updateB")

		# TODO: update the robot.task_assigned value in h_ij
		cur_team_task = list(task_mat[self.id])
		if self.human.cur_wl > self.W_ol and sum(cur_team_task) > 0: # Checking to assign task to robot agent
			idx = cur_team_task.index(1) # find the idx of the task
			pos = self.id*n_tasks + idx # Find the task position in z_i
			b_i[pos] = 1.1*b_i[pos] # Alter the corresponding bidding value by 10%
			self.robot.watch_pos = pos
			self.robot.task_idx = idx

		# Sanity Check
		if np.shape(self.b_i) == np.shape(b_i):
			self.b_i = b_i
		else:
			print("Invalid shape B")
