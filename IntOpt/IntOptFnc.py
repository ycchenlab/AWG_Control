import numpy as np
from scipy.ndimage import maximum_filter
from scipy.optimize import curve_fit
from PIL import Image
import matplotlib.pyplot as plt
import json

def init_params(ntrap, rfamp):
    positions = np.array([[0, 0] for i in range(ntrap)])
    amplitudes = np.array([rfamp for i in range(ntrap)])
    data = {'ntrap': ntrap, 'positions': positions.tolist(), 'amplitudes': amplitudes.tolist()}
    with open(f'IntOptD/params_0.json', 'w') as f:
        json.dump(data, f)

a = init_params(1, 0.05)