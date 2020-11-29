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

    def auction_phase(self):
        for team in self.Teams:
            for j, b in enumerate(team.b_i):
                if b > team.y_i[j]:
                    team.x_i[j] = 1
                    team.y_i[j] = b

    def consensus_phase(self):
        for team in self.Teams:
            #Get y from neighbors
            row = team.id
            neighbors_y = list()
            for neighbor in self.comm_mat[row]:
                if neighbor == 1:
                    neighbors_y.append(self.Teams[neighbor].y_i)
            
            #Find max task bid
            for i, x in enumerate(team.x_i):
                if x == 1:
                    max_bid = team.y_i[i]
                    for y_k in neighbors_y:
                        neighbor_bid = y_k[i]
                        if neighbor_bid > max_bid:
                            max_bid = neighbor_bid
                            team.y_i[i] = max_bid
                            team.x_i[i] = 0

    def reached_consensus(self):
        for team in self.Teams:
            if team.y_previous != team.y_i:
                return False
        return True
            
    def runSimulation(self, n_episodes):
        for i in range(n_episodes):
            # self.comm_mat = self.generate_COMM(n_teams) # uncomment for dynamic system
            self.task_mat = np.random.randint(2, size=(self.n_teams, self.n_tasks))
            self.generate_Z(self.comm_mat, self.task_mat)

            consensus = False
            counter = 0
            while consensus != True: # Subject to change; Update the termination condition for consensus termination
                # Phase 0 Set up problem
                self.generate_B(self.task_mat)
                for team in self.Teams:
                    team.y_previous = team.y_i
                
                # Phase 1 Auction
                self.auction_phase()

                # Phase 2 Consensus
                self.consensus_phase()

                # Phase 3: Did we reach consensus
                if counter > 100:
                    consensus = True
                else:
                    consensus = self.reached_consensus()
                counter += 1

            # Get Task performance metrics and workload metrics
            # updateWorkload
            
##################################################################################################

def main():
    world_obj = World()
    
if __name__ == '__main__':
    main()



