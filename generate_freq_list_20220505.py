import sys
import math 
from aux_functions_20220504 import write_step_single_freq, write_step_multi_freq

# This Python file generates the .txt file containing the information needed for the AOD conrol program to generate the required
# waveforms. 
# The required information in the file contains the sampling rate for the AWG, the number of distinct frequency components,
# the relative amplitude and relative phase between each frequency components, the starting and ending frequencies for each step,
# and the duration of each frequency shift step.
#
# The txt file for setup should contain the following information in the following order:
# Line 1 of the .txt file: Sampling frequency in MHz. For this board (M4i.6622-x8), 50 MHz < sampling frequency < 625 MHz
#
# The subsequent lines are grouped into sets of 3 lines.
# The first and second lines contain two sets of frequencies of equal number along with their relative amplitudes and phases. 
# The number of frequencies listed denotes the number of freqency components in the output RF signal.
# The i-th output signal frequency will change from the i-th freq in Line 1 into the i-th freq in Line 2.
# This frequency transition follows a cubic interpolation frequency curve, and the duration is listed in Line 3.
# The detailed explanation of each line is as follows:
# Line 1: This line contains number of frequencies, frequency components (in MHz), relative amplitude, relative phase (in radian)
#         The data in this line is organized as follows (n denotes the number of frequencies):
#         n, n nums denoting the n frequencies, n nums denoting the relative amp, n nums denoting the relative phase
#         Note that the numbers are separated by a whitespace.
#         Also note that the relative amplitude may be any positive number. What matters is the relative amplitude.
#     Ex: 3 75.000 76.000 77.000 1 1 1 0 0.5 1
# Line 2: This line contains the ending frequencies for the movement
#     Ex: 3 77.000 78.000 79.000
# Line 3: This line contains the time for this step (frequency transition) in us (microsecond)
#     Ex: 6000


R = 625 # sampling rate, unit: MHz
central_freq = 75.0 # unit: MHz, denotes the frequency for the coordinate 0
lattice_spacing = 2 # unit: MHz, denotes the frequency spacing between neighboring coordinate points
transit_time = 1000 # unit: us, the time it takes for the light to shift one coordinate unit horizontally or vertically
out_file_1 = 'test_gen_mixed_freq_list_1_rel_phase.txt' # file name of the output file specifying the signal in the x direction
out_file_2 = 'test_gen_mixed_freq_list_2_rel_phase.txt' # file name of the output file specifying the signal in the y direction

# the first line of both files is the sampling frequency
f1 = open(out_file_1, 'w')
f2 = open(out_file_2, 'w')
f1.write(str(R) + '\n')
f2.write(str(R)+ '\n')

# The movement processes are organized into a list of n-lists. Each n-list denotes a movement step.
# That is, each point in the first sub-list of the n-list moves to the points in the second sub-list, and so on.
# Ex: [(0,0), (3,0), (5,0)], [(1,0), (2,0), (6,0)] means that (0,0) moves to (1,0), and (3,0) to (2,0), and so on.
# The length of the sub-lists can be arbitrary, but each sub-lists should contain the same number of points.
# Also, the number of steps contained in a process_list is also arbitrary.
process_list = [ [ [(0,0), (3,0), (5,0)], [(1,0), (2,0), (6,0)], [(1,1), (2,1), (6,1)]],
                 [ [(2,0), (2,1), (2,2)], [(0,0), (0,1), (0,2)]],
                 [ [(2,0), (2,1), (2,2)], [(2,0), (2,1), (2,2)]],
                 [ [(0,0)], [(0,1)], [(0,2)] ] ]
# process_list = [ [ [(0,0), (1,0), (2,0), (3,0)], [(0,0), (1,0), (2,0), (3,0)]]]
#process_list = [ [ [(0,0), (1,0), (2,0), (3,0)], [(1,0), (2,0), (3,0), (5,0)]]]
#process_list = [ [ [(0,0)], [(0,0)]]]

# What is this?
for steps_list in process_list:
    if len(steps_list[0]) > 1: # move more than one point in this step list
        for p1, p2 in zip(steps_list, steps_list[1:]):
            amp = [1] * len(p1)
            phase = [0] * len(p1)
            write_step_multi_freq(float(central_freq), float(lattice_spacing), transit_time, p1, p2, f1, f2, amp, phase)
    elif len(steps_list[0]) == 1: # move one point only
        for p1, p2 in zip(steps_list, steps_list[1:]):
            print(p1)
            print(p2)
            write_step_single_freq(float(central_freq), float(lattice_spacing), transit_time, p1[0], p2[0], f1, f2)
    
    