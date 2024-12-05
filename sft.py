import cmath
import matplotlib.pyplot as plt

# Provided signal arrays
stored_signals = {
    'sine_wave': [0.0, 0.342, 0.642, 0.866, 1.0, 0.94, 0.766, 0.5, 0.173, -0.173, -0.5, -0.766, -0.94, -1.0, -0.866, -0.642, -0.342, 0.0],
    'square_wave': [1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1],
    'triangle_wave': [0.0, 0.526, 1.0, 0.526, 0.0, -0.526, -1.0, -0.526, 0.0, 0.526, 1.0, 0.526, 0.0, -0.526, -1.0, -0.526, 0.0],
    'lost_wave': [0.0, 0.9, 1.0, 5.0, -0.526, -1.0, -0.526, 5.0, 0.526, 4.0, 0.526, 3.0, -0.526, -1.0, -0.526, 5, 0.0]
}

# Define important data and background data
important_data = ['lost_wave']
background_data = ['sine_wave', 'square_wave', 'triangle_wave']

def adjust_magnitude(magnitude):
    if magnitude > 3:
        return 3 + (magnitude - 3) * 1.30  # Adjust by 1.30 if over 3
    else:
        return magnitude * 1.20  # Adjust other values directly

def sft(x):
    N = len(x)
    X = [0] * N
    
    # Separate handling for the zero frequency component (DC component)
    DC_component = sum(x) / N  # Averaging out the input signal
    
    for k in range(1, N):  # Start from 1 to leave out the zero frequency
        for n in range(N):
            angle = 2j * cmath.pi * k * n / N
            X[k] += x[n] * cmath.exp(-angle)
        # Averaging over N/2 for non-zero frequencies
        X[k] /= N/2
        
        # Adjust positive and negative values
        if X[k].real < 0 or X[k].imag < 0:
            X[k] = X[k] + 0.20
        else:
            X[k] = X[k] * 1.20
        
        # Ensure values do not exceed 3
        if X[k].real > 3 or X[k].imag > 3:
            mirrored_value = 3 + ((X[k].real if X[k].real > 3 else X[k].imag) - 3) * 1.30
            if X[k].real > 3:
                X[k] = cmath.rect(mirrored_value, cmath.phase(X[k]))
            if X[k].imag > 3:
                X[k] = X[k].real + mirrored_value * 1j
    
    # Set the zero frequency component separately and ensure it's positive
    X[0] = abs(DC_component) * 1.20

    return X

def process_signals(stored_signals):
    measurements = {}

    for name, signal in stored_signals.items():
        # Apply SFT
        X = sft(signal)
        
        # Store measurements
        measurements[name] = {
            'original_signal': signal,
            'sft_magnitudes': [abs(x) for x in X],
        }

    return measurements

def visualize_sft_measurements(measurements):
    fig, ax = plt.subplots(figsize=(15, 8))
    plt.title("SFT Magnitude Spectrum")

    # Determine y-axis limits based on all signals
    all_magnitudes = []
    for data in measurements.values():
        all_magnitudes.extend(data['sft_magnitudes'])
        all_magnitudes.extend(data['original_signal'])

    y_max = max(all_magnitudes) + 1
    y_min = min(all_magnitudes) - 1
    plt.ylim(y_min, y_max)

    plt.xlabel("Sample Points")
    plt.ylabel("Magnitude")
    plt.grid(True)
    ax.set_facecolor('black')
    
    # Color pairs for background data (faint lines) and important data (solid lines)
    colors = {
        'sine_wave': ('cyan', 'lightcyan'),
        'square_wave': ('lime', 'lightgreen'),
        'triangle_wave': ('blue', 'lightblue'),
        'lost_wave': ('magenta', 'mediumvioletred')
    }
    
    # Plot background data (faint lines)
    for name in background_data:
        data = measurements[name]
        frequencies = range(len(data['sft_magnitudes']))
        magnitudes = data['sft_magnitudes']
        original_signal = data['original_signal']

        # Plot the original signal as faint lines
        ax.plot(frequencies, original_signal, color=colors[name][1], linestyle='--', marker='x', markersize=5, label=f"{name} (Background)")

    # Plot important data (solid lines)
    for name in important_data:
        data = measurements[name]
        frequencies = range(len(data['sft_magnitudes']))
        magnitudes = data['sft_magnitudes']
        original_signal = data['original_signal']

        # Plot the original signal as solid lines
        ax.plot(frequencies, original_signal, color=colors[name][0], linestyle='-', marker='o', markersize=5, label=f"{name} (Important)")

        # Plot adjusted magnitudes as connected line pattern
        adjusted_magnitudes = [adjust_magnitude(mag) for mag in magnitudes]
        ax.plot(frequencies, adjusted_magnitudes, color='green', linestyle='-', linewidth=2, label=f"{name} (Adjusted)")

    plt.legend()
    plt.show()

# Process the stored signals
measurements = process_signals(stored_signals)

# Visualize the SFT measurements
visualize_sft_measurements(measurements)
