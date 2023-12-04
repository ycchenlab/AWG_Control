import numpy as np
from scipy.optimize import curve_fit
from PIL import Image
import matplotlib.pyplot as plt

load = np.array(Image.open('../IntOpt/IntOptD/example2.png'))
im = load[438:467, 623:652]

def gaussian_2d(xy, amplitude, x_mean, y_mean, x_stddev, y_stddev, rotation):
    x, y = xy
    x_rot = (x - x_mean) * np.cos(rotation) - (y - y_mean) * np.sin(rotation)
    y_rot = (x - x_mean) * np.sin(rotation) + (y - y_mean) * np.cos(rotation)
    exponent = -((x_rot / x_stddev) ** 2 + (y_rot / y_stddev) ** 2) / 2
    return amplitude * np.exp(exponent)

x = np.arange(im.shape[1])
y = np.arange(im.shape[0])
xx, yy = np.meshgrid(x, y)

xy = (xx.flatten(), yy.flatten())
data = im.flatten()

bounds = (0, [np.inf, np.inf, np.inf, np.inf, np.inf, 2 * np.pi])
popt, _ = curve_fit(gaussian_2d, xy, data, p0=[np.max(im), im.shape[1] / 2, im.shape[0] / 2, 10, 10, 0], bounds=bounds)

fitted_data = gaussian_2d((xx, yy), *popt).reshape(im.shape)

plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(im, cmap='viridis')
plt.title('Original Image')

plt.subplot(1, 2, 2)
plt.imshow(fitted_data, cmap='viridis')
plt.title('Fitted Gaussian')

plt.tight_layout()
plt.show()
