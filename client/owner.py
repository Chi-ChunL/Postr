import json
import os
from pathlib import Path


OWNER_PATHS = [
    Path.cwd() / "owner.json",
    Path.cwd() / ".owner.json",
    Path.cwd() / "postr_owner.json",
    Path.cwd() / ".postr_owner.json",
    Path.home() / ".postr_owner.json",
]


def loadAdminKey() -> str:
    env_key = os.getenv("POSTR_ADMIN_KEY", "").strip()
    if env_key:
        return env_key

    for path in OWNER_PATHS:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return str(data.get("admin_key", "")).strip()
            except Exception:
                return ""

    return ""


def hasAdminKey() -> bool:
    return loadAdminKey() != ""