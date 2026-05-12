from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from openbci_realtime_app.app.main_window import MainWindow
from openbci_realtime_app.config.settings import SettingsManager


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    app.setApplicationName("OpenBCI Realtime EEG")

    settings_manager = SettingsManager()
    window = MainWindow(settings_manager)
    window.resize(1400, 850)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

