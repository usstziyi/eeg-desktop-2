from __future__ import annotations

import logging

import numpy as np
from PySide6.QtCore import QObject, Signal, Slot

from openbci_realtime_app.acquisition.board_session import BoardInfo
from openbci_realtime_app.config.settings import AppSettings
from openbci_realtime_app.processing.band_power import compute_band_powers
from openbci_realtime_app.processing.filters import filter_eeg_window
from openbci_realtime_app.processing.spectrum import compute_welch_psd
from openbci_realtime_app.processing.types import ProcessedData

LOGGER = logging.getLogger(__name__)


class ProcessorWorker(QObject):
    processed_ready = Signal(object)
    error = Signal(str)

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings

    @Slot(object, object)
    def process(self, data: np.ndarray, info: BoardInfo) -> None:
        try:
            if data.size == 0:
                return
            eeg = np.asarray(data[info.eeg_channels, :], dtype=float)
            if eeg.size == 0:
                return

            processing = self.settings.processing
            filtered = filter_eeg_window(
                eeg,
                info.sampling_rate,
                processing.bandpass_low_hz,
                processing.bandpass_high_hz,
                processing.notch_hz,
            )
            freqs, psd = compute_welch_psd(
                filtered,
                info.sampling_rate,
                processing.psd_window_seconds,
                processing.welch_overlap_ratio,
            )
            band_names, band_powers = compute_band_powers(freqs, psd)
            time_axis = np.arange(eeg.shape[1], dtype=float) / info.sampling_rate
            self.processed_ready.emit(
                ProcessedData(
                    raw_eeg=eeg,
                    filtered_eeg=filtered,
                    time_axis=time_axis,
                    psd_freqs=freqs,
                    psd=psd,
                    band_names=band_names,
                    band_powers=band_powers,
                    sampling_rate=info.sampling_rate,
                )
            )
        except Exception as exc:
            LOGGER.exception("Processing failed.")
            self.error.emit(str(exc))

