"""Watch .env files for changes and emit diff events."""

from __future__ import annotations

import time
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional

from envcmp.loader import load_from_file
from envcmp.pipeline import PipelineConfig, PipelineResult, run


@dataclass
class WatchEvent:
    """Emitted when a watched file changes."""

    path: Path
    result: PipelineResult
    timestamp: float = field(default_factory=time.time)

    def __repr__(self) -> str:  # pragma: no cover
        return f"WatchEvent(path={self.path}, changed={len(self.result.diff.changed)})"


def _file_hash(path: Path) -> str:
    """Return MD5 hex digest of *path* contents."""
    return hashlib.md5(path.read_bytes()).hexdigest()


class Watcher:
    """Poll one or more .env files and call *callback* when a diff is detected."""

    def __init__(
        self,
        paths: list[Path],
        callback: Callable[[WatchEvent], None],
        config: Optional[PipelineConfig] = None,
        interval: float = 2.0,
    ) -> None:
        if len(paths) < 2:
            raise ValueError("At least two paths are required to watch for diffs.")
        self.paths = [Path(p) for p in paths]
        self.callback = callback
        self.config = config or PipelineConfig()
        self.interval = interval
        self._hashes: Dict[str, str] = {}
        self._running = False

    def _current_hashes(self) -> Dict[str, str]:
        return {str(p): _file_hash(p) for p in self.paths if p.exists()}

    def _has_changed(self, new_hashes: Dict[str, str]) -> bool:
        return new_hashes != self._hashes

    def _emit(self) -> None:
        sources = [load_from_file(p) for p in self.paths]
        result = run(sources[0], sources[1], config=self.config)
        event = WatchEvent(path=self.paths[0], result=result)
        self.callback(event)

    def poll_once(self) -> bool:
        """Check for changes once. Returns True if a change was detected."""
        new_hashes = self._current_hashes()
        if self._has_changed(new_hashes):
            self._hashes = new_hashes
            self._emit()
            return True
        return False

    def start(self, max_iterations: Optional[int] = None) -> None:  # pragma: no cover
        """Block and poll indefinitely (or up to *max_iterations* cycles)."""
        self._running = True
        self._hashes = self._current_hashes()
        iterations = 0
        while self._running:
            time.sleep(self.interval)
            self.poll_once()
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break

    def stop(self) -> None:  # pragma: no cover
        self._running = False
