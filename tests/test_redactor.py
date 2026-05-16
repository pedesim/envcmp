"""Tests for envcmp.redactor."""
from __future__ import annotations

import pytest

from envcmp.masker import SecretMasker
from envcmp.redactor import Redactor, RedactResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def redactor() -> Redactor:
    return Redactor()


@pytest.fixture()
def mixed_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "SECRET_TOKEN": "tok_xyz",
    }


# ---------------------------------------------------------------------------
# RedactResult
# ---------------------------------------------------------------------------

def test_redact_result_redacted_count():
    result = RedactResult(data={}, redacted_keys=["A", "B"])
    assert result.redacted_count == 2


def test_redact_result_empty():
    result = RedactResult(data={})
    assert result.redacted_count == 0


# ---------------------------------------------------------------------------
# Redactor.redact
# ---------------------------------------------------------------------------

def test_secret_keys_are_masked(redactor, mixed_env):
    result = redactor.redact(mixed_env)
    assert result.data["DB_PASSWORD"] == SecretMasker.MASK
    assert result.data["API_KEY"] == SecretMasker.MASK
    assert result.data["SECRET_TOKEN"] == SecretMasker.MASK


def test_non_secret_keys_are_unchanged(redactor, mixed_env):
    result = redactor.redact(mixed_env)
    assert result.data["APP_NAME"] == "myapp"
    assert result.data["DEBUG"] == "true"


def test_redacted_keys_list_is_sorted(redactor, mixed_env):
    result = redactor.redact(mixed_env)
    assert result.redacted_keys == sorted(result.redacted_keys)


def test_redacted_keys_contains_expected(redactor, mixed_env):
    result = redactor.redact(mixed_env)
    assert "DB_PASSWORD" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys
    assert "SECRET_TOKEN" in result.redacted_keys


def test_non_secret_keys_not_in_redacted_list(redactor, mixed_env):
    result = redactor.redact(mixed_env)
    assert "APP_NAME" not in result.redacted_keys
    assert "DEBUG" not in result.redacted_keys


def test_original_dict_not_mutated(redactor, mixed_env):
    original_password = mixed_env["DB_PASSWORD"]
    redactor.redact(mixed_env)
    assert mixed_env["DB_PASSWORD"] == original_password


def test_empty_env_returns_empty_result(redactor):
    result = redactor.redact({})
    assert result.data == {}
    assert result.redacted_keys == []


def test_all_plain_keys_nothing_redacted(redactor):
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redactor.redact(env)
    assert result.redacted_count == 0
    assert result.data == env


# ---------------------------------------------------------------------------
# Redactor.redact_to_dict
# ---------------------------------------------------------------------------

def test_redact_to_dict_returns_dict(redactor, mixed_env):
    out = redactor.redact_to_dict(mixed_env)
    assert isinstance(out, dict)


def test_redact_to_dict_masks_secrets(redactor, mixed_env):
    out = redactor.redact_to_dict(mixed_env)
    assert out["DB_PASSWORD"] == SecretMasker.MASK


# ---------------------------------------------------------------------------
# Custom masker
# ---------------------------------------------------------------------------

def test_custom_masker_is_used():
    custom = SecretMasker(secret_patterns=["CUSTOM"])
    r = Redactor(masker=custom)
    env = {"CUSTOM_VALUE": "hidden", "NORMAL": "visible"}
    result = r.redact(env)
    assert result.data["CUSTOM_VALUE"] == SecretMasker.MASK
    assert result.data["NORMAL"] == "visible"
