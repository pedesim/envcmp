"""Tests for envcmp.masker."""

import pytest
from envcmp.masker import SecretMasker, MASK_PLACEHOLDER


@pytest.fixture()
def masker() -> SecretMasker:
    return SecretMasker()


# --- is_secret ---

def test_password_key_is_secret(masker):
    assert masker.is_secret("DB_PASSWORD") is True


def test_token_key_is_secret(masker):
    assert masker.is_secret("GITHUB_TOKEN") is True


def test_api_key_is_secret(masker):
    assert masker.is_secret("STRIPE_API_KEY") is True


def test_secret_key_is_secret(masker):
    assert masker.is_secret("APP_SECRET") is True


def test_plain_key_is_not_secret(masker):
    assert masker.is_secret("DEBUG") is False


def test_host_key_is_not_secret(masker):
    assert masker.is_secret("DB_HOST") is False


def test_matching_is_case_insensitive(masker):
    assert masker.is_secret("db_password") is True


# --- mask ---

def test_mask_replaces_secret_value(masker):
    assert masker.mask("DB_PASSWORD", "s3cr3t") == MASK_PLACEHOLDER


def test_mask_preserves_plain_value(masker):
    assert masker.mask("DEBUG", "true") == "true"


# --- mask_dict ---

def test_mask_dict_masks_secrets(masker):
    env = {"DB_PASSWORD": "hunter2", "DEBUG": "true", "API_KEY": "abc123"}
    result = masker.mask_dict(env)
    assert result["DB_PASSWORD"] == MASK_PLACEHOLDER
    assert result["API_KEY"] == MASK_PLACEHOLDER
    assert result["DEBUG"] == "true"


def test_mask_dict_returns_new_dict(masker):
    env = {"SECRET_KEY": "xyz"}
    result = masker.mask_dict(env)
    assert result is not env


# --- custom patterns ---

def test_custom_pattern_matches():
    masker = SecretMasker(patterns=[r".*INTERNAL.*"])
    assert masker.is_secret("MY_INTERNAL_VALUE") is True
    assert masker.is_secret("DB_PASSWORD") is False  # default patterns not included


def test_custom_placeholder():
    masker = SecretMasker(placeholder="<REDACTED>")
    assert masker.mask("DB_PASSWORD", "secret") == "<REDACTED>"
