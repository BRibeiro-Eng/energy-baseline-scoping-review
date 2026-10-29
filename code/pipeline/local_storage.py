"""Fail-closed validation for local production inputs on macOS."""

from __future__ import annotations

import hashlib
import stat
from pathlib import Path
from typing import Iterable


PROHIBITED_ROOTS = (
    Path("/Users/bernardoribeiro/Desktop"),
    Path("/Users/bernardoribeiro/Documents"),
    Path("/Users/bernardoribeiro/Library/Mobile Documents"),
)


class StorageValidationError(RuntimeError):
    """A required production path is unavailable or outside local storage."""


def _within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def is_prohibited(path: Path) -> bool:
    """Return whether a path resolves inside an iCloud-managed project root."""

    resolved = path.expanduser().resolve(strict=False)
    return any(_within(resolved, root) for root in PROHIBITED_ROOTS)


def is_dataless(path: Path) -> bool:
    """Return whether macOS has evicted the file contents."""

    return bool(path.stat().st_flags & stat.SF_DATALESS)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_required_paths(root: Path, required: Iterable[Path]) -> dict:
    """Validate and hash required files rooted in a local authoritative tree."""

    root = root.expanduser().resolve(strict=True)
    if is_prohibited(root):
        raise StorageValidationError(f"prohibited root: {root}")

    hashes = {}
    for supplied in required:
        resolved = Path(supplied).expanduser().resolve(strict=False)
        if is_prohibited(resolved):
            raise StorageValidationError(f"prohibited resolved path: {resolved}")
        if not resolved.is_file():
            raise StorageValidationError(f"missing or unreadable file: {resolved}")
        if not _within(resolved, root):
            raise StorageValidationError(f"path escapes root: {resolved}")
        if is_dataless(resolved):
            raise StorageValidationError(f"dataless file: {resolved}")
        hashes[str(resolved.relative_to(root))] = _sha256(resolved)

    return {"root": str(root), "files": hashes, "count": len(hashes)}
