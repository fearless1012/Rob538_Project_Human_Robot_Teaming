from matplotlib.pyplot import colorbar
import numpy as np
import copy
import matplotlib.pyplot as plt
from collections import Counter
import random
from Team import Team

class World(object):
    def __init__(self, n_teams=4, n_tasks=3, W_ul=10.0, W_ol=100.0):
        self.n_teams = n_teams  
        self.n_tasks = n_tasks
        
        self.W_ul = W_ul
        self.W_ol = W_ol

        self.Teams = self.generate_teams(n_teams, n_tasks)
        self.task_mat = np.random.randint(2, size=(n_teams, n_tasks))
        self.comm_mat = self.generate_COMM(n_teams)

        self.wl_mean_metrics = []
        self.wl_std_metrics = []
        self.perf_metrics = []

    def generate_teams(self, n_teams, n_tasks):
        Teams = []
        for i in range(n_teams):
            T = Team(n_teams, n_tasks, i, self.W_ul, self.W_ol)
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
        for i in range(self.n_teams):
            self.Teams[i].updateWorkload()
            
    def clearParams(self):
        for i in range(self.n_teams):
            self.Teams[i].clearParams()

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
            if team.y_previous.all() != team.y_i.all():
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

            self.updateWorkload() #  updateWorkload
            self.getMetrics()
            self.clearParams()

        self.plot(self.wl_mean_metrics, self.wl_std_metrics, self.perf_metrics, n_episodes)

    def getMetrics(self):
        wl_t = []
        h_t = []
        system_perf = 0.0
        for i in range(self.n_teams):
            wl = self.Teams[i].human.cur_wl
            system_perf += self.Teams[i].cur_team_perf
            h_t.append(self.Teams[i].human.task_perf)
            wl_t.append(wl)

        total_tasks = np.sum(self.task_mat)
        system_perf  = system_perf/(total_tasks*sum(h_t))

        wl_mean = np.mean(wl_t)
        wl_std = np.std(wl_t)

        self.wl_mean_metrics.append(wl_mean)
        self.wl_std_metrics.append(wl_std)
        self.perf_metrics.append(system_perf)

    def moving_average(self, reward_list, n=10):
        ma_reward = []
        N = len(reward_list)
        for i in range(N):
            end = i+n
            if end < N:
                cum = reward_list[i:end]
                avg = np.sum(cum) / (len(cum))
                ma_reward.append(avg)
            else:
                break
        return ma_reward

    def plot(self, wl_mean, wl_std, perf_mean, T):
        # moving average smoothing ??
        plt.clf()
        x = range(T)
        plt.xlabel('Time Steps', fontsize=30)
        plt.ylabel('Workload Level', fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.title("workload vs Timesteps", fontsize=35)
        plt.errorbar(x, wl_mean, yerr=wl_std, label='Workload Variation', ecolor="tab:red")
        # plt.legend(loc="upper right", fontsize=25)
        plt.xlim(-0.03*T, 1.10*T)
        plt.ylim(0, 100)
        plt.grid()
        plt.show()

        plt.clf()
        plt.xlabel('Time Steps', fontsize=30)
        plt.ylabel('Performance Level', fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.title("Performance Level vs Timesteps", fontsize=35)
        plt.plot(perf_mean, label='Performance Level')
        plt.xlim(-0.03*T, 1.10*T)
        plt.ylim(0, 1)
        plt.grid()
        plt.show()

##################################################################################################

def main():
    world_obj = World()
    n_episodes = 100
    world_obj.runSimulation(n_episodes)
    
if __name__ == '__main__':
    main()



