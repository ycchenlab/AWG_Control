# Title: Generation of moving trap
# Description:
# 1. Construct the piecewise quadratic frequency function for each possible trajectory of the trap.
# 2. Generate and save the sequence of RF signals for the moving trap.


import numpy as np
import json


filename = "../Data/static_trap_parameters_20230920_151601.json"
with open(filename, "r") as json_file:
    loaded_data = json.load(json_file)
    ntrap, freq, amp, phase = loaded_data[0], loaded_data[1], loaded_data[2], loaded_data[3]

class Move:
    def __init__(self, f, p, a, t):
        self.R = 625  # sampling rate, unit: MHz
        self.f_i, self.f_f = f[0], f[1]  # initial and final frequencies
        self.p_i, self.p_f = p[0], p[1]  # initial and final phases
        self.a = a  # list of amplitudes of static traps
        self.t = t  # moving time

        # coefficients of frequency interpolation functions
        self.cf_1, self.cf_2 = np.array([0 for _ in range(3)]), np.array([0 for _ in range(3)])
        self.signal_length = self.R * self.t
        self.cont_freq = np.array([0.0 for _ in range(self.signal_length)])
        self.cont_amp = np.array([0.0 for _ in range(self.signal_length)])
        self.signal = np.array([0.0 for _ in range(self.signal_length)])

    def get_cont_freq(self):
        f_m = (self.f_i + self.f_f) / 2  # middle frequency between 2 interpolation curve
        self.cf_1 = np.linalg.solve(np.array([[1, 0, 0], [1, self.t/2, (self.t/2)**2], [0, 1, 0]]), np.array([self.f_i, f_m, 0]))
        self.cf_2 = np.linalg.solve(np.array([[1, self.t/2, (self.t/2)**2], [1, self.t, self.t**2], [0, 1, 2*self.t]]), np.array([f_m, self.f_f, 0]))

        for i in range(self.signal_length):
            if i < self.signal_length / 2:
                self.cont_freq[i] = self.cf_1[0] + self.cf_1[1] * i / self.R + self.cf_1[2] * (i / self.R) ** 2
            else:
                self.cont_freq[i] = self.cf_2[0] + self.cf_2[1] * i / self.R + self.cf_2[2] * (i / self.R) ** 2

    def get_transit_time(self):
        pass

    def get_cont_amp(self):
        for i in range(self.signal_length):
            f = self.cont_freq[i]
            for j in range(len(freq)):
                if freq[j] <=  f <= freq[j+1]:
                    self.cont_amp[i] = amp[j] + (amp[j+1] - amp[j]) * (f - freq[j]) / (freq[j+1] - freq[j])



    def get_signal(self):
        pass

a = Move(f=(125, 75), p=(0, 0), a=[1, 1, 1], t=3000)
a.get_cont_freq()

# fn = "test.json"
# with open(fn, "w") as json_file:
#     json.dump(a.cont_freq.tolist(), json_file)

from matplotlib import pyplot as plt
plt.plot(a.cont_freq)
plt.show()






# class Move:
#     def __init__(self, filename):
#         # import some parameters (ntrap, [f], [a], [p]) from the static trap file
#
#
#         # some parameters associated to moving traps
#         self.coefficient_matrix = np.array([])

    # def get_coefficient(self, start_f, end_f):
    #     pass
    #
    # def get_signal(self, cfft):
    #     pass
