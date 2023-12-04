import EasyPySpin
import cv2
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


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
        saturated_mask = self.image >= threshold
        saturated_per = np.sum(saturated_mask) / (self.image.shape[0] * self.image.shape[1]) * 100
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