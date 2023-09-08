process_list = [ [ [(0,0), (3,0), (5,0)], [(1,0), (2,0), (6,0)], [(1,1), (2,1), (6,1)]],
                 [ [(2,0), (2,1), (2,2)], [(0,0), (0,1), (0,2)]],
                 [ [(2,0), (2,1), (2,2)], [(2,0), (2,1), (2,2)]],
                 [ [(0,0)], [(0,1)], [(0,2)] ] ]
from aux_functions_20220504 import *
R = 625 # sampling rate, unit: MHz
central_freq = 75.0 # unit: MHz, denotes the frequency for the coordinate 0
lattice_spacing = 2 # unit: MHz, denotes the frequency spacing between neighboring coordinate points
transit_time = 1000 # unit: us, the time it takes for the light to shift one coordinate unit horizontally or vertically

# s = [75.000, 81.000, 85.000]
# e = [77.000, 79.000, 87.000]
# out = cubic_interp_freq_list(R, transit_time, s, e)
# print(out)
#
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import numpy as np
#
# s1 = [out[i][0] for i in range(len(out))]
# s2 = [out[i][1] for i in range(len(out))]
# plt.plot(s1)
# plt.plot(s2)
# plt.show()

# R, time, freq_list_1, freq_list_1_2, time_list, amp_list_1, phase_list_1 = read_setup_from_txt('test_gen_mixed_freq_list_1_rel_phase.txt')
# print(f"R = {R}")
# print(f"time = {time}")
# print(f"freq_list_1 = {freq_list_1}")
# # print(f"freq_list_1_2 = {freq_list_1_2}")
# # print(f"time_list = {time_list}")
# # print(f"amp_list_1 = {amp_list_1}")
# # print(f"phase_list_1 = {phase_list_1}")

a = [0, 1, 2, 3]
b = [4, 5, 6, 7]
for x, y in zip(a, b):
    print(x, y)