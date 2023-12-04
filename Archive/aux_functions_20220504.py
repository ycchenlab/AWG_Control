import sys
import math
import numpy as np
from scipy.interpolate import CubicSpline

def read_setup_from_txt(file_path):  # for cubic interpolation
    
    '''This function reads in a .txt file containing the procedures (frequencies, relative amp and phase, duration)
    that describe the RF signal for the 2D AOD to complete the pre-determined movement process

    The txt file for setup should contain the following information in the following order:
    Line 1 of the .txt file: Sampling frequency in MHz. For this board (M4i.6622-x8), 50 MHz < sampling frequency < 625 MHz

    The subsequent lines are grouped into sets of 3 lines.
    The first and second lines contain two sets of frequencies of equal number along with their relative amplitudes and phases.
    The number of frequencies listed denotes the number of frequency components in the output RF signal.
    The i-th output signal frequency will change from the i-th freq in Line 1 into the i-th freq in Line 2.
    This frequency transition follows a cubic interpolation frequency curve, and the duration is listed in Line 3.
    The detailed explanation of each line is as follows:
    Line 1: This line contains number of frequencies, frequency components (in MHz), relative amplitude, relative phase (in radian)
            The Data in this line is organized as follows (n denotes the number of frequencies):
            n, n nums denoting the n frequencies, n nums denoting the relative amp, n nums denoting the relative phase
            Note that the numbers are separated by a whitespace.
            Also note that the relative amplitude may be any positive number. What matters is the relative amplitude.
        Ex: 3 75.000 76.000 77.000 1 1 1 0 0.5 1
    Line 2: This line contains the ending frequencies for the movement
        Ex: 3 77.000 78.000 79.000
    Line 3: This line contains the time for this step (frequency transition) in us (microsecond)
        Ex: 6000'''

    freq_list_1 = []
    freq_list_2 = []
    time_list = []
    amp_list = []
    phase_list = []
    time = 0  # the duration of the whole operation
    with open(file_path) as f:
        R = int(f.readline())
        while True:
            f1 = f.readline().strip().split()  # extract the initial frequnecy of sub-process
            f2 = f.readline().strip().split()  # extract the final frequency of sub-process
            t  = f.readline().strip() # extract the duration of sub-process
            if not t: break #EOF
            num_freq = int(f1[0])
            a1 = [float(f1[num_freq + 1 + i]) for i in range(num_freq)]
            amp = [a/sum(a1) for a in a1] # assume that the relative strength does not change for f1, f2
            phase = [float(f1[2*num_freq + 1 + i]) for i in range(num_freq)]
            f1 = f1[1:num_freq+1] # contains only the frequency components
            f2 = f2[1:num_freq+1] # contains only the frequency components       
            freq_list_1.append([float(num) for num in f1])
            freq_list_2.append([float(num) for num in f2])
            time_list.append(int(t))
            amp_list.append(amp)
            phase_list.append(phase)
            time = time + int(t)
    return R, time, freq_list_1, freq_list_2, time_list, amp_list, phase_list

def cubic_interp_freq_list(R, transit_time, s_freq, e_freq):
    # R:              sampling rate of the AWG in MHz.
    # transit_time:   time (in us) it takes to change the frequency from start to end.
    # s_freq/e_freq:  start/end frequency
    
    # This function returns a list containing frequency steps that are generated using cubic interpolation.
    num_pts = int(math.floor(R * transit_time)) # use floor to prevent decimals
    x = [1, num_pts]
    y = [s_freq, e_freq]
    cub_interp = CubicSpline(x, y)
    return cub_interp(range(1, num_pts+1)).tolist()

# The following functions are for generating the frequency file from coordinates 
# These functions are currently called in the file: generate_freq_list_20220505.py

def move_horizontal(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, mult_freq_dir, amp, phase):
    coor_diff = 0
    for coor1, coor2 in zip(p1, p2):
        if abs(coor2[0] - coor1[0]) > coor_diff:
            coor_diff = abs(coor2[0] - coor1[0]) 
    if mult_freq_dir == 'x':
        freq_list_1 = []
        freq_list_2 = []
        for points in p1: # collect all the initial freq components in the x direction
            freq_list_1.append(central_freq + lattice_spacing*points[0]) # convert coordinates into frequencies
        for points in p2: # collect all the initial freq components in the x direction
            freq_list_2.append(central_freq + lattice_spacing*points[0]) # convert coordinates into frequencies
        y_freq = p1[0][1] * lattice_spacing + central_freq
        
        f2.write('1 ' + '%.3f' % (y_freq) + ' 1 0\n') # only one freq component in the y dir
        f2.write('1 ' + '%.3f' % (y_freq) + ' 1\n')
        f1.write(str(len(freq_list_1)))
        for freq in freq_list_1:
            f1.write(' %.3f' % (freq))
        for a in amp:
            f1.write(' %.3f' % (a)) 
        for p in phase:
            f1.write(' %.5f' % (p)) 
        f1.write('\n')
        f1.write(str(len(freq_list_2)))
        for freq in freq_list_2:
            f1.write(' %.3f' % (freq))
        f1.write('\n')
        f1.write(str(transit_time * coor_diff) + '\n') # write the total time
        f2.write(str(transit_time * coor_diff) + '\n')
    elif mult_freq_dir == 'y':
        freq_list = []
        for points in p1: # collect all the initial freq components in the y direction
            freq_list.append(central_freq + lattice_spacing*points[1]) # convert coordinates into frequencies
        x_freq_init = p1[0][0] * lattice_spacing + central_freq
        x_freq_final = p2[0][0] * lattice_spacing + central_freq
        f1.write('1 ' + '%.3f ' % (x_freq_init) + ' 1 0\n') # only one freq component in the x dir
        f1.write('1 ' + '%.3f ' % (x_freq_final) + ' 1\n')
        f2.write(str(len(freq_list))) 
        for freq in freq_list:
            f2.write(' %.3f' % (freq))
        for a in amp:
            f2.write(' %.3f' % (a)) 
        for p in phase:
            f2.write(' %.5f' % (p)) 
        f2.write('\n')
        f2.write(str(len(freq_list)))
        for freq in freq_list:
            f2.write(' %.3f' % (freq))
        f2.write('\n')
        f1.write(str(transit_time * coor_diff) + '\n') # write the total time
        f2.write(str(transit_time * coor_diff) + '\n')

