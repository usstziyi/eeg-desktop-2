from __future__ import annotations

import numpy as np

BANDS: tuple[tuple[str, float, float], ...] = (
    ("Delta", 0.5, 4.0),
    ("Theta", 4.0, 8.0),
    ("Alpha", 8.0, 13.0),
    ("Beta", 13.0, 30.0),
    ("Gamma", 30.0, 45.0),
)


def compute_band_powers(freqs: np.ndarray, psd: np.ndarray) -> tuple[tuple[str, ...], np.ndarray]:
    names = tuple(name for name, _, _ in BANDS)
    if freqs.size == 0 or psd.size == 0:
        return names, np.zeros((0, len(BANDS)))

    powers = np.zeros((psd.shape[0], len(BANDS)), dtype=float)
    for band_index, (_, low, high) in enumerate(BANDS):
        mask = (freqs >= low) & (freqs < high)
        if np.any(mask):
            powers[:, band_index] = np.trapz(psd[:, mask], freqs[mask], axis=1)
    return names, powers

