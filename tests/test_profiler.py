"""Tests for envcmp.profiler."""
import pytest

from envcmp.loader import EnvSource
from envcmp.masker import SecretMasker
from envcmp.profiler import ProfileReport, profile


def _source(data: dict, label: str = "test") -> EnvSource:
    src = EnvSource.__new__(EnvSource)
    src.label = label
    src.path = None
    src.data = data
    return src


@pytest.fixture()
def basic_source():
    return _source(
        {
            "APP_NAME": "myapp",
            "DB_PASSWORD": "s3cr3t",
            "API_KEY": "abc123",
            "DEBUG": "",
            "PORT": "8080",
        },
        label="staging",
    )


def test_profile_returns_profile_report(basic_source):
    result = profile(basic_source)
    assert isinstance(result, ProfileReport)


def test_total_keys(basic_source):
    result = profile(basic_source)
    assert result.total_keys == 5


def test_label_matches_source(basic_source):
    result = profile(basic_source)
    assert result.label == "staging"


def test_secret_keys_detected(basic_source):
    result = profile(basic_source)
    assert "DB_PASSWORD" in result.secret_keys
    assert "API_KEY" in result.secret_keys


def test_non_secret_not_in_secret_keys(basic_source):
    result = profile(basic_source)
    assert "APP_NAME" not in result.secret_keys
    assert "PORT" not in result.secret_keys


def test_empty_keys_detected(basic_source):
    result = profile(basic_source)
    assert "DEBUG" in result.empty_keys


def test_non_empty_not_in_empty_keys(basic_source):
    result = profile(basic_source)
    assert "APP_NAME" not in result.empty_keys


def test_no_duplicates_in_simple_source(basic_source):
    result = profile(basic_source)
    assert result.duplicate_keys == []


def test_key_lengths_populated(basic_source):
    result = profile(basic_source)
    assert result.key_lengths["APP_NAME"] == len("myapp")
    assert result.key_lengths["PORT"] == len("8080")


def test_empty_source_gives_zero_totals():
    src = _source({}, label="empty")
    result = profile(src)
    assert result.total_keys == 0
    assert result.secret_count == 0
    assert result.empty_count == 0


def test_summary_contains_label(basic_source):
    result = profile(basic_source)
    assert "staging" in result.summary()


def test_summary_contains_counts(basic_source):
    result = profile(basic_source)
    summary = result.summary()
    assert "Total keys" in summary
    assert "Secret keys" in summary
    assert "Empty keys" in summary


def test_custom_masker_respected():
    src = _source({"MY_CUSTOM_FIELD": "value", "NAME": "alice"})
    masker = SecretMasker(patterns=["custom"])
    result = profile(src, masker=masker)
    assert "MY_CUSTOM_FIELD" in result.secret_keys
    assert "NAME" not in result.secret_keys


def test_secret_count_property(basic_source):
    result = profile(basic_source)
    assert result.secret_count == len(result.secret_keys)


def test_empty_count_property(basic_source):
    result = profile(basic_source)
    assert result.empty_count == len(result.empty_keys)
