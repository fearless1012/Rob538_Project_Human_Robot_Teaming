import numpy as np
import copy
import matplotlib.pyplot as plt
from collections import Counter
import random
from Team import Team

class World(object):
    def __init__(self, n_teams=20, n_tasks=4):
        self.n_teams = n_teams  
        self.n_tasks = n_tasks

        self.Teams = self.generate_teams(n_teams, n_tasks)
        self.task_mat = np.random.randint(2, size=(n_teams, n_tasks))
        self.comm_mat = self.generate_COMM(n_teams)

    def generate_teams(self, n_teams, n_tasks):
        Teams = []
        for i in range(n_teams):
            T = Team(n_teams, n_tasks, i)
            Teams.append(T)
        return Teams

    def generate_COMM(self, n_teams):
        G = np.random.randint(2, size=(n_teams, n_teams))
        np.fill_diagonal(G, 1)
        comm_mat = np.tril(G) + np.tril(G, -1).T
        return comm_mat

    def generate_Z(self, comm_mat, task_mat):
        for i in range(self.n_teams):
            G = comm_mat[i]
            self.Teams[i].updateZ(G, task_mat, self.n_tasks)

    def generate_B(self, task_mat):
        for i in range(self.n_teams):
            self.Teams[i].updateB(task_mat, self.n_tasks)

    def updateWorkload(self):
        pass

    def runSimulation(self, n_episodes):
        for i in range(n_episodes):
            # self.comm_mat = self.generate_COMM(n_teams) # uncomment for dynamic system
            self.task_mat = np.random.randint(2, size=(n_teams, n_tasks))
            self.generate_Z(self.comm_mat, self.task_mat)
            self.generate_B(self.task_mat)
            while self.consensus != True: # Subject to change; Update the termination condition for consensus termination
                # TODO: Phase 1 Auction
                # TODO: Phase 2 Consensus

            # Get Task performance metrics and workload metrics
            # updateWorkload
            
##################################################################################################

def main():
    world_obj = World()
    
if __name__ == '__main__':
    main()



