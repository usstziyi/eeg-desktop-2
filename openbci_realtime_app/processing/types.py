from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ProcessedData:
    raw_eeg: np.ndarray
    filtered_eeg: np.ndarray
    time_axis: np.ndarray
    psd_freqs: np.ndarray
    psd: np.ndarray
    band_names: tuple[str, ...]
    band_powers: np.ndarray
    sampling_rate: int

