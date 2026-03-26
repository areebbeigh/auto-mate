"""Resolve Fernet-compatible secret key: env → ~/.auto-mate → generate and persist."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from cryptography.fernet import Fernet

ENV_KEYS = ("AUTO_MATE_SECRET_KEY", "SECRET_KEY")
DOTFILE_NAME = ".auto-mate"
FILE_ENTRY_PREFIX = "SECRET_KEY="


def _parse_secret_key_from_file(content: str) -> str | None:
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(FILE_ENTRY_PREFIX):
            value = line[len(FILE_ENTRY_PREFIX) :].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            if value:
                return value
    return None


def _persist_key_to_dotfile(path: Path, key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        existing = path.read_text(encoding="utf-8")
        if not existing.endswith("\n"):
            existing += "\n"
        path.write_text(existing + f"{FILE_ENTRY_PREFIX}{key}\n", encoding="utf-8")
    else:
        path.write_text(f"{FILE_ENTRY_PREFIX}{key}\n", encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def load_or_create_fernet_key() -> bytes:
    """Return Fernet key bytes (32-byte url-safe base64)."""
    for env_name in ENV_KEYS:
        raw = os.environ.get(env_name)
        if raw is not None and raw.strip():
            return raw.strip().encode("ascii")

    dotfile = Path.home() / DOTFILE_NAME
    if dotfile.is_file():
        try:
            text = dotfile.read_text(encoding="utf-8")
        except OSError:
            text = ""
        parsed = _parse_secret_key_from_file(text)
        if parsed:
            return parsed.encode("ascii")

    key = Fernet.generate_key().decode("ascii")
    _persist_key_to_dotfile(dotfile, key)
    return key.encode("ascii")
