from __future__ import annotations

import numpy as np
from scipy import signal


def compute_welch_psd(
    eeg: np.ndarray,
    sampling_rate: int,
    window_seconds: int,
    overlap_ratio: float,
) -> tuple[np.ndarray, np.ndarray]:
    if eeg.size == 0:
        return np.empty(0), np.empty((0, 0))

    nperseg = min(eeg.shape[1], max(32, int(window_seconds * sampling_rate)))
    if nperseg < 8:
        return np.empty(0), np.empty((eeg.shape[0], 0))

    overlap_ratio = min(max(overlap_ratio, 0.0), 0.9)
    noverlap = int(nperseg * overlap_ratio)
    freqs, psd = signal.welch(
        eeg,
        fs=sampling_rate,
        axis=1,
        nperseg=nperseg,
        noverlap=noverlap,
        scaling="density",
    )
    return freqs, psd