def move_vertical(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, mult_freq_dir, amp, phase):
    coor_diff = 0
    for coor1, coor2 in zip(p1, p2):
        if abs(coor2[1] - coor1[1]) > coor_diff:
            coor_diff = abs(coor2[1] - coor1[1]) 
    if mult_freq_dir == 'x':
        freq_list = []
        for points in p1: # collect all the initial freq components in the x direction
            freq_list.append(central_freq + lattice_spacing*points[0]) # convert coordinates into frequencies
        y_freq_init = p1[0][1] * lattice_spacing + central_freq
        y_freq_final = p2[0][1] * lattice_spacing + central_freq
        f1.write(str(len(freq_list)))
        for freq in freq_list:
            f1.write(' %.3f' % (freq))
        for a in amp:
            f1.write(' %.3f' % (a)) 
        for p in phase:
            f1.write(' %.5f' % (p)) 
        f1.write('\n')
        f1.write(str(len(freq_list)))
        for freq in freq_list:
            f1.write(' %.3f' % (freq))
        f1.write('\n')
        f2.write('1 ' + '%.3f ' % (y_freq_init) + ' 1 0\n') # only one freq component in the y dir
        f2.write('1 ' + '%.3f ' % (y_freq_final) + ' 1\n')
        f1.write(str(transit_time * coor_diff) + '\n') # write the total time
        f2.write(str(transit_time * coor_diff) + '\n')
    elif mult_freq_dir == 'y':
        freq_list_1 = []
        freq_list_2 = []
        for points in p1: # collect all the initial freq components in the x direction
            freq_list_1.append(central_freq + lattice_spacing*points[1]) # convert coordinates into frequencies
        for points in p2: # collect all the initial freq components in the x direction
            freq_list_2.append(central_freq + lattice_spacing*points[1]) # convert coordinates into frequencies
        x_freq = p1[0][0] * lattice_spacing + central_freq
        
        f1.write('1 ' + '%.3f' % (x_freq) + ' 1 0\n') # only one freq component in the x dir
        f1.write('1 ' + '%.3f' % (x_freq) + ' 1\n')
        f2.write(str(len(freq_list_1)))
        for freq in freq_list_1:
            f2.write(' %.3f ' % (freq))
        for a in amp:
            f2.write(' %.3f' % (a)) 
        for p in phase:
            f2.write(' %.5f' % (p)) 
        f2.write('\n')
        f2.write(str(len(freq_list_2)))
        for freq in freq_list_2:
            f2.write(' %.3f' % (freq))
        f2.write('\n')
        f1.write(str(transit_time * coor_diff) + '\n') # write the total time
        f2.write(str(transit_time * coor_diff) + '\n')

def no_move(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, mult_freq_dir, amp, phase):
    if mult_freq_dir == 'x':
        freq_list = []
        for points in p1: # collect all the initial freq components in the x direction
            freq_list.append(central_freq + lattice_spacing*points[0]) # convert coordinates into frequencies
        y_freq = p1[0][1] * lattice_spacing + central_freq
        f1.write(str(len(freq_list)))
        for freq in freq_list:
            f1.write(' %.3f' % (freq))
        for a in amp:
            f1.write(' %.3f' % (a)) 
        for p in phase:
            f1.write(' %.5f' % (p)) 
        f1.write('\n')
        f1.write(str(len(freq_list)))
        for freq in freq_list:
            f1.write(' %.3f ' % (freq))
        f1.write('\n')
        f2.write('1 ' + '%.3f' % (y_freq) + ' 1 0\n') # only one freq component in the y dir
        f2.write('1 ' + '%.3f' % (y_freq) + ' 1\n')
        f1.write(str(transit_time) + '\n') # write the total time
        f2.write(str(transit_time) + '\n')
    if mult_freq_dir == 'y':
        freq_list = []
        for points in p1: # collect all the initial freq components in the x direction
            freq_list.append(central_freq + lattice_spacing*points[1]) # convert coordinates into frequencies
        x_freq = p1[0][0] * lattice_spacing + central_freq
        f2.write(str(len(freq_list)))
        for freq in freq_list:
            f2.write(' %.3f' % (freq))
        for a in amp:
            f2.write(' %.3f' % (a)) 
        for p in phase:
            f2.write(' %.5f' % (p)) 
        f2.write('\n')
        f2.write(str(len(freq_list)))
        for freq in freq_list:
            f2.write(' %.3f ' % (freq))
        f2.write('\n')
        f1.write('1 ' + '%.3f' % (x_freq) + ' 1 0\n') # only one freq component in the x dir
        f1.write('1 ' + '%.3f' % (x_freq) + ' 1\n')
        f1.write(str(transit_time) + '\n') # write the total time
        f2.write(str(transit_time) + '\n')
        

