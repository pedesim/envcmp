"""Tests for envcmp.differ module."""

import pytest
from envcmp.differ import DiffStatus, diff_envs


ENV_A = {
    "APP_ENV": "production",
    "DB_HOST": "db.prod.example.com",
    "DB_PORT": "5432",
    "SECRET_KEY": "supersecret",
}

ENV_B = {
    "APP_ENV": "staging",
    "DB_HOST": "db.prod.example.com",
    "DB_PORT": "5432",
    "NEW_FEATURE_FLAG": "true",
}


def test_changed_key():
    result = diff_envs(ENV_A, ENV_B)
    changed_keys = {e.key for e in result.changed}
    assert "APP_ENV" in changed_keys


def test_removed_key():
    result = diff_envs(ENV_A, ENV_B)
    removed_keys = {e.key for e in result.removed}
    assert "SECRET_KEY" in removed_keys


def test_added_key():
    result = diff_envs(ENV_A, ENV_B)
    added_keys = {e.key for e in result.added}
    assert "NEW_FEATURE_FLAG" in added_keys


def test_unchanged_excluded_by_default():
    result = diff_envs(ENV_A, ENV_B)
    assert result.unchanged == []


def test_unchanged_included_when_requested():
    result = diff_envs(ENV_A, ENV_B, include_unchanged=True)
    unchanged_keys = {e.key for e in result.unchanged}
    assert "DB_HOST" in unchanged_keys
    assert "DB_PORT" in unchanged_keys


def test_has_differences_true():
    result = diff_envs(ENV_A, ENV_B)
    assert result.has_differences is True


def test_has_differences_false():
    result = diff_envs(ENV_A, ENV_A)
    assert result.has_differences is False


def test_identical_envs_no_entries_by_default():
    result = diff_envs(ENV_A, ENV_A)
    assert result.entries == []


def test_empty_envs():
    result = diff_envs({}, {})
    assert result.entries == []
    assert result.has_differences is False


def test_diff_entry_repr_added():
    result = diff_envs({}, {"FOO": "bar"})
    assert repr(result.added[0]) == "[+] FOO=bar"


def test_diff_entry_repr_removed():
    result = diff_envs({"FOO": "bar"}, {})
    assert repr(result.removed[0]) == "[-] FOO=bar"


def test_diff_entry_repr_changed():
    result = diff_envs({"FOO": "old"}, {"FOO": "new"})
    assert repr(result.changed[0]) == "[~] FOO: 'old' -> 'new'"


def test_keys_sorted_in_result():
    env_a = {"ZEBRA": "1", "ALPHA": "2"}
    env_b = {"ZEBRA": "1", "ALPHA": "3"}
    result = diff_envs(env_a, env_b)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
