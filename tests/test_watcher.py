"""Tests for envcmp.watcher."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envcmp.watcher import Watcher, WatchEvent, _file_hash
from envcmp.pipeline import PipelineConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_watcher(tmp_path: Path, callback=None):
    a = tmp_path / ".env.a"
    b = tmp_path / ".env.b"
    a.write_text("KEY=value\n")
    b.write_text("KEY=value\n")
    cb = callback or (lambda e: None)
    return Watcher([a, b], callback=cb), a, b


# ---------------------------------------------------------------------------
# _file_hash
# ---------------------------------------------------------------------------

def test_file_hash_returns_string(tmp_path):
    f = tmp_path / "x.env"
    f.write_text("A=1")
    assert isinstance(_file_hash(f), str)


def test_file_hash_changes_when_content_changes(tmp_path):
    f = tmp_path / "x.env"
    f.write_text("A=1")
    h1 = _file_hash(f)
    f.write_text("A=2")
    h2 = _file_hash(f)
    assert h1 != h2


def test_file_hash_stable_for_same_content(tmp_path):
    f = tmp_path / "x.env"
    f.write_text("A=1")
    assert _file_hash(f) == _file_hash(f)


# ---------------------------------------------------------------------------
# Watcher construction
# ---------------------------------------------------------------------------

def test_requires_at_least_two_paths(tmp_path):
    a = tmp_path / ".env"
    a.write_text("A=1")
    with pytest.raises(ValueError, match="At least two"):
        Watcher([a], callback=lambda e: None)


def test_watcher_stores_paths(tmp_path):
    watcher, a, b = _make_watcher(tmp_path)
    assert len(watcher.paths) == 2


def test_default_config_is_pipeline_config(tmp_path):
    watcher, _, _ = _make_watcher(tmp_path)
    assert isinstance(watcher.config, PipelineConfig)


def test_custom_config_stored(tmp_path):
    cfg = PipelineConfig(include_unchanged=True)
    watcher, a, b = _make_watcher(tmp_path)
    watcher.config = cfg
    assert watcher.config.include_unchanged is True


# ---------------------------------------------------------------------------
# poll_once
# ---------------------------------------------------------------------------

def test_poll_once_no_change_returns_false(tmp_path):
    watcher, a, b = _make_watcher(tmp_path)
    # seed hashes
    watcher._hashes = watcher._current_hashes()
    assert watcher.poll_once() is False


def test_poll_once_detects_change(tmp_path):
    events = []
    watcher, a, b = _make_watcher(tmp_path, callback=events.append)
    watcher._hashes = watcher._current_hashes()
    b.write_text("KEY=changed\n")
    result = watcher.poll_once()
    assert result is True
    assert len(events) == 1


def test_poll_once_emits_watch_event(tmp_path):
    events = []
    watcher, a, b = _make_watcher(tmp_path, callback=events.append)
    watcher._hashes = watcher._current_hashes()
    b.write_text("KEY=new_value\n")
    watcher.poll_once()
    assert isinstance(events[0], WatchEvent)


def test_watch_event_has_pipeline_result(tmp_path):
    events = []
    watcher, a, b = _make_watcher(tmp_path, callback=events.append)
    watcher._hashes = watcher._current_hashes()
    b.write_text("KEY=new_value\n")
    watcher.poll_once()
    from envcmp.pipeline import PipelineResult
    assert isinstance(events[0].result, PipelineResult)


def test_watch_event_timestamp_is_recent(tmp_path):
    events = []
    watcher, a, b = _make_watcher(tmp_path, callback=events.append)
    watcher._hashes = watcher._current_hashes()
    b.write_text("KEY=new_value\n")
    before = time.time()
    watcher.poll_once()
    after = time.time()
    assert before <= events[0].timestamp <= after


def test_no_callback_on_second_poll_without_change(tmp_path):
    events = []
    watcher, a, b = _make_watcher(tmp_path, callback=events.append)
    watcher._hashes = watcher._current_hashes()
    b.write_text("KEY=changed\n")
    watcher.poll_once()
    watcher.poll_once()  # no further change
    assert len(events) == 1
