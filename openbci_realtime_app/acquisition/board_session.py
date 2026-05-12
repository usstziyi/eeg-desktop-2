from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from brainflow.board_shim import BoardShim

from openbci_realtime_app.acquisition.board_factory import create_board
from openbci_realtime_app.config.settings import BoardSettings

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BoardInfo:
    board_id: int
    sampling_rate: int
    eeg_channels: list[int]
    accel_channels: list[int]
    timestamp_channel: int


class BoardSession:
    """Owns the BrainFlow board object and enforces paired start/stop/release calls."""

    def __init__(self, settings: BoardSettings) -> None:
        self.settings = settings
        self.board: BoardShim | None = None
        self.info: BoardInfo | None = None
        self.prepared = False
        self.streaming = False

    def prepare(self) -> BoardInfo:
        if self.prepared and self.info is not None:
            return self.info

        self.board = create_board(self.settings)
        self.board.prepare_session()
        board_id = self.board.get_board_id()
        self.info = BoardInfo(
            board_id=board_id,
            sampling_rate=BoardShim.get_sampling_rate(board_id),
            eeg_channels=list(BoardShim.get_eeg_channels(board_id)),
            accel_channels=list(BoardShim.get_accel_channels(board_id)),
            timestamp_channel=BoardShim.get_timestamp_channel(board_id),
        )
        self.prepared = True
        LOGGER.info("Prepared BrainFlow board session: %s", self.info)
        return self.info

    def start(self, buffer_size: int = 45000, streamer_params: str = "") -> BoardInfo:
        info = self.prepare()
        if self.board is None:
            raise RuntimeError("Board is not prepared.")
        if not self.streaming:
            self.board.start_stream(buffer_size, streamer_params)
            self.streaming = True
            LOGGER.info("BrainFlow stream started.")
        return info

    def get_current_data(self, num_samples: int) -> np.ndarray:
        if self.board is None or not self.streaming:
            return np.empty((0, 0))
        return self.board.get_current_board_data(num_samples)

    def insert_marker(self, value: float) -> None:
        if self.board is None or not self.streaming:
            raise RuntimeError("Cannot insert marker before stream starts.")
        self.board.insert_marker(value)

    def stop(self) -> None:
        if self.board is not None and self.streaming:
            try:
                self.board.stop_stream()
                LOGGER.info("BrainFlow stream stopped.")
            finally:
                self.streaming = False

    def release(self) -> None:
        if self.board is not None and self.prepared:
            try:
                # release_session is mandatory for real Cyton hardware to free the serial port.
                self.board.release_session()
                LOGGER.info("BrainFlow session released.")
            finally:
                self.prepared = False
                self.streaming = False
                self.board = None
                self.info = None

    def close(self) -> None:
        try:
            self.stop()
        finally:
            self.release()