def write_step_multi_freq(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, amp, phase):
    # p1 is a list containing (possibly) multiple tuples indicating the initial coordinates of the points
    # p2 denotes the coordinates of the next position
    num_freq = len(p1)
    if abs(p1[0][0] - p2[0][0]) != 0: # the case where the next move is horizontal
        print('Move horizontal')
        if p1[0][0] != p1[1][0]: # multi freq in x direction
            direction = 'x'
            move_horizontal(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, direction, amp, phase)
        elif p1[0][0] == p1[1][0]: # multi freq in y direction
            direction = 'y'
            move_horizontal(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, direction, amp, phase)
            
    elif abs(p1[0][1] - p2[0][1]) != 0: # the case where the next move is vertical
        print('Move vertical')
        if p1[0][0] != p1[1][0]: # multi freq in x direction
            direction = 'x'
            move_vertical(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, direction, amp, phase)
        elif p1[0][0] == p1[1][0]: # multi freq in y direction
            direction = 'y'
            move_vertical(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, direction, amp, phase)
                        
    else: # the case where the two sets of points have the same coordinates
        if p1[0][0] != p1[1][0]: # multi freq in x direction
            direction = 'x'
            no_move(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, direction, amp, phase)
        elif p1[0][0] == p1[1][0]: # multi freq in y direction
            direction = 'y'
            no_move(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2, direction, amp, phase)

def write_step_single_freq(central_freq, lattice_spacing, transit_time, p1, p2, f1, f2):
    if abs(p1[0] - p2[0]) != 0: # the case where the next move is horizontal
        coor_diff = abs(p1[0] - p2[0])
        print('Move horizontal')
        start_freq = central_freq + lattice_spacing * p1[0]
        end_freq = central_freq + lattice_spacing * p2[0]
        invariant_freq = central_freq + lattice_spacing * p1[1]
        f1.write('1 %.3f' % (start_freq) + ' 1 0\n')
        f1.write('1 %.3f' % (end_freq) + ' 1\n')
        f2.write('1 %.3f' % (invariant_freq) + ' 1 0\n') # no change in vertical direction   
        f2.write('1 %.3f' % (invariant_freq) + ' 1\n')
        f1.write(str(transit_time * coor_diff) + '\n') # write the total time
        f2.write(str(transit_time * coor_diff) + '\n')
    elif abs(p1[1] - p2[1]) != 0: # the case where the next move is vertical
        coor_diff = abs(p1[1] - p2[1])
        print('Move vertical')
        start_freq = central_freq + lattice_spacing * p1[1]
        end_freq = central_freq + lattice_spacing * p2[1]
        invariant_freq = central_freq + lattice_spacing * p1[0]
        f2.write('1 %.3f' % (start_freq) + ' 1 0\n')
        f2.write('1 %.3f' % (end_freq) + ' 1\n')
        f1.write('1 %.3f' % (invariant_freq) + ' 1 0\n') # no change in horizontal direction   
        f1.write('1 %.3f' % (invariant_freq) + ' 1\n')
        f1.write(str(transit_time * coor_diff) + '\n') # write the total time
        f2.write(str(transit_time * coor_diff) + '\n')             
    else: # the case where the two points have the same coordinate
        invariant_freq_1 = central_freq + lattice_spacing * p1[0]
        invariant_freq_2 = central_freq + lattice_spacing * p1[1]
        f1.write('1 %.3f' % (invariant_freq_1) + ' 1 0\n') # no change in horizontal direction   
        f1.write('1 %.3f' % (invariant_freq_1) + ' 1\n')
        f2.write('1 %.3f' % (invariant_freq_2) + ' 1 0\n') # no change in vertical direction   
        f2.write('1 %.3f' % (invariant_freq_2) + ' 1\n')
        f1.write(str(transit_time) + '\n') # write the total time
        f2.write(str(transit_time) + '\n')

# f_name = 'test_cubic_input_rel_phase.txt'
# R, time, freq_list_1, freq_list_2, time_list, amp_list, phase_list = read_from_txt_mixed_freq_cubic_rel_phase(f_name)
# print(freq_list_1)
# print(freq_list_2)
# print(amp_list)
# print(phase_list)

# print(len(cubic_interp_freq_list(200, 50, 76, 75)))