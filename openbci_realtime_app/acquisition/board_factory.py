from __future__ import annotations

from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams

from openbci_realtime_app.config.settings import BoardSettings


def create_board(settings: BoardSettings) -> BoardShim:
    params = BrainFlowInputParams()
    params.timeout = settings.timeout

    if settings.mode == "synthetic":
        board_id = BoardIds.SYNTHETIC_BOARD.value
    elif settings.mode == "cyton":
        if not settings.serial_port.strip():
            raise ValueError("Cyton mode requires a serial port.")
        params.serial_port = settings.serial_port.strip()
        board_id = BoardIds.CYTON_BOARD.value
    else:
        raise ValueError(f"Unsupported board mode: {settings.mode}")

    return BoardShim(board_id, params)

