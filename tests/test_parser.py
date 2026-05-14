"""Tests for envcmp.parser module."""

import textwrap
from pathlib import Path

import pytest

from envcmp.parser import parse_env_file, parse_env_string


# ---------------------------------------------------------------------------
# parse_env_string
# ---------------------------------------------------------------------------

class TestParseEnvString:
    def test_simple_key_value(self):
        result = parse_env_string("FOO=bar")
        assert result == {"FOO": "bar"}

    def test_multiple_keys(self):
        text = textwrap.dedent("""
            APP_ENV=production
            DB_HOST=localhost
            DB_PORT=5432
        """)
        result = parse_env_string(text)
        assert result == {
            "APP_ENV": "production",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
        }

    def test_double_quoted_value(self):
        result = parse_env_string('SECRET="my secret value"')
        assert result["SECRET"] == "my secret value"

    def test_single_quoted_value(self):
        result = parse_env_string("SECRET='my secret value'")
        assert result["SECRET"] == "my secret value"

    def test_empty_value(self):
        result = parse_env_string("EMPTY=")
        assert result["EMPTY"] == ""

    def test_comment_lines_skipped(self):
        text = textwrap.dedent("""
            # This is a comment
            FOO=bar
            # Another comment
            BAZ=qux
        """)
        result = parse_env_string(text)
        assert "FOO" in result
        assert "BAZ" in result
        assert len(result) == 2

    def test_blank_lines_skipped(self):
        result = parse_env_string("\n\nFOO=bar\n\n")
        assert result == {"FOO": "bar"}

    def test_value_with_equals_sign(self):
        result = parse_env_string("TOKEN=abc=def=ghi")
        # Only the first '=' is the delimiter; rest is part of value
        assert result["TOKEN"] == "abc=def=ghi"

    def test_invalid_line_raises(self):
        with pytest.raises(ValueError, match="Invalid syntax"):
            parse_env_string("THIS IS NOT VALID")

    def test_spaces_around_equals(self):
        result = parse_env_string("FOO = bar")
        assert result["FOO"] == "bar"


# ---------------------------------------------------------------------------
# parse_env_file
# ---------------------------------------------------------------------------

class TestParseEnvFile:
    def test_reads_file_correctly(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("APP=test\nDEBUG=true\n", encoding="utf-8")
        result = parse_env_file(env_file)
        assert result == {"APP": "test", "DEBUG": "true"}

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            parse_env_file(tmp_path / "nonexistent.env")

    def test_accepts_string_path(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("KEY=value\n", encoding="utf-8")
        result = parse_env_file(str(env_file))
        assert result["KEY"] == "value"
