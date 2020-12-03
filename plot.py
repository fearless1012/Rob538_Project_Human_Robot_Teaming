import matplotlib.pyplot as plt
import numpy as np

def main():

    n_episodes = 100
    random_wl_mean = 20
    random_wl_std = 10
    random_perf


    x = range(n_episodes)
    # con_wl = self.consensus_wl_mean
    # con_wl_errm = np.subtract(self.consensus_wl_mean, self.consensus_wl_std)
    # con_wl_errp = np.add(self.consensus_wl_mean, self.consensus_wl_std)
    # con_perf = self.consensus_perf
    #
    # ncb_wl = self.noCollab_wl_mean
    # ncb_wl_errm = np.subtract(self.noCollab_wl_mean, self.noCollab_wl_std)
    # ncb_wl_errp = np.add(self.noCollab_wl_mean, self.noCollab_wl_std)
    # ncb_perf = self.noCollab_perf

    ran_wl = random_wl_mean
    ran_wl_errm = np.subtract(random_wl_mean,random_wl_std)
    ran_wl_errp = np.add(random_wl_mean, random_wl_std)
    ran_perf = random_perf

    plt.clf()
    plt.xlabel('Time Steps', fontsize=35)
    plt.ylabel('Workload Level', fontsize=35)
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    plt.title(title + " Workload Variation", fontsize=40)

    #plt.plot(x, con_wl, '-', label='Consensus', color='red')
    #plt.fill_between(x, con_wl_errm, con_wl_errp, color='red', alpha=0.2)

    #plt.plot(x, ncb_wl, '-', label='No Collaboration', color='green')
    #plt.fill_between(x, ncb_wl_errm, ncb_wl_errp, color='green', alpha=0.2)

    plt.plot(x, ran_wl, '-', label='Random', color='blue')
    plt.fill_between(x, ran_wl_errm, ran_wl_errp, color='blue', alpha=0.2)

    plt.legend(loc="upper right", fontsize=30, prop={'size': 6})
    plt.xlim(-0.03 * n_episodes, 1.10 * n_episodes)
    plt.ylim(0, 100 + 50)
    plt.grid()
    plt.show()

    plt.clf()
    plt.xlabel('Time Steps', fontsize=35)
    plt.ylabel('Performance Level', fontsize=35)
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    plt.title(title + " Performance", fontsize=40)

    plt.plot(x, con_perf, '-', label='Consensus', color='red')
    plt.plot(x, ncb_perf, '-', label='No Collaboration', color='green')
    plt.plot(x, ran_perf, '-', label='Random', color='blue')

    plt.legend(loc="upper right", fontsize=30)
    plt.xlim(-0.03 * n_episodes, 1.03 * n_episodes)
    plt.ylim(0, 110)
    plt.grid()
    plt.show()

if __name__ == '__main__':
    main()
