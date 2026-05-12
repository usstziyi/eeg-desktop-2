from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


class CsvRecorder:
    """Small CSV recorder for processed windows; BrainFlow streamer can replace this later."""

    def __init__(self, output_path: Path, channel_names: list[str]) -> None:
        self.output_path = output_path
        self.channel_names = channel_names
        self.file = None
        self.writer: csv.writer | None = None

    def start(self) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.output_path.open("w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)
        self.writer.writerow(["sample_index", *self.channel_names])

    def write_window(self, eeg: np.ndarray, start_index: int = 0) -> None:
        if self.writer is None:
            raise RuntimeError("Recorder has not been started.")
        for offset, sample in enumerate(eeg.T):
            self.writer.writerow([start_index + offset, *sample.tolist()])

    def stop(self) -> None:
        if self.file is not None:
            self.file.close()
        self.file = None
        self.writer = None

