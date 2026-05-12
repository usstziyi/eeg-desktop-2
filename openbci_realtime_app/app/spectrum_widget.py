from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget


class SpectrumWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.plot = pg.PlotWidget()
        self.plot.setBackground("w")
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setLabel("bottom", "Frequency", units="Hz")
        self.plot.setLabel("left", "PSD")
        self.curve = self.plot.plot(pen=pg.mkPen("#1f77b4", width=1))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot)

    def update_data(self, freqs: np.ndarray, psd: np.ndarray) -> None:
        if freqs.size == 0 or psd.size == 0:
            return
        mean_psd = np.mean(psd, axis=0)
        self.curve.setData(freqs, mean_psd)
        self.plot.setXRange(0, min(60, float(freqs[-1])), padding=0)

