'''
Intensity optimization 1st stage: adjust different RF components to obtain uniform trapping depth.
===============================================================================================
Procedure:
1. Generate a trap centered at 75MHz.
    a. (Input) Input the RF amplitude and the phase mode.
    b. (Manual) Adjust the mirror so that it is centered at the middle of the ccd.
    c. (Manual, input) Record the power using the power meter (and store it). Or change the RF amplitude.
    d. (Auto) Take pictures and adjust the gain (other parameters are fixed) so that the max intensity (I_0) is about 150 ~ 200.
2. Generate multiple traps
    a. (Input) Input the desired number of traps and the frequency spacing.
    b. (Manual) Under large gain (max=24), check if there is some strange pattern (ex: diffraction).
3. Optimization
    a. (Auto) Find the local maxima, and get rid of the points we do not want. Save the position.
    b. (Auto) Implement Gaussian fitting on each trap. Return the intensity (I) and beam waist (sigma_x, sigma_y).
    c. (Auto) Correct each RF amplitude using the formula: A' = A + eta * err * A, where eta (= 0.1) is the learning rate, and err = (I_0 - I)/I_0 is the relative error.
    d. (Auto) Feed the new RF amplitude into AOD and (b), (c) iteratively. Once the stdev of intensity < 0.5, save the data and quit.
'''

from static_trap import StaticTrap
from complete_control_dev_class import AWG
import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import EasyPySpin
import cv2
from PIL import Image
from datetime import datetime

# 1
print('Welcome to intensity optimization program.')
a_0 = float(input('Please enter the RF amplitude (recommended: 0.05 mv): '))
phase_mode = input('Please enter the phase mode (zero/random/formula): ')
print('===================================================')


if a_0 >= 0.3:
    raise ValueError('Amplitude too large. May lead to AOD damage.')
if phase_mode not in ['zero', 'random', 'formula']:
    raise ValueError(f"{phase_mode} does not belong to any of these mode: ['zero', 'random', 'formula']")
elif phase_mode == 'zero':
    print('Warning: Phase mode "zero" may lead to intermodulation!!!')


test = StaticTrap(ntrap=1, mode=phase_mode)
test.amp = np.array([a_0])
test.get_signal()

with open(test.filename, 'r') as f:
    d = json.load(f)

awg = AWG(time=test.duration)
awg.transfer_data(50, d, 0)
awg.execute()
print('Single trap generated!')
print('===================================================')

print('Center the trap to the center of ccd view.')
adjust_a = input('Change RF amplitude (y/n):')
if adjust_a != 'y':
    print('Please restart the program to assign different RF amplitude!!!')
    exit()
central_power = float(input('The power of the single trap (in mW): '))

### Function
def imcapture(filepath, gain=-1):
    cap = EasyPySpin.VideoCapture(0)

    if not cap.isOpened():
        print("Camera can't open\nexit")
        return -1

    cap.set(cv2.CAP_PROP_EXPOSURE, -1)  # -1 sets exposure_time to auto
    cap.set(cv2.CAP_PROP_GAIN, gain)  # -1 sets gain to auto

    ret, frame = cap.read()
    cv2.imwrite(filepath, frame)
    cap.release()
    cv2.destroyAllWindows()

class Fitting():
    def __init__(self, image, center, d):
        self.center = center
        self.d = d
        self.image = image[center[0] - d//2: center[0] + d//2, center[1] - d//2: center[1] + d//2]
        self.sat = self.check_saturation()

    def check_saturation(self):
        threshold = 254
        saturated_mask = im >= threshold
        saturated_per = np.sum(saturated_mask) / (im.shape[0] * im.shape[1]) * 100
        if saturated_per > 1:
            return True
        else:
            return False

    def start_fit(self):
        # return the fitted amplitude
        def gaussian_2d(xy, amplitude, x_mean, y_mean, x_stddev, y_stddev, rotation):
            x, y = xy
            x_rot = (x - x_mean) * np.cos(rotation) - (y - y_mean) * np.sin(rotation)
            y_rot = (x - x_mean) * np.sin(rotation) + (y - y_mean) * np.cos(rotation)
            exponent = -((x_rot / x_stddev) ** 2 + (y_rot / y_stddev) ** 2) / 2
            return amplitude * np.exp(exponent)

        x = np.arange(self.image.shape[1])
        y = np.arange(self.image.shape[0])
        xx, yy = np.meshgrid(x, y)

        xy = (xx.flatten(), yy.flatten())
        data = self.image.flatten()

        bounds = (0, [np.inf, np.inf, np.inf, np.inf, np.inf, 2 * np.pi])
        popt, _ = curve_fit(gaussian_2d, xy, data, p0=[np.max(self.image), self.d//2, self.d//2, 10, 10, 0],
                            bounds=bounds)
        self.fitted_data = gaussian_2d((xx, yy), *popt).reshape(self.image.shape)

        self.I0, self.sigma_x, self.sigma_y = popt[0], popt[3], popt[4]

    def show_image(self):
        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.imshow(self.image, cmap='viridis')
        plt.title('Original Image')

        plt.subplot(1, 2, 2)
        plt.imshow(self.fitted_data, cmap='viridis')
        plt.title(f'Fitted Gaussian with I0 = {self.I0:.2f}')

        plt.tight_layout()
        plt.show()

frame_width = 30 # the area where the trap locates is d^2
gain = 10
central_I0 = 0
print('Adjusting ccd gain...')
while True:
    image = imcapture('single_trap.png', gain)
    im = np.array(Image.open(f'single_trap.png'))
    os.remove('single_trap.png')

    r = Fitting(im, [im.shape[0], im.shape[1]], frame_width)
    r.start_fit()
    if r.I0 < 150:
        gain += 1
    elif r.I0 > 200:
        gain -= 1
    else:
        central_I0 = r.I0
        print(f'Peak intensity (0~255): {central_I0}')
        r.show_image()
        break
print('===================================================')

# 2
ntrap = int(input("Input the number of traps: "))
spacing = float(input("Input the lattice spacing (in MHz): "))

test = StaticTrap(ntrap=ntrap, lattice_spacing=spacing, mode=phase_mode)
test.amp = np.array([a_0 for _ in range(ntrap)])
test.get_signal()

with open(test.filename, 'r') as f:
    signal = json.load(f)

awg = AWG(time=test.duration)
awg.transfer_data(50, signal, 0)
awg.execute()

print('Adjust the gain to 24 in SpinView, and check if there is any strange pattern. \n Press enter to continue...')
input()
print('===================================================')


# 3
print('Intensity optimization start...')
date = datetime.now().strftime('%y%m%d_%H:%M')
im_folder = f'./IntOptD_{date}'
os.makedirs(im_folder)

# find local maxima
print('Finding local maxima...')
imcapture(f'{im_folder}/opt_{0}.png', gain)
image = cv2.imread(f'{im_folder}/opt_{0}.png')
image_np = np.asarray(image)

# Assuming traps are identifiable after preprocessing (thresholding, etc.)
# Perform image processing steps here to identify the traps...

# Example: Convert to grayscale and apply thresholding
_, thresholded = cv2.threshold(image, 150, 200, cv2.THRESH_BINARY)

# Find contours representing the traps
contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Extract trap positions
trap_positions = []
for contour in contours:
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])  # x-coordinate of centroid
        cY = int(M["m01"] / M["m00"])  # y-coordinate of centroid
        trap_positions.append((cX, cY))

# Convert trap_positions to NumPy array (optional)
# not sure if this need to be flipped???
trap_positions = np.array(trap_positions)
print(f'Local maxima found: {trap_positions}')

# plot and check if the local maxima are correct
plt.imshow(image_np)
plt.scatter(trap_positions[:, 0], trap_positions[:, 1], color='red', marker='o')
plt.show()
if trap_positions.shape[0] != ntrap:
    raise Exception(f'Number of local maxima ({trap_positions.shape[0]}) does not match the number of traps ({ntrap})!!!')

# create a dict to store information
data = {
    'info': {
        'central_rf_amp': a_0,
        'central_rf_power': central_power,
        'central_rf_int': central_I0,
        'ntrap': ntrap,
        'lattice_spacing': spacing,
        'phase_mode': phase_mode,
        'trap_position': np.ndarray.tolist(trap_positions),
        'intial_trap_amp': np.ndarray.tolist(test.amp),
        'trap_freq': np.ndarray.tolist(test.freq),
        'trap_phase': np.ndarray.tolist(test.phase),
    }
}

init_amp = test.amp
print('Optimization start...')
for i in range(100):
    print(f'Iteration {i+1}')
    imcapture(f'{im_folder}/opt_{i+1}')
    image = cv2.imread(f'{im_folder}/opt_{0}.png')
    image_np = np.asarray(image)

    intensity, waist_x, waist_y = [], [], []
    for j in range(ntrap):
        r = Fitting(im, trap_positions[j], frame_width)
        r.start_fit()

        intensity.append(r.I0)
        waist_x.append(r.sigma_x)
        waist_y.append(r.sigma_y)

    sigma_int, sigma_wx, sigma_wy = np.std(intensity), np.std(waist_x), np.std(waist_y)
    if sigma_int <= 0.5:
        print('Optimization complete!')
        with open(f'{im_folder}/opt_log.json', 'w') as f:
            json.dump(data, f)
        print('Log created!')
        sys.exit()

    init_amp = np.array([init_amp[k] + 0.1 * (central_I0 - intensity[k]) / central_I0 * init_amp[k] for k in range(ntrap)])

    # generate net trap:
    test = StaticTrap(ntrap=ntrap, lattice_spacing=spacing, mode=phase_mode)
    test.amp = init_amp
    test.get_signal()

    with open(test.filename, 'r') as f:
        signal = json.load(f)

    awg = AWG(time=test.duration)
    awg.transfer_data(50, signal, 0)
    awg.execute()

    # store the data
    data[f'iteration_{i+1}'] = {
        'intensity': intensity,
        'waist_x': waist_x,
        'waist_y': waist_y,
        'std_intensity': sigma_int,
        'std_waist_x': sigma_wx,
        'std_waist_y': sigma_wy,
        'new_amp': np.ndarray.tolist(init_amp)
    }

print('Optimization end. May not complete')
with open(f'{im_folder}/opt_log.json', 'w') as f:
    json.dump(data, f)
print('Log created!')

