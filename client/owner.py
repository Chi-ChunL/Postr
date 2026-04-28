import json
from pathlib import Path

OWNER_PATHS = [
    Path("owner.json"),
    Path(".owner.json"),
    Path.home() / ".postr_owner.json",
]

def loadAdminKey() -> str:
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