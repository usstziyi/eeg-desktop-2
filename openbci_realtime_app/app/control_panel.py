from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from openbci_realtime_app.acquisition.ports import list_serial_ports
from openbci_realtime_app.config.settings import AppSettings


class ControlPanel(QWidget):
    connect_requested = Signal()
    disconnect_requested = Signal()
    marker_requested = Signal()
    settings_changed = Signal()

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["synthetic", "cyton"])
        self.mode_combo.setCurrentText(settings.board.mode)

        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.refresh_ports()
        self.port_combo.setCurrentText(settings.board.serial_port)

        self.refresh_ports_button = QPushButton("Refresh")
        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")
        self.marker_button = QPushButton("Marker")

        self.window_spin = QSpinBox()
        self.window_spin.setRange(1, 30)
        self.window_spin.setValue(settings.display.window_seconds)

        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(20, 1000)
        self.refresh_spin.setValue(settings.display.refresh_ms)

        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(10, 10000)
        self.scale_spin.setValue(settings.display.y_scale_uv)

        self.low_spin = QDoubleSpinBox()
        self.low_spin.setRange(0.1, 100.0)
        self.low_spin.setDecimals(1)
        self.low_spin.setValue(settings.processing.bandpass_low_hz)

        self.high_spin = QDoubleSpinBox()
        self.high_spin.setRange(1.0, 120.0)
        self.high_spin.setDecimals(1)
        self.high_spin.setValue(settings.processing.bandpass_high_hz)

        self.notch_combo = QComboBox()
        self.notch_combo.addItems(["0", "50", "60"])
        self.notch_combo.setCurrentText(str(settings.processing.notch_hz))

        self.status_label = QLabel("Idle")
        self._build_layout()
        self._wire_signals()
        self.set_connected(False)

    def _build_layout(self) -> None:
        board_form = QFormLayout()
        board_form.addRow("Mode", self.mode_combo)
        port_row = QHBoxLayout()
        port_row.addWidget(self.port_combo)
        port_row.addWidget(self.refresh_ports_button)
        board_form.addRow("Port", port_row)

        button_row = QHBoxLayout()
        button_row.addWidget(self.connect_button)
        button_row.addWidget(self.disconnect_button)

        board_group = QGroupBox("Board")
        board_layout = QVBoxLayout(board_group)
        board_layout.addLayout(board_form)
        board_layout.addLayout(button_row)
        board_layout.addWidget(self.marker_button)

        display_form = QFormLayout()
        display_form.addRow("Window (s)", self.window_spin)
        display_form.addRow("Refresh (ms)", self.refresh_spin)
        display_form.addRow("Scale (uV)", self.scale_spin)
        display_group = QGroupBox("Display")
        display_group.setLayout(display_form)

        processing_form = QFormLayout()
        processing_form.addRow("Bandpass Low", self.low_spin)
        processing_form.addRow("Bandpass High", self.high_spin)
        processing_form.addRow("Notch", self.notch_combo)
        processing_group = QGroupBox("Processing")
        processing_group.setLayout(processing_form)

        layout = QVBoxLayout(self)
        layout.addWidget(board_group)
        layout.addWidget(display_group)
        layout.addWidget(processing_group)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

    def _wire_signals(self) -> None:
        self.refresh_ports_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self._on_connect)
        self.disconnect_button.clicked.connect(self.disconnect_requested)
        self.marker_button.clicked.connect(self.marker_requested)
        for widget in (
            self.mode_combo,
            self.port_combo,
            self.window_spin,
            self.refresh_spin,
            self.scale_spin,
            self.low_spin,
            self.high_spin,
            self.notch_combo,
        ):
            if isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda _text: self._apply_to_settings())
            else:
                widget.valueChanged.connect(lambda _value: self._apply_to_settings())

    def refresh_ports(self) -> None:
        current = self.port_combo.currentText() if hasattr(self, "port_combo") else ""
        self.port_combo.clear()
        self.port_combo.addItems(list_serial_ports())
        if current:
            self.port_combo.setCurrentText(current)

    def set_connected(self, connected: bool) -> None:
        self.connect_button.setEnabled(not connected)
        self.disconnect_button.setEnabled(connected)
        self.marker_button.setEnabled(connected)
        self.mode_combo.setEnabled(not connected)
        self.port_combo.setEnabled(not connected)

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def _on_connect(self) -> None:
        self._apply_to_settings()
        self.connect_requested.emit()

    def _apply_to_settings(self) -> None:
        self.settings.board.mode = self.mode_combo.currentText()
        self.settings.board.serial_port = self.port_combo.currentText().strip()
        self.settings.display.window_seconds = self.window_spin.value()
        self.settings.display.refresh_ms = self.refresh_spin.value()
        self.settings.display.y_scale_uv = self.scale_spin.value()
        self.settings.processing.bandpass_low_hz = self.low_spin.value()
        self.settings.processing.bandpass_high_hz = self.high_spin.value()
        self.settings.processing.notch_hz = int(self.notch_combo.currentText())
        self.settings_changed.emit()
