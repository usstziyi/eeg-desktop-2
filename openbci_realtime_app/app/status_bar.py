from __future__ import annotations

from PySide6.QtWidgets import QLabel

from openbci_realtime_app.acquisition.board_session import BoardInfo


class BoardStatusLabel(QLabel):
    def set_board_info(self, info: BoardInfo) -> None:
        self.setText(
            f"Board {info.board_id} | {info.sampling_rate} Hz | "
            f"{len(info.eeg_channels)} EEG channels"
        )

    def set_idle(self) -> None:
        self.setText("Disconnected")

