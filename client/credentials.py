import keyring

SERVICE_NAME = "postr-tui"

def savePassword(username:str, password: str) -> None:
    keyring.set_password(SERVICE_NAME, username, password)

def loadPassword(username: str) -> str | None:
    return keyring.get_password(SERVICE_NAME, username) or ""

def deletePassword(username: str) -> None:
    try:
        keyring.delete_password(SERVICE_NAME, username)
    except Exception:
        pass