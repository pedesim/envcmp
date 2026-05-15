"""Tests for envcmp.loader."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from envcmp.loader import EnvSource, load_from_env, load_from_file, load_from_string


# ---------------------------------------------------------------------------
# load_from_string
# ---------------------------------------------------------------------------

class TestLoadFromString:
    def test_basic_parse(self):
        src = load_from_string("FOO=bar\nBAZ=qux\n")
        assert src.data == {"FOO": "bar", "BAZ": "qux"}

    def test_default_label(self):
        src = load_from_string("X=1")
        assert src.label == "<string>"

    def test_custom_label(self):
        src = load_from_string("X=1", label="staging")
        assert src.label == "staging"

    def test_path_is_none(self):
        src = load_from_string("X=1")
        assert src.path is None

    def test_empty_string(self):
        src = load_from_string("")
        assert src.data == {}


# ---------------------------------------------------------------------------
# load_from_file
# ---------------------------------------------------------------------------

class TestLoadFromFile:
    def test_loads_file(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("APP_ENV=production\nDEBUG=false\n")
        src = load_from_file(env_file)
        assert src.data == {"APP_ENV": "production", "DEBUG": "false"}

    def test_default_label_is_filename(self, tmp_path: Path):
        env_file = tmp_path / "production.env"
        env_file.write_text("X=1")
        src = load_from_file(env_file)
        assert src.label == "production.env"

    def test_custom_label(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("X=1")
        src = load_from_file(env_file, label="prod")
        assert src.label == "prod"

    def test_path_stored(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("X=1")
        src = load_from_file(env_file)
        assert src.path == env_file.resolve()

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_from_file(tmp_path / "nonexistent.env")

    def test_directory_raises(self, tmp_path: Path):
        with pytest.raises(ValueError):
            load_from_file(tmp_path)

    def test_accepts_string_path(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("K=V")
        src = load_from_file(str(env_file))
        assert src.data == {"K": "V"}


# ---------------------------------------------------------------------------
# load_from_env
# ---------------------------------------------------------------------------

class TestLoadFromEnv:
    def test_loads_process_env(self, monkeypatch):
        monkeypatch.setenv("ENVCMP_TEST_VAR", "hello")
        src = load_from_env()
        assert src.data.get("ENVCMP_TEST_VAR") == "hello"

    def test_default_label(self):
        src = load_from_env()
        assert src.label == "<environment>"

    def test_prefix_filter(self, monkeypatch):
        monkeypatch.setenv("MYAPP_FOO", "1")
        monkeypatch.setenv("MYAPP_BAR", "2")
        monkeypatch.setenv("OTHER_KEY", "3")
        src = load_from_env(prefix="MYAPP_")
        assert "MYAPP_FOO" in src.data
        assert "MYAPP_BAR" in src.data
        assert "OTHER_KEY" not in src.data

    def test_path_is_none(self):
        src = load_from_env()
        assert src.path is None
