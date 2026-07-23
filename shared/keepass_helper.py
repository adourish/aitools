"""
keepass_helper.py -- retrieve secrets from the automation KeePass vault.

Vault locations tried in order:
  1. KEEPASS_DB / KEEPASS_KEY env vars
  2. C:\\keys\\automation-keys.kdbx  +  C:\\keys\\automation-keys.keyfile   (FDA GFE laptop)
  3. G:\\My Drive\\Areas\\Keys\\automation-keys.kdbx  +
     C:\\Users\\adourish\\.keepass\\automation-keys.keyfile                 (REI laptop)

Requires keepassxc-cli on PATH.
"""

import os
import subprocess

_DB_CANDIDATES = [
    os.environ.get("KEEPASS_DB", ""),
    r"C:\keys\automation-keys.kdbx",
    r"G:\My Drive\Areas\Keys\automation-keys.kdbx",
]
_KEY_CANDIDATES = [
    os.environ.get("KEEPASS_KEY", ""),
    r"C:\keys\automation-keys.keyfile",
    r"C:\Users\adourish\.keepass\automation-keys.keyfile",
]


def _find_vault():
    for db, key in zip(_DB_CANDIDATES, _KEY_CANDIDATES):
        if db and key and os.path.isfile(db) and os.path.isfile(key):
            return db, key
    raise FileNotFoundError(
        "KeePass vault not found. Set KEEPASS_DB / KEEPASS_KEY env vars or "
        "ensure the vault exists at C:\\keys\\ or G:\\My Drive\\Areas\\Keys\\."
    )


def get_secret(entry: str, field: str = "Password") -> str:
    """Return the value of *field* from *entry* in the automation vault.

    Args:
        entry: Full KeePass path, e.g. "DevOps/FDA Jenkins API token (jenkins.fda.gov)".
        field: Field name -- "Password", "UserName", "URL", etc.

    Returns:
        The field value as a stripped string.

    Raises:
        FileNotFoundError: Vault or key file not found.
        RuntimeError:      keepassxc-cli returned a non-zero exit code.
    """
    db, key = _find_vault()
    result = subprocess.run(
        [
            "keepassxc-cli", "show",
            "--key-file", key,
            "--no-password",
            "--attributes", field,
            db,
            entry,
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"keepassxc-cli failed for entry '{entry}' field '{field}':\n"
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()