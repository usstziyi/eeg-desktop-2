from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget


class EegPlotWidget(QWidget):
    def __init__(self, channel_count: int = 8, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.channel_count = channel_count
        self.plot = pg.PlotWidget()
        self.plot.setBackground("w")
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setLabel("bottom", "Time", units="s")
        self.plot.setLabel("left", "EEG", units="uV")
        self.plot.setClipToView(True)
        self.plot.setDownsampling(auto=True, mode="peak")
        self.curves = [
            self.plot.plot(pen=pg.mkPen(pg.intColor(i, hues=channel_count), width=1))
            for i in range(channel_count)
        ]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot)

    def update_data(self, time_axis: np.ndarray, eeg: np.ndarray, scale_uv: float) -> None:
        if eeg.size == 0:
            return
        channels = min(self.channel_count, eeg.shape[0])
        offsets = np.arange(channels, dtype=float)[:, None] * scale_uv * 2.5
        centered = eeg[:channels] - np.mean(eeg[:channels], axis=1, keepdims=True)
        stacked = centered + offsets
        for index in range(channels):
            self.curves[index].setData(time_axis, stacked[index])
        self.plot.setYRange(-scale_uv, max(1, channels) * scale_uv * 2.5)

