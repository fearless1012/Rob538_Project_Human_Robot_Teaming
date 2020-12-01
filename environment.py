from matplotlib.pyplot import colorbar
import numpy as np
import copy
import matplotlib.pyplot as plt
from collections import Counter
import random
from Team import Team
import time

np.set_printoptions(precision = 3, linewidth=1000)

class World(object):
    def __init__(self, title, n_teams=20, n_tasks=4, static=True, capability='mixed', n_episodes=100, W_ul=20.0, W_ol=100.0):
        self.title = title
        self.n_teams = n_teams  
        self.n_tasks = n_tasks
        self.static = static
        self.n_episodes = n_episodes

        self.Teams = self.generate_teams(n_teams, n_tasks, capability, W_ul, W_ol)
        self.task_mat_set = self.generate_TaskSet(n_teams, n_tasks, n_episodes)
        self.comm_mat_set = self.generate_COMMSet(n_teams, static, n_episodes)

        # All Metrics Needed
        self.consensus_wl_mean = []
        self.consensus_wl_std = []
        self.consensus_perf = []

        self.noCollab_wl_mean = []
        self.noCollab_wl_std = []
        self.noCollab_perf = []

        self.random_wl_mean = []
        self.random_wl_std = []
        self.random_perf = []

    def generate_teams(self, n_teams, n_tasks, capability, W_ul, W_ol):
        Teams = []
        for i in range(n_teams):
            T = Team(n_teams, n_tasks, i, capability, W_ul, W_ol)
            Teams.append(T)
        return Teams

    def generate_TaskSet(self, n_teams, n_tasks, n_episodes):
        task_mat_set = []
        for i in range(n_episodes):
            task_mat = np.random.randint(2, size=(n_teams, n_tasks))
            task_mat_set.append(task_mat)
        return task_mat_set

    def generate_COMMSet(self, n_teams, static, n_episodes):
        comm_mat_set = []

        G = np.random.randint(2, size=(n_teams, n_teams))
        np.fill_diagonal(G, 1)
        comm_mat = np.tril(G) + np.tril(G, -1).T

        for i in range(n_episodes):
            if static == True:
                comm_mat_set.append(comm_mat)

            else:
                G = np.random.randint(2, size=(n_teams, n_teams))
                np.fill_diagonal(G, 1)
                comm_mat = np.tril(G) + np.tril(G, -1).T
                comm_mat_set.append(comm_mat)

        return comm_mat_set

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
            
    def clearParams(self, reset_workload=False):
        for i in range(self.n_teams):
            self.Teams[i].clearParams(reset_workload)

    def auction_phase(self):
        for team in self.Teams:
            for j, b in enumerate(team.b_i):
                if b > team.y_i[j]:
                    team.x_i[j] = 1
                    team.y_i[j] = b

    def consensus_phase(self, comm_mat):
        for team in self.Teams:
            #Get y from neighbors
            row = team.id
            neighbors_y = list()
            neighbors = list()
            for i, neighbor in enumerate(comm_mat[row]):
                if neighbor == 1:
                    neighbors_y.append(self.Teams[i].y_i)
                    neighbors.append(i)
            
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
            if not np.array_equal(team.y_previous, team.y_i):
                return False
        return True
            
    def runConsensusSimulation(self):
        for i in range(self.n_episodes):
            task_mat = self.task_mat_set[i]
            comm_mat = self.comm_mat_set[i]

            self.generate_Z(comm_mat, task_mat)
            consensus = False
            counter = 0
            while consensus != True: # Subject to change; Update the termination condition for consensus termination
                # Phase 0 Set up problem
                self.generate_B(task_mat)
                for team in self.Teams:
                    team.y_previous = copy.deepcopy(team.y_i)
                
                self.auction_phase() # Phase 1 Auction
                self.consensus_phase(comm_mat)  # Phase 2 Consensus

                if counter >= 100:  # Phase 3: Check Consensus
                    consensus = True
                else:
                    consensus = self.reached_consensus()
                counter += 1

            self.updateWorkload() #  updateWorkload
            wl_mean, wl_std, perf_mean = self.getMetrics(task_mat)
            self.consensus_wl_mean.append(wl_mean)
            self.consensus_wl_std.append(wl_std)
            self.consensus_perf.append(perf_mean)
            self.clearParams()
        self.clearParams(reset_workload=True)

    def runNoCollabSimulation(self):
        for i in range(self.n_episodes):
            task_mat = self.task_mat_set[i]
            comm_mat = self.comm_mat_set[i]

            #NoCollab Task Allocation Algorithm
            self.generate_Z(comm_mat, task_mat)
            for team in self.Teams:
                G = comm_mat[team.id]
                z_i = list()
                b_i = list()

                #No collaboration - generate Z
                for j in range(len(G)):
                    if j == team.id:
                        z_i += list(task_mat[j])
                    else:
                        z_i += list(np.zeros(self.n_tasks, dtype=int))
                # Sanity Check
                if np.shape(team.z_i) == np.shape(z_i):
                    team.z_i = z_i
                else:
                    print("Invalid shape Z")

                #No collaboration - generate B
                for j in range(len(team.z_i)):
                    if team.z_i[j] == 1:
                        task_cnt = sum(team.x_i) - team.robot.task_assigned
                        w_oj = team.human.cur_wl + np.exp(task_cnt + 1)
                        a_ij = team.human.task_perf*(team.W_ol - abs(team.W_nl - w_oj))
                        p_ij = (1-team.human.task_perf)*abs(w_oj - team.human.cur_wl)
                        b_ij = a_ij - p_ij
                        b_i.append(b_ij)
                    elif team.z_i[j] == 0:
                        b_ij = 0.0
                        b_i.append(b_ij)
                    else:
                        print("Invalid z value in updateB")

                cur_team_task = list(task_mat[team.id])
                if team.human.cur_wl > team.W_nl and sum(cur_team_task) > 0: # Checking to assign task to robot agent
                    idx = cur_team_task.index(1) # find the idx of the task
                    pos = team.id*self.n_tasks + idx # Find the task position in z_i
                    b_i[pos] = 1.1*b_i[pos] # Alter the corresponding bidding value by 10%
                    team.robot.watch_pos = pos
                    team.robot.task_idx = idx
                # Sanity Check
                if np.shape(team.b_i) == np.shape(b_i):
                    team.b_i = b_i
                else:
                    print("Invalid shape B")

                # No collaboration - task assignment
                for i, b in enumerate(team.b_i):
                    if b > 0:
                        team.x_i[i] = 1
                        team.y_i[i] = b

            self.updateWorkload()
            wl_mean, wl_std, perf_mean = self.getMetrics(task_mat)
            self.noCollab_wl_mean.append(wl_mean)
            self.noCollab_wl_std.append(wl_std)
            self.noCollab_perf.append(perf_mean)
            self.clearParams()
        self.clearParams(reset_workload=True)
        
    def runRandomSimulation(self):
        for i in range(self.n_episodes):
            task_mat = self.task_mat_set[i]
            comm_mat = self.comm_mat_set[i]

            # TODO : Random Task Allocation Algorithm

            self.updateWorkload()
            wl_mean, wl_std, perf_mean = self.getMetrics(task_mat)
            self.random_wl_mean.append(wl_mean)
            self.random_wl_std.append(wl_std)
            self.random_perf.append(perf_mean)
            self.clearParams()
        self.clearParams(reset_workload=True)

    def runSimulation(self):
        self.runConsensusSimulation()
        self.runNoCollabSimulation()
        # self.runRandomSimulation()
        self.plot(title=self.title)

    def getMetrics(self, task_mat):
        wl_t = []
        h_t = []
        system_perf = 0.0
        for i in range(self.n_teams):
            wl = self.Teams[i].human.cur_wl
            system_perf += self.Teams[i].cur_team_perf
            h_t.append(self.Teams[i].human.task_perf)
            wl_t.append(wl)

        total_tasks = np.sum(task_mat)
        perf_mean  = system_perf/(total_tasks*sum(h_t))
        wl_mean = np.mean(wl_t)
        wl_std = np.std(wl_t)
        return wl_mean, wl_std, perf_mean

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

    def plot(self, title=''):
        x = range(self.n_episodes)
        con_wl = self.consensus_wl_mean
        con_wl_errm = np.subtract(self.consensus_wl_mean, self.consensus_wl_std)
        con_wl_errp = np.add(self.consensus_wl_mean, self.consensus_wl_std) 
        con_perf = self.consensus_perf

        ncb_wl = self.noCollab_wl_mean
        ncb_wl_errm = np.subtract(self.noCollab_wl_mean, self.noCollab_wl_std)
        ncb_wl_errp = np.add(self.noCollab_wl_mean, self.noCollab_wl_std) 
        ncb_perf = self.noCollab_perf

        ran_wl = self.random_wl_mean
        ran_wl_errm = np.subtract(self.random_wl_mean, self.random_wl_std)
        ran_wl_errp = np.add(self.random_wl_mean, self.random_wl_std) 
        ran_perf = self.random_perf

        plt.clf()
        plt.xlabel('Time Steps', fontsize=35)
        plt.ylabel('Workload Level', fontsize=35)
        plt.xticks(fontsize=25)
        plt.yticks(fontsize=25)
        plt.title(title+" Workload Variation", fontsize=40)

        plt.plot(x, con_wl, '-', label='Consensus', color='red')
        plt.fill_between(x, con_wl_errm, con_wl_errp, color='red', alpha=0.2)
        
        plt.plot(x, ncb_wl, '-', label='No Collaboration', color='green')
        plt.fill_between(x, ncb_wl_errm, ncb_wl_errp, color='green', alpha=0.2)

        # plt.plot(x, ran_wl, '-', label='Random', color='blue')
        # plt.fill_between(x, ran_wl_errm, ran_wl_errp, color='blue', alpha=0.2)

        plt.legend(loc="upper right", fontsize=30)
        plt.xlim(-0.03*self.n_episodes, 1.10*self.n_episodes)
        plt.ylim(0, 100+50)
        plt.grid()
        plt.show()

        plt.clf()
        plt.xlabel('Time Steps', fontsize=35)
        plt.ylabel('Performance Level', fontsize=35)
        plt.xticks(fontsize=25)
        plt.yticks(fontsize=25)
        plt.title(title+" Performance", fontsize=40)

        plt.plot(x, con_perf, '-', label='Consensus', color='red')
        plt.plot(x, ncb_perf, '-', label='No Collaboration', color='green')
        # plt.plot(x, ran_perf, '-', label='Random', color='blue')
        
        plt.legend(loc="upper right", fontsize=30)
        plt.xlim(-0.03*self.n_episodes, 1.03*self.n_episodes)
        plt.ylim(0, 1.2)
        plt.grid()
        plt.show()
        # plt.errorbar(x, wl_mean, yerr=wl_std, label='Consensus', ecolor="red")

