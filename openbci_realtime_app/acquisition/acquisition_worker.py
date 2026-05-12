from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from openbci_realtime_app.acquisition.board_session import BoardInfo, BoardSession
from openbci_realtime_app.config.settings import AppSettings

LOGGER = logging.getLogger(__name__)


class AcquisitionWorker(QObject):
    data_ready = Signal(object, object)
    started = Signal(object)
    stopped = Signal()
    error = Signal(str)

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.session: BoardSession | None = None
        self.info: BoardInfo | None = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)

    @Slot()
    def start(self) -> None:
        try:
            self.session = BoardSession(self.settings.board)
            self.info = self.session.start()
            self.timer.setInterval(self.settings.display.refresh_ms)
            self.timer.start()
            self.started.emit(self.info)
        except Exception as exc:
            LOGGER.exception("Failed to start acquisition.")
            self.error.emit(str(exc))
            self._close_session()

    @Slot()
    def stop(self) -> None:
        self.timer.stop()
        self._close_session()
        self.stopped.emit()

    @Slot()
    def poll(self) -> None:
        if self.session is None or self.info is None:
            return
        try:
            window_samples = self.info.sampling_rate * self.settings.display.window_seconds
            data = self.session.get_current_data(window_samples)
            if data.size:
                self.data_ready.emit(data, self.info)
        except Exception as exc:
            LOGGER.exception("Acquisition polling failed.")
            self.error.emit(str(exc))
            self.stop()

    def _close_session(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None
            self.info = None

