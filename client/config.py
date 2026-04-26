import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".postr_config.json"

def loadConfig() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    
def saveConfig(data: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

def clearConfig() -> None:
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink