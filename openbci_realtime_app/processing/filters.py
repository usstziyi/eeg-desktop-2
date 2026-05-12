from __future__ import annotations

import numpy as np
from scipy import signal


def detrend_channels(eeg: np.ndarray) -> np.ndarray:
    if eeg.size == 0:
        return eeg.copy()
    return signal.detrend(eeg, axis=1, type="constant")


def filter_eeg_window(
    eeg: np.ndarray,
    sampling_rate: int,
    low_hz: float,
    high_hz: float,
    notch_hz: int,
) -> np.ndarray:
    """Filter a display window.

    This is intentionally window-based for MVP simplicity. A future strict low-latency
    processing chain can swap this for stateful sosfilt without touching the GUI layer.
    """

    if eeg.size == 0 or eeg.shape[1] < max(8, sampling_rate // 2):
        return eeg.copy()

    nyquist = sampling_rate / 2.0
    high = min(high_hz, nyquist - 1.0)
    low = max(low_hz, 0.1)
    filtered = detrend_channels(eeg)

    if 0 < low < high < nyquist:
        sos = signal.butter(4, [low, high], btype="bandpass", fs=sampling_rate, output="sos")
        filtered = signal.sosfilt(sos, filtered, axis=1)

    if notch_hz > 0 and notch_hz < nyquist:
        b, a = signal.iirnotch(notch_hz, Q=30, fs=sampling_rate)
        filtered = signal.lfilter(b, a, filtered, axis=1)

    return filtered
