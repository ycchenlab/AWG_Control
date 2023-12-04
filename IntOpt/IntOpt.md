# RF Intensity Optimization
## Steps
1. Create single trap, align it to the center of CCD, and adjust its power to the desired value.
   (Typically, at 75MHz, RF=0.05mV corresponds to 0.1mW trap)
2. Calculate its intensity on CCD and set I_0 (about 150, saturated at 255)
3. Capture an image with 10 traps, RF = 0.05 each, and readjust its size if needed (60 * 360)
4. In each iteration, the input is the image. After fitting with Gaussian function, the output is the change of RF amplitudes.
5. The original guess A' = A * mean(I)/I will lead to unexpected distribution and the final intensity is hard to predict.
The update rule is A' = A * sqrt(I_0 / I). The reason why I put a square root is to prevent over-updating.
6. Repeat several times until the trap intensity becomes uniform.

## 1116 Experiment
1. RF frequencies: 10 traps, 70.5 ~ 79.5 MHz, step = 1Mhz
2. Trap power: 0.1mW each and corresponds to 150 on CCD
3. RF amplitudes:
   1. [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
   2. [0.1709, 0.1075, 0.0746, 0.0597, 0.0604, 0.0508, 0.0546, 0.0667, 0.1148, 0.196]
   3. [0.0889, 0.0777, 0.0717, 0.0835, 0.0846, 0.0794, 0.079, 0.0806, 0.0867, 0.0972]
   4. [0.1367, 0.0942, 0.0682, 0.0519, 0.054, 0.0455, 0.0493, 0.0594, 0.1007, 0.1444]
   5. [0.0766, 0.0657, 0.0606, 0.0691, 0.069, 0.0651, 0.0652, 0.0668, 0.0723, 0.0828]
   6. [0.1134, 0.081, 0.0614, 0.0443, 0.0461, 0.0399, 0.0429, 0.0511, 0.0845, 0.1208]
   7. [0.077, 0.0664, 0.0599, 0.0678, 0.0667, 0.064, 0.0636, 0.0649, 0.0707, 0.0833]
   8. [0.0926, 0.0734, 0.0618, 0.0553, 0.0557, 0.0511, 0.0528, 0.0578, 0.0764, 0.1]
4. Mean intensity = 156.069, std = 1.774
5. In the first 7 updates, I used the update formula A' = A * (I_0 / I) and found that the stdev's fluctuate between
50~60. The intensity didn't become uniform. After I changed the formula, it converged quickly.

## Some Future Work
1. To capture images with python package (failed but I still want to try).
2. Store the standard deviation of each trap (I only printed out in the last experiment).
3. Make a GUI (more user-friendly).
