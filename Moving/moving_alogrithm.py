# 1D AOD Moving Algorithm
# Input: the trapped atom status (generated by simulation or CCD signal) and the desired trap configuration
# Output: frequency transition of RF signals, which will be used in generating the transition signals


import numpy as np

R = 625  # sampling rate, unit: MHz
CENTRAL_FREQ = 75.0  # unit: MHz, denotes the frequency for the coordinate 0
LATTICE_SPACING = 0.5  # unit: MHz, denotes the frequency spacing between neighboring coordinate points (min: 0.45 MHz in Lukin's paper)


class MovingAlgo_1:
    # Algorithm 1: equal spacing traps -> specific configuration (pairs of traps of our interest)
    def __init__(self, ntrap=60, load_prob=.55):
        self.ntrap = ntrap
        self.init_freq_config = np.array([CENTRAL_FREQ + 0.5*(i-0.5*(-1+self.ntrap)) for i in range(self.ntrap)])  # initial trap layout
        self.init_atom_in_trap = np.array([np.random.choice([0, 1], p=[1-load_prob, load_prob]) for _ in range(self.ntrap)])  # simulation: if the atoms are in the trap

        self.final_trap_on = np.array([1 if (i%4==0 or i%4==1) else 0 for i in range(self.ntrap)])  # desired layout
        # 1: start freq, 2: final freq of a list of traps
        self.final_freq_config_1 = np.array([0.0 for _ in range(self.ntrap)])
        self.final_freq_config_2 = np.array([CENTRAL_FREQ + 0.5*(i-0.5*(-1+self.ntrap)) if (i%4==0 or i%4==1) else 0 for i in range(self.ntrap)])
        self.final_atom_in_trap = np.copy(self.init_atom_in_trap)  # to be manipulated: final trap configuration
        self.transition_list = []

    def calculation(self):
        # may be simplified to speedup
        k = 0
        while k < self.ntrap:
            if self.final_atom_in_trap[k] == 1 and self.final_trap_on[k] == 1:
                self.final_freq_config_1[k] = self.init_freq_config[k]
                self.transition_list.append([self.final_freq_config_1[k], self.final_freq_config_2[k]])
            elif self.final_atom_in_trap[k] == 0 and self.final_trap_on[k] == 1:
                # find the first non-zero element in init_atom_in_trap
                j = k + 1
                while j < self.ntrap-1:
                    if self.final_atom_in_trap[j] == 1:
                        self.final_atom_in_trap[k], self.final_atom_in_trap[j] = 1, 0  # swap
                        self.final_freq_config_1[k] = self.init_freq_config[j]
                        self.transition_list.append([self.final_freq_config_1[k], self.final_freq_config_2[k]])
                        break
                    j += 1
            elif self.final_atom_in_trap[k] == 1 and self.final_trap_on[k] == 0:
                self.final_atom_in_trap[k] = 0

            k += 1


test = MovingAlgo_1()
test.calculation()
print(test.init_atom_in_trap)
print(test.final_atom_in_trap)
print(test.transition_list)