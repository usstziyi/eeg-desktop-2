from __future__ import annotations

import sys
from glob import glob


def list_serial_ports() -> list[str]:
    """Best-effort serial port discovery without adding a pyserial dependency."""

    if sys.platform.startswith("win"):
        return [f"COM{i}" for i in range(1, 257)]
    if sys.platform == "darwin":
        return sorted(glob("/dev/cu.*"))
    return sorted(glob("/dev/ttyUSB*") + glob("/dev/ttyACM*"))

