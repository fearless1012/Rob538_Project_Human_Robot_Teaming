import numpy as np
import copy
import matplotlib.pyplot as plt
from collections import Counter
import random

class Human(object):
	def __init__(self):
		self.skill = np.random.randint(3) 		# 0, 1, 2
		self.getParam()

		self.cur_wl = 0.0
		self.cur_task_cnt = 0

	def getParam(self):
		if self.skill == 0: # Bad agent
			self.wl_decay = random.uniform(0.8, 0.9)
			self.task_perf = random.uniform(0.5, 0.6)

		elif self.skill == 1: # Avg agent
			self.wl_decay = random.uniform(0.7, 0.8)
			self.task_perf = random.uniform(0.7, 0.8)

		elif self.skill == 2: # Good agent
			self.wl_decay = random.uniform(0.6, 0.7)
			self.task_perf = random.uniform(0.9, 1.0)

		else:
			print("Invalid!")

	def updateWorkload(self, n_tasks_assigned): # Update del_wl if needed 
		del_wl = np.exp(n_tasks_assigned)
		self.cur_wl = self.wl_decay*self.cur_wl + del_wl

class Robot(object):
	def __init__(self):
		self.task_assigned = 0 # 0 if task is not assigned at time T; 1 if task is assigned
		self.watch_pos = -1
		self.task_idx = 0

class Team(object):
	def __init__(self, n_teams, n_tasks, id_num):
		skill = np.random.randint(3)
		self.human = Human()
		self.robot = Robot()
		self.id = id_num

		self.z_i = np.zeros(n_teams*n_tasks, dtype=int)
		self.x_i = np.zeros(n_teams*n_tasks, dtype=int)
		self.b_i = np.zeros(n_teams*n_tasks)
		self.y_i = np.zeros(n_teams*n_tasks)
		self.y_previous = np.zeros(n_teams*n_tasks)

	def updateWorkload(self):
		task_cnt = sum(self.x_i) - self.robot.task_assigned
		self.human.updateWorkload(task_cnt)

	def clearParams(self):
		self.z_i = np.zeros(n_teams*n_tasks, dtype=int)
		self.x_i = np.zeros(n_teams*n_tasks, dtype=int)
		self.b_i = np.zeros(n_teams*n_tasks)
		self.y_i = np.zeros(n_teams*n_tasks)

		self.robot.task_assigned = -1

	def updateZ(self, G, task_mat, n_tasks):
		z = []
		for j in range(len(G)):
			if G[j] == 1:
				z += task_mat[j]
			else:
				z += np.zeros(n_tasks, dtype=int)

		# Sanity Check
		if self.z_i.shape == z.shape:
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

		for j in range(len(self.z)):
			if self.z_i[j] == 1:
				task_cnt = sum(self.x_i) - self.robot.task_assigned
				w_oj = self.human.cur_wl + np.exp(task_cnt + 1)
				a_ij = self.human.task_perf*(self.W_ol - abs(self.W_nl - w_oj))
				p_ij = (1-self.human.task_perf)*abs(w_oj - self.human.cur_wl)
				b_ij = a_ij - p_ij
				b_i.append(b_ij)

			elif self.z_i[j] == 0:
				b_ij = 0.0
				b_i.append(b_ij)

			else:
				print("Invalid z value in updateB")

		# TODO: update the robot.task_assigned value in h_ij
		cur_team_task = list(task_mat[self.id])
		if self.human.cur_wl > self.W_nl and sum(cur_team_task) > 0: # Checking to assign task to robot agent
			idx = cur_team_task.index(1) # find the idx of the task
			pos = self.id*n_tasks + idx # Find the task position in z_i
			b_i[pos] = 1.1*b_i[pos] # Alter the corresponding bidding value by 10%
			self.robot.watch_pos = pos
			self.robot.task_idx = idx

		# Sanity Check
		if self.b_i.shape == b_i.shape:
			self.b_i = b_i
		else:
			print("Invalid shape B")
