# Title: Generation of static trap
# Description:
# 1. Generate and save the sequence of RF signals for the static trap
# 2. To avoid the effect of intermodulation, we need to carefully select the amplitudes and phases of RF tones.
# !!! Amplitude needs to be optimized !!!
# !!! Time needs to be adjusted !!!

import numpy as np
import datetime
import json

# some parameters
R = 625  # sampling rate, unit: MHz
#LATTICE_SPACING  unit: MHz, denotes the frequency spacing between neighboring coordinate points (min: 0.45 MHz in Lukin's paper)


class StaticTrap:
    def __init__(self, lattice_spacing=1.0, ntrap=6, duration=50, mode='formula'):
        CENTRAL_FREQ = 75.0 # unit: MHz, denotes the frequency for the coordinate 0
        # setup: num of traps, {freq, amp, phase} of RF signals, E for total RF signal
        self.ntrap = ntrap
        self.duration = duration
        self.signal_length = R * duration
        self.time = np.linspace(0, duration, self.signal_length, endpoint=False)
        self.freq = np.array([CENTRAL_FREQ - lattice_spacing * ((self.ntrap - 1)/2 - i) for i in range(self.ntrap)])
        self.amp = np.array([0.1 for _ in range(self.ntrap)])
        self.phase = self.get_phase(mode)

        # show status
        print(f'Number of traps: {self.ntrap}')
        print(f'Frequency: {self.freq}')
        print(f'Amplitude: {self.amp}')
        print(f'Phase: {mode}')
        print(f'Signal duration: {duration} us')

        # output
        self.signal = np.zeros(len(self.time))

        # intermodulation
        self.E_2_signal = np.zeros(len(self.time))

    def get_phase(self, mode):
        if mode == "zero":
            phase = np.zeros(self.ntrap)  # zero phases, no relative phase
        elif mode == "random":
            phase = np.random.rand(self.ntrap) * 2 * np.pi  # random phases
        elif mode == "formula":
            phase = np.array([0.0 for _ in range(self.ntrap)])  # phases obtained from a specific formula
            for i in range(self.ntrap):
                k = self.freq[i] / lattice_spacing
                phase[i] = 0.5 * np.pi * (k + 1 * (k ** 2) / self.ntrap)
        else:
            print("Error: mode must be one of these: 'zero', 'random', or 'formula'.")
        return np.around(phase, decimals=5)

    def get_signal(self):
        for i in range(self.ntrap):
            self.signal += self.amp[i] * np.sin(2 * np.pi * self.freq[i] * self.time + self.phase[i])

        self.filename = './Data/static_trap_signal_' + str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) + '.json'
        with open(self.filename, 'w') as f:
            json.dump(self.signal.tolist(), f)


    # for test purpose
    def calc_E_2_signal(self):
        for i in range(self.ntrap):
            for j in range(self.ntrap):
                if i > j:
                    self.E_2_signal += np.sin(((self.phase[i]-self.phase[j]) + 2 * np.pi * (self.freq[i]-self.freq[j]) * self.time))




# # generate a random static trap
# tmp = StaticTrap()
# tmp.get_signal()
# d = tmp.signal
#
#
# # export AWG signal to json
# dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# filename = './Data/static_trap_signal_' + str(dt) + '.json'
# with open(filename, mode='w') as f:
#     json.dump(d, f)
#
# # export trap parameters to json
# l = [tmp.ntrap, tmp.freq.tolist(), tmp.amp.tolist(), tmp.phase.tolist()]
# filename_2 = './Data/static_trap_parameters_' + str(dt) + '.json'
# with open(filename_2, mode='w') as f:
#     json.dump(l, f)

# test = StaticTrap(ntrap= 80, duration=10, mode='formula')
# test.get_signal()
# test.calc_E_2_signal()
#
# import matplotlib.pyplot as plt
# plt.plot(test.time, test.signal)
# plt.show()
