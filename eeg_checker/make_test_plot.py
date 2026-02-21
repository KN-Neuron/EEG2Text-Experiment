import os
import glob
import numpy as np
import mne

# filepath: /home/grzegina/documents/projects/EEG2Text-Experiment/eeg_checker/make_test_plot.py
"""EEG Data Quality Check Script

Loads FIF data from data/7/ directory and creates interactive plots
with statistics to verify data quality.
"""

import matplotlib.pyplot as plt

# Set up interactive backend
plt.ion()

# Find FIF files in data/7/ directory
data_dir = "data/szczepanek-najnowsze"
fif_files = glob.glob(os.path.join(data_dir, "*.fif"))

if not fif_files:
    print(f"No FIF files found in {data_dir}")
    exit(1)

print(f"Found {len(fif_files)} FIF file(s):")
for f in fif_files:
    print(f"  - {f}")

# Load the first FIF file (or modify to load specific one)
fif_path = fif_files[0]
print(f"\nLoading: {fif_path}")

raw = mne.io.read_raw_fif(fif_path, preload=True, verbose=False)

# Print basic info
print("\n" + "=" * 60)
print("DATA SUMMARY")
print("=" * 60)
print(f"Sampling frequency: {raw.info['sfreq']} Hz")
print(f"Duration: {raw.times[-1]:.2f} seconds")
print(f"Number of channels: {len(raw.ch_names)}")
print(f"Channels: {', '.join(raw.ch_names)}")

# Get data for statistics
data = raw.get_data()

# Calculate statistics per channel
print("\n" + "=" * 60)
print("CHANNEL STATISTICS (in µV)")
print("=" * 60)
print(f"{'Channel':<10} {'Mean':>12} {'Std':>12} {'Min':>12} {'Max':>12} {'Range':>12}")
print("-" * 70)

stats = {}
for i, ch_name in enumerate(raw.ch_names):
    ch_data = data[i] * 1e6  # Convert to µV
    stats[ch_name] = {
        'mean': np.mean(ch_data),
        'std': np.std(ch_data),
        'min': np.min(ch_data),
        'max': np.max(ch_data),
        'range': np.ptp(ch_data)
    }
    print(f"{ch_name:<10} {stats[ch_name]['mean']:>12.2f} {stats[ch_name]['std']:>12.2f} "
          f"{stats[ch_name]['min']:>12.2f} {stats[ch_name]['max']:>12.2f} {stats[ch_name]['range']:>12.2f}")

# Check for potential issues
print("\n" + "=" * 60)
print("DATA QUALITY CHECKS")
print("=" * 60)

# Check for flat channels
flat_threshold = 1e-7
flat_channels = [ch for i, ch in enumerate(raw.ch_names) if np.std(data[i]) < flat_threshold]
if flat_channels:
    print(f"⚠️  WARNING: Flat channels detected: {flat_channels}")
else:
    print("✓ No flat channels detected")

# Check for high amplitude channels (possible artifacts)
high_amp_threshold = 500e-6  # 500 µV
high_amp_channels = [ch for i, ch in enumerate(raw.ch_names) if np.max(np.abs(data[i])) > high_amp_threshold]
if high_amp_channels:
    print(f"⚠️  WARNING: High amplitude channels (>500µV): {high_amp_channels}")
else:
    print("✓ No abnormally high amplitude channels")

# Check for NaN or Inf values
has_nan = np.any(np.isnan(data))
has_inf = np.any(np.isinf(data))
if has_nan or has_inf:
    print(f"⚠️  WARNING: Data contains {'NaN' if has_nan else ''} {'Inf' if has_inf else ''} values")
else:
    print("✓ No NaN or Inf values")

# Print annotations if any
annotations = raw.annotations
if len(annotations) > 0:
    print(f"\n" + "=" * 60)
    print("ANNOTATIONS")
    print("=" * 60)
    for ann in annotations:
        print(f"  Time: {ann['onset']:.2f}s, Duration: {ann['duration']:.2f}s, Description: {ann['description']}")
else:
    print("\nNo annotations found in the data")

# Create interactive plots
print("\n" + "=" * 60)
print("GENERATING PLOTS...")
print("=" * 60)

# Figure 1: Raw data plot (MNE interactive browser)
print("\nPlot 1: Interactive raw data browser")
fig1 = raw.copy().filter(1, 40, verbose=False).plot(
    scalings='auto',
    title='EEG Raw Data (1-40 Hz filtered)',
    show=False,
    block=False
)

# Figure 2: Power Spectral Density
print("Plot 2: Power Spectral Density")
fig2, ax2 = plt.subplots(figsize=(12, 6))
raw.compute_psd(fmin=0.5, fmax=100, verbose=False).plot(axes=ax2, show=False)
ax2.set_title('Power Spectral Density')
fig2.tight_layout()

# Figure 3: Channel variance bar plot
print("Plot 3: Channel variance comparison")
fig3, ax3 = plt.subplots(figsize=(14, 6))
variances = [np.var(data[i]) * 1e12 for i in range(len(raw.ch_names))]  # Convert to µV²
colors = ['red' if ch in flat_channels or ch in high_amp_channels else 'steelblue' 
          for ch in raw.ch_names]
bars = ax3.bar(raw.ch_names, variances, color=colors)
ax3.set_xlabel('Channel')
ax3.set_ylabel('Variance (µV²)')
ax3.set_title('Channel Variance (Red = Potential Issues)')
ax3.tick_params(axis='x', rotation=45)
fig3.tight_layout()

# Figure 4: Correlation matrix
print("Plot 4: Channel correlation matrix")
fig4, ax4 = plt.subplots(figsize=(12, 10))
corr_matrix = np.corrcoef(data)
im = ax4.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax4.set_xticks(range(len(raw.ch_names)))
ax4.set_yticks(range(len(raw.ch_names)))
ax4.set_xticklabels(raw.ch_names, rotation=45, ha='right')
ax4.set_yticklabels(raw.ch_names)
ax4.set_title('Channel Correlation Matrix')
plt.colorbar(im, ax=ax4, label='Correlation')
fig4.tight_layout()

# Figure 5: Time series for first few channels
print("Plot 5: Sample time series")
n_channels_to_plot = min(8, len(raw.ch_names))
fig5, axes5 = plt.subplots(n_channels_to_plot, 1, figsize=(14, 2*n_channels_to_plot), sharex=True)
times = raw.times
for i in range(n_channels_to_plot):
    axes5[i].plot(times, data[i] * 1e6, linewidth=0.5)
    axes5[i].set_ylabel(f'{raw.ch_names[i]}\n(µV)')
    axes5[i].grid(True, alpha=0.3)
axes5[-1].set_xlabel('Time (s)')
fig5.suptitle('Sample Channel Time Series', fontsize=12)
fig5.tight_layout()

plt.show(block=True)

print("\nDone! Close plot windows to exit.")