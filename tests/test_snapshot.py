"""Tests for envcmp.snapshot."""

import json
import os
import pytest

from envcmp.snapshot import Snapshot, save_snapshot, load_snapshot, snapshot_from_env_source


# ---------------------------------------------------------------------------
# Snapshot dataclass
# ---------------------------------------------------------------------------

def test_snapshot_repr_contains_label():
    s = Snapshot(label="prod", data={"A": "1"})
    assert "prod" in repr(s)


def test_snapshot_repr_contains_key_count():
    s = Snapshot(label="prod", data={"A": "1", "B": "2"})
    assert "2" in repr(s)


def test_to_dict_contains_all_fields():
    s = Snapshot(label="staging", data={"X": "y"}, source_path=".env")
    d = s.to_dict()
    assert d["label"] == "staging"
    assert d["data"] == {"X": "y"}
    assert d["source_path"] == ".env"
    assert "captured_at" in d


def test_from_dict_round_trips():
    original = Snapshot(label="dev", data={"K": "v"}, source_path=None)
    restored = Snapshot.from_dict(original.to_dict())
    assert restored.label == original.label
    assert restored.data == original.data
    assert restored.captured_at == original.captured_at


def test_from_dict_missing_source_path_defaults_none():
    raw = {"label": "x", "data": {}, "captured_at": "2024-01-01T00:00:00+00:00"}
    s = Snapshot.from_dict(raw)
    assert s.source_path is None


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_and_load_round_trip(tmp_path):
    snap = Snapshot(label="ci", data={"FOO": "bar", "PORT": "8080"})
    dest = str(tmp_path / "snapshots" / "ci.json")
    save_snapshot(snap, dest)
    assert os.path.exists(dest)
    loaded = load_snapshot(dest)
    assert loaded.label == snap.label
    assert loaded.data == snap.data


def test_saved_file_is_valid_json(tmp_path):
    snap = Snapshot(label="test", data={"A": "1"})
    dest = str(tmp_path / "snap.json")
    save_snapshot(snap, dest)
    with open(dest) as fh:
        parsed = json.load(fh)
    assert parsed["label"] == "test"


def test_load_nonexistent_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot(str(tmp_path / "missing.json"))


# ---------------------------------------------------------------------------
# snapshot_from_env_source
# ---------------------------------------------------------------------------

class _FakeSource:
    def __init__(self, label, data, path=None):
        self.label = label
        self.data = data
        self.path = path


def test_snapshot_from_env_source_copies_data():
    src = _FakeSource("local", {"DB": "sqlite"}, path=None)
    snap = snapshot_from_env_source(src)
    assert snap.label == "local"
    assert snap.data == {"DB": "sqlite"}


def test_snapshot_from_env_source_sets_path():
    src = _FakeSource("prod", {}, path="/etc/app/.env")
    snap = snapshot_from_env_source(src)
    assert snap.source_path == "/etc/app/.env"


def test_snapshot_from_env_source_no_path_is_none():
    src = _FakeSource("dev", {}, path=None)
    snap = snapshot_from_env_source(src)
    assert snap.source_path is None
