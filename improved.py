import cmath
import matplotlib.pyplot as plt
import random

# Example placeholder for well-known test data with optional timestamps
stored_signals = {
    'sine_wave': {
        'signal': [0.0, 0.342, 0.642, 0.866, 1.0, 0.94, 0.766, 0.5, 0.173, -0.173, -0.5, -0.766, -0.94, -1.0, -0.866, -0.642, -0.342, 0.0],
        'timestamps': [('2024-12-26 06:00:00', '2024-12-26 06:18:00')]
    },
    'square_wave': {
        'signal': [1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1],
        'timestamps': [('2024-12-26 06:20:00', '2024-12-26 06:40:00')]
    },
    'triangle_wave': {
        'signal': [0.0, 0.526, 1.0, 0.526, 0.0, -0.526, -1.0, -0.526, 0.0, 0.526, 1.0, 0.526, 0.0, -0.526, -1.0, -0.526, 0.0],
        'timestamps': [('2024-12-26 06:45:00', '2024-12-26 07:00:00')]
    }
}

def adjust_magnitude(magnitude):
    if magnitude > 3:
        return 3 - (magnitude - 3) * 0.20  # Adjust by 0.20 if over 3
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
            mirrored_value = 3 - ((X[k].real if X[k].real > 3 else X[k].imag) - 3)
            if X[k].real > 3:
                X[k] = cmath.rect(mirrored_value, cmath.phase(X[k]))
            if X[k].imag > 3:
                X[k] = X[k].real + mirrored_value * 1j
    
    # Set the zero frequency component separately and ensure it's positive
    X[0] = abs(DC_component) * 1.20

    return X

def process_signals(stored_signals):
    measurements = {}

    for name, data in stored_signals.items():
        signal = data['signal']
        timestamps = data.get('timestamps', [('', '')])
        
        # Apply SFT
        X = sft(signal)
        
        # Store measurements
        measurements[name] = {
            'original_signal': signal,
            'sft_magnitudes': [abs(x) for x in X],
            'timestamps': timestamps
        }

    return measurements

def visualize_sft_measurements(measurements):
    fig, ax = plt.subplots(figsize=(15, 8))
    plt.title("SFT Magnitude Spectrum with Mohr's Circles")
    plt.xlabel("Sample Points")
    plt.ylabel("Magnitude")
    plt.ylim(-2, 5)
    plt.grid(True)
    ax.set_facecolor('black')
    
    # Define color palettes
    dark_colors = ['darkred', 'darkblue', 'darkgreen', 'darkmagenta', 'darkorange', 'darkcyan']
    neon_colors = ['red', 'blue', 'green', 'magenta', 'orange', 'cyan']

    used_dark_colors = set()
    offset = 0.25  # Offset for the timestamps to avoid overlap
    
    for index, (name, data) in enumerate(measurements.items()):
        frequencies = range(len(data['sft_magnitudes']))
        magnitudes = data['sft_magnitudes']
        original_signal = data['original_signal']
        timestamps = data['timestamps'][0]

        # Ensure distinct dark and neon color pairs
        available_dark_colors = list(set(dark_colors) - used_dark_colors)
        if not available_dark_colors:
            used_dark_colors.clear()
            available_dark_colors = dark_colors

        dark_color = random.choice(available_dark_colors)
        neon_color = neon_colors[dark_colors.index(dark_color)]
        used_dark_colors.add(dark_color)

        # Plot the original signal (neon colors)
        ax.plot(frequencies, original_signal, color=neon_color, linestyle='--', marker='x', markersize=5, label=f"{name} (Original)")

        # Plot the adjusted magnitudes (darker colors)
        ax.plot(frequencies, magnitudes, color=dark_color, marker='o', markersize=5, label=name)

        for i, magnitude in enumerate(magnitudes):
            adjusted_magnitude = adjust_magnitude(magnitude)
            plot_mohrs_circle(adjusted_magnitude, ax, frequencies[i], original_signal[i])

            # Add a dot at the adjusted peak height
            plt.plot([frequencies[i]], [adjusted_magnitude], 'go')  # Green dot at the peak height

        # Add timestamp annotations with indicators
        ax.annotate(f"Start: {timestamps[0]}",
                    xy=(frequencies[0], -1.5 - index * offset), xycoords='data',
                    bbox=dict(boxstyle="round,pad=0.3", edgecolor=dark_color, facecolor='wheat', alpha=0.6),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color=dark_color))
        
        ax.annotate(f"End: {timestamps[1]}",
                    xy=(frequencies[-1], -1.5 - index * offset), xycoords='data',
                    bbox=dict(boxstyle="round,pad=0.3", edgecolor=dark_color, facecolor='wheat', alpha=0.6),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color=dark_color))
        
        # Place indicators outside the timestamp area
        ax.plot(frequencies[0], 2 - index * offset, marker='v', markersize=10, color=dark_color)
        ax.plot(frequencies[-1], 2 - index * offset, marker='v', markersize=10, color=dark_color)

    plt.legend()
    plt.show()

def plot_mohrs_circle(magnitude, ax, position, original_value):
    # Compute the adjusted stress
    sigma_avg = magnitude / 2
    R = magnitude / 2

    # Define the circle
    circle = plt.Circle((position, sigma_avg), R, color='r', fill=True)

    ax.add_artist(circle)
    ax.plot([position - R, position + R], [sigma_avg, sigma_avg], 'r-')  # Red line at the middle of the circle

    # Draw lines within the circle to represent intersections
    if original_value != magnitude:
        intersection_left = (position - R, sigma_avg)
        intersection_right = (position + R, sigma_avg)
        ax.plot([position, intersection_left[0]], [sigma_avg, intersection_left[1]], 'r--')  # Line to the left intersection
        ax.plot([position, intersection_right[0]], [sigma_avg, intersection_right[1]], 'r--')  # Line to the right intersection
    else:
        ax.plot([position], [sigma_avg], 'ro')  # Single dot if there's only one point

# Process the stored signals
measurements = process_signals(stored_signals)

# Visualize the SFT measurements
visualize_sft_measurements(measurements)
