from __future__ import annotations

import numpy as np

from openbci_realtime_app.processing.band_power import compute_band_powers
from openbci_realtime_app.processing.spectrum import compute_welch_psd


def test_welch_psd_returns_one_row_per_channel() -> None:
    sampling_rate = 250
    t = np.arange(0, 4, 1 / sampling_rate)
    eeg = np.vstack([np.sin(2 * np.pi * 10 * t), np.sin(2 * np.pi * 20 * t)])

    freqs, psd = compute_welch_psd(eeg, sampling_rate, window_seconds=2, overlap_ratio=0.5)

    assert freqs.ndim == 1
    assert psd.shape == (2, freqs.size)


def test_band_power_shape_matches_channels_and_bands() -> None:
    freqs = np.linspace(0, 60, 121)
    psd = np.ones((8, freqs.size))

    names, powers = compute_band_powers(freqs, psd)

    assert names == ("Delta", "Theta", "Alpha", "Beta", "Gamma")
    assert powers.shape == (8, 5)
    assert np.all(powers >= 0)

