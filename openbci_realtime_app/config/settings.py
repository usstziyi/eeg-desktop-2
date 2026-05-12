from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BoardSettings:
    mode: str = "synthetic"
    serial_port: str = ""
    timeout: int = 10


@dataclass
class DisplaySettings:
    window_seconds: int = 4
    refresh_ms: int = 50
    y_scale_uv: int = 100


@dataclass
class ProcessingSettings:
    bandpass_low_hz: float = 1.0
    bandpass_high_hz: float = 45.0
    notch_hz: int = 50
    psd_window_seconds: int = 4
    welch_overlap_ratio: float = 0.5


@dataclass
class RecordingSettings:
    enabled: bool = False
    directory: str = "recordings"


@dataclass
class AppSettings:
    board: BoardSettings = field(default_factory=BoardSettings)
    display: DisplaySettings = field(default_factory=DisplaySettings)
    processing: ProcessingSettings = field(default_factory=ProcessingSettings)
    recording: RecordingSettings = field(default_factory=RecordingSettings)


class SettingsManager:
    """Loads and saves user settings while keeping sane defaults for missing keys."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path.cwd() / "settings.json"
        self.settings = self.load()

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        data = json.loads(self.path.read_text(encoding="utf-8-sig"))
        return self._from_dict(data)

    def save(self, settings: AppSettings | None = None) -> None:
        settings = settings or self.settings
        self.path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _from_dict(data: dict[str, Any]) -> AppSettings:
        return AppSettings(
            board=BoardSettings(**data.get("board", {})),
            display=DisplaySettings(**data.get("display", {})),
            processing=ProcessingSettings(**data.get("processing", {})),
            recording=RecordingSettings(**data.get("recording", {})),
        )

