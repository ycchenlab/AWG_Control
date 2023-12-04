import numpy as np
import matplotlib.pyplot as plt

# Define parameters
n = 10  # Number of frequencies
duration = 1.0  # Duration of the signal in seconds
sampling_freq = 1000  # Sampling frequency in Hz
start_freq = 400  # Starting frequency in Hz
end_freq = 500  # Ending frequency in Hz

# Generate time vector
t = np.linspace(0, duration, int(sampling_freq * duration), endpoint=False)

# Initialize the waveform
waveform = np.zeros(len(t))

# Calculate frequency spacing based on the start and end frequencies
freq_spacing = (end_freq - start_freq) / (n - 1)

# Generate the waveform with frequencies starting from start_freq to end_freq
for i in range(n):
    frequency = start_freq + i * freq_spacing
    k = frequency / freq_spacing
    phase = 0.5 * np.pi * (k + (k ** 2) / n)
    waveform += np.sin(2 * np.pi * frequency * t + phase)

# Perform FFT on the waveform
fft_result = np.fft.fft(waveform)
freq = np.fft.fftfreq(len(fft_result), 1.0 / sampling_freq)

# Plot the time-domain waveform
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(t, waveform)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Time Domain Waveform')

# Plot the frequency spectrum
plt.subplot(2, 1, 2)
plt.plot(freq, np.abs(fft_result))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('Frequency Spectrum')
plt.xlim(0, sampling_freq / 2)

plt.tight_layout()
plt.show()

