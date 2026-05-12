from __future__ import annotations

from openbci_realtime_app.config.settings import AppSettings, SettingsManager


def test_settings_round_trip(tmp_path) -> None:  # noqa: ANN001
    path = tmp_path / "settings.json"
    manager = SettingsManager(path)
    manager.settings.board.mode = "cyton"
    manager.settings.board.serial_port = "COM3"
    manager.save()

    loaded = SettingsManager(path).settings

    assert isinstance(loaded, AppSettings)
    assert loaded.board.mode == "cyton"
    assert loaded.board.serial_port == "COM3"

