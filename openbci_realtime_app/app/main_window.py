from __future__ import annotations

import logging
import time

from PySide6.QtCore import QMetaObject, QThread, Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QMessageBox, QSplitter, QTabWidget, QVBoxLayout, QWidget
from PySide6.QtWidgets import QMainWindow

from openbci_realtime_app.acquisition.acquisition_worker import AcquisitionWorker
from openbci_realtime_app.app.band_power_widget import BandPowerWidget
from openbci_realtime_app.app.control_panel import ControlPanel
from openbci_realtime_app.app.eeg_plot_widget import EegPlotWidget
from openbci_realtime_app.app.spectrum_widget import SpectrumWidget
from openbci_realtime_app.app.status_bar import BoardStatusLabel
from openbci_realtime_app.config.settings import SettingsManager
from openbci_realtime_app.processing.processor_worker import ProcessorWorker
from openbci_realtime_app.processing.types import ProcessedData

LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, settings_manager: SettingsManager) -> None:
        super().__init__()
        self.settings_manager = settings_manager
        self.settings = settings_manager.settings
        self.setWindowTitle("OpenBCI Realtime EEG")

        self.control_panel = ControlPanel(self.settings)
        self.eeg_plot = EegPlotWidget(channel_count=8)
        self.spectrum_widget = SpectrumWidget()
        self.band_power_widget = BandPowerWidget()
        self.board_status = BoardStatusLabel()
        self.board_status.set_idle()

        self.acquisition_thread: QThread | None = None
        self.acquisition_worker: AcquisitionWorker | None = None
        self.processing_thread: QThread | None = None
        self.processor_worker: ProcessorWorker | None = None

        self._build_layout()
        self._wire_controls()

    def _build_layout(self) -> None:
        tabs = QTabWidget()
        tabs.addTab(self.spectrum_widget, "PSD")
        tabs.addTab(self.band_power_widget, "Band Power")

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(self.board_status)
        right_layout.addWidget(tabs)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.eeg_plot)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 5)
        splitter.setStretchFactor(2, 2)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.addWidget(splitter)
        self.setCentralWidget(central)

    def _wire_controls(self) -> None:
        self.control_panel.connect_requested.connect(self.start_acquisition)
        self.control_panel.disconnect_requested.connect(self.stop_acquisition)
        self.control_panel.marker_requested.connect(self.insert_marker)
        self.control_panel.settings_changed.connect(self._save_settings)

    @Slot()
    def start_acquisition(self) -> None:
        if self.acquisition_thread is not None:
            return
        self._save_settings()

        self.acquisition_thread = QThread(self)
        self.processing_thread = QThread(self)
        self.acquisition_worker = AcquisitionWorker(self.settings)
        self.processor_worker = ProcessorWorker(self.settings)
        self.acquisition_worker.moveToThread(self.acquisition_thread)
        self.processor_worker.moveToThread(self.processing_thread)

        self.acquisition_thread.started.connect(self.acquisition_worker.start)
        self.acquisition_worker.data_ready.connect(self.processor_worker.process)
        self.acquisition_worker.started.connect(self._on_acquisition_started)
        self.acquisition_worker.stopped.connect(self._on_acquisition_stopped)
        self.acquisition_worker.error.connect(self._show_error)
        self.processor_worker.processed_ready.connect(self._update_views)
        self.processor_worker.error.connect(self._show_error)

        self.acquisition_thread.finished.connect(self.acquisition_worker.deleteLater)
        self.processing_thread.finished.connect(self.processor_worker.deleteLater)
        self.acquisition_thread.start()
        self.processing_thread.start()
        self.control_panel.set_status("Connecting...")

    @Slot()
    def stop_acquisition(self) -> None:
        # Stop the worker first so it can call BoardShim stop_stream/release_session on its own thread.
        if self.acquisition_worker is not None:
            QMetaObject.invokeMethod(
                self.acquisition_worker,
                "stop",
                Qt.BlockingQueuedConnection,
            )
        self._shutdown_threads()

    @Slot(object)
    def _on_acquisition_started(self, info: object) -> None:
        self.control_panel.set_connected(True)
        self.control_panel.set_status("Streaming")
        self.board_status.set_board_info(info)

    @Slot()
    def _on_acquisition_stopped(self) -> None:
        self.control_panel.set_connected(False)
        self.control_panel.set_status("Stopped")
        self.board_status.set_idle()

    @Slot(object)
    def _update_views(self, processed: ProcessedData) -> None:
        self.eeg_plot.update_data(
            processed.time_axis,
            processed.filtered_eeg,
            self.settings.display.y_scale_uv,
        )
        self.spectrum_widget.update_data(processed.psd_freqs, processed.psd)
        self.band_power_widget.update_data(processed.band_names, processed.band_powers)

    @Slot()
    def insert_marker(self) -> None:
        if self.acquisition_worker is None or self.acquisition_worker.session is None:
            return
        try:
            self.acquisition_worker.session.insert_marker(time.time())
        except Exception as exc:
            self._show_error(str(exc))

    @Slot(str)
    def _show_error(self, message: str) -> None:
        LOGGER.error(message)
        self.control_panel.set_status("Error")
        QMessageBox.warning(self, "OpenBCI Error", message)
        self.stop_acquisition()

    def _shutdown_threads(self) -> None:
        for thread in (self.acquisition_thread, self.processing_thread):
            if thread is not None:
                thread.quit()
                thread.wait(3000)
        self.acquisition_thread = None
        self.processing_thread = None
        self.acquisition_worker = None
        self.processor_worker = None
        self.control_panel.set_connected(False)

    def _save_settings(self) -> None:
        self.settings_manager.save(self.settings)

    def closeEvent(self, event) -> None:  # noqa: ANN001
        self.stop_acquisition()
        self._save_settings()
        super().closeEvent(event)