##################################################################################################

def main():

#     # Comparison 1: Environment
#     # Scenario 1a: Static with 20 teams & 4 tasks and Mixed Capabilities
    world_obj_1a = World(title='Static Environment:', n_teams=20, n_tasks=4, static=True, capability='mixed', n_episodes=100)
    world_obj_1a.runSimulation()

#     # Comparison 1: Environment
#     # Scenario 1b: Dynamic with 20 teams and Mixed Capabilities
#     world_obj_1b = World(title='Dynamic Environment:', n_teams=20, n_tasks=4, static=False, capability='mixed', n_episodes=100)
#     world_obj_1b.runSimulation()

# # ####################################################################################################

#     # Comparison 2: Team Scalability
#     # Scenario 2a: Static with 10 teams and Mixed Capabilities
    # world_obj_2a = World(title='10 Teams:', n_teams=10, n_tasks=4, static=True, capability='mixed', n_episodes=100)
    # world_obj_2a.runSimulation()

#     # Comparison 2: Team Scalability
#     # Scenario 2b: Static with 50 teams and Mixed Capabilities
    # world_obj_2b = World(title='100 Teams:', n_teams=100, n_tasks=4, static=True, capability='mixed', n_episodes=100)
    # world_obj_2b.runSimulation()


# # ###################################################################################################

#     # Comparison 3: Team Capabilities
#     # Scenario 3a: Static with 20 teams and all are bad teams
#     n_episodes = 100
#     world_obj_3a = World(title='Only Bad Teams:', n_teams=20, n_tasks=4, static=True, capability='bad', n_episodes=100)
#     world_obj_3a.runSimulation()


#     # Comparison 3: Team Capabilities
#     # Scenario 3b: Static with 20 teams and all good agents   
#     world_obj_3b = World(title='Only Good Teams:', n_teams=20, n_tasks=4, static=True, capability='good', n_episodes=100)
#     world_obj_3b.runSimulation()

if __name__ == '__main__':
    main()



