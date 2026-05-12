from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget


class BandPowerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.plot = pg.PlotWidget()
        self.plot.setBackground("w")
        self.plot.setLabel("left", "Power")
        self.plot.showGrid(x=False, y=True, alpha=0.15)
        self.bar: pg.BarGraphItem | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot)

    def update_data(self, names: tuple[str, ...], band_powers: np.ndarray) -> None:
        if not names or band_powers.size == 0:
            return
        mean_power = np.mean(band_powers, axis=0)
        x = np.arange(len(names))
        if self.bar is not None:
            self.plot.removeItem(self.bar)
        self.bar = pg.BarGraphItem(x=x, height=mean_power, width=0.65, brush="#4c78a8")
        self.plot.addItem(self.bar)
        axis = self.plot.getAxis("bottom")
        axis.setTicks([[(int(i), name) for i, name in enumerate(names)]])

