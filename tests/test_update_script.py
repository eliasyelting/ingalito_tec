import subprocess

import pytest

from scripts.actualizar_catalogo import run_scraper


def test_scraper_error_is_propagated_without_silent_success(monkeypatch, tmp_path):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0])

    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        run_scraper(tmp_path / "raw.json")