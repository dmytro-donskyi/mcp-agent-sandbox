"""Directory sandbox containment preventing path traversal vulnerabilities (CWE-22)."""
from __future__ import annotations

import os
from pathlib import Path


class PathTraversalError(Exception):
    """Raised when an agent attempts to access files outside the authorized workspace boundary."""


class DirectorySandbox:
    """Confines all filesystem operations within an isolated project root."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def resolve_safe_path(self, target: str | Path) -> Path:
        """Resolves target relative to root. Raises PathTraversalError if outside root."""
        candidate = (self.root / target).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            raise PathTraversalError(
                f"Security Violation: Target path '{target}' escapes authorized boundary '{self.root}'"
            )
        return candidate

    def safe_read_text(self, rel_path: str) -> str:
        safe_p = self.resolve_safe_path(rel_path)
        if not safe_p.exists():
            raise FileNotFoundError(f"File not found within sandbox: {rel_path}")
        return safe_p.read_text(encoding="utf-8")

    def safe_write_text(self, rel_path: str, content: str) -> None:
        safe_p = self.resolve_safe_path(rel_path)
        safe_p.parent.mkdir(parents=True, exist_ok=True)
        safe_p.write_text(content, encoding="utf-8")
