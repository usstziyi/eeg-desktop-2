from __future__ import annotations

import numpy as np

from openbci_realtime_app.processing.filters import detrend_channels, filter_eeg_window


def test_detrend_removes_channel_mean() -> None:
    eeg = np.array([[1.0, 2.0, 3.0], [10.0, 10.0, 10.0]])

    detrended = detrend_channels(eeg)

    assert np.allclose(np.mean(detrended, axis=1), 0.0)


def test_filter_eeg_window_preserves_shape() -> None:
    sampling_rate = 250
    rng = np.random.default_rng(42)
    eeg = rng.normal(size=(8, sampling_rate * 4))

    filtered = filter_eeg_window(eeg, sampling_rate, 1.0, 45.0, 50)

    assert filtered.shape == eeg.shape
    assert np.all(np.isfinite(filtered))

