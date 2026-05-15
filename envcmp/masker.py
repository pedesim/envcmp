"""Secret masking for sensitive .env values."""

import re
from typing import Collection

# Default patterns that indicate a key holds a secret value
DEFAULT_SECRET_PATTERNS: list[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE_KEY.*",
    r".*AUTH.*",
    r".*CREDENTIAL.*",
    r".*DSN.*",
]

MASK_PLACEHOLDER = "***"


class SecretMasker:
    """Masks values whose keys match known secret patterns."""

    def __init__(
        self,
        patterns: Collection[str] | None = None,
        placeholder: str = MASK_PLACEHOLDER,
    ) -> None:
        raw_patterns = patterns if patterns is not None else DEFAULT_SECRET_PATTERNS
        self._regexes = [re.compile(p, re.IGNORECASE) for p in raw_patterns]
        self.placeholder = placeholder

    def is_secret(self, key: str) -> bool:
        """Return True if *key* matches any secret pattern."""
        return any(rx.fullmatch(key) for rx in self._regexes)

    def mask(self, key: str, value: str) -> str:
        """Return the masked placeholder if *key* is a secret, else *value*."""
        return self.placeholder if self.is_secret(key) else value

    def mask_dict(self, env: dict[str, str]) -> dict[str, str]:
        """Return a new dict with secret values replaced by the placeholder."""
        return {k: self.mask(k, v) for k, v in env.items()}
