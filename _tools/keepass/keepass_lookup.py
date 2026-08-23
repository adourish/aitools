#!/usr/bin/env python3
"""
keepass_lookup — read credentials out of the automation KeePass vault.

The vault (`automation-keys.kdbx`) is unlocked with a KEY FILE and no master
password, so agents and unattended scripts can read secrets without a prompt.

Vault discovery order (first hit wins):
    database  : $KEEPASS_DB
                ~/keys/automation-keys.kdbx
                C:\\keys\\automation-keys.kdbx
                G:\\My Drive\\Areas\\Keys\\automation-keys.kdbx
    key file  : $KEEPASS_KEY
                <same folder as the database>/automation-keys.keyfile
                ~/.keepass/automation-keys.keyfile
                C:\\keys\\automation-keys.keyfile

Usage:
    python keepass_lookup.py doctor
    python keepass_lookup.py list [--group DevOps] [--json]
    python keepass_lookup.py find jenkins
    python keepass_lookup.py get "DevOps/FDA Jira PAT (sde.fda.gov)" --field password
    python keepass_lookup.py get "Database/SERIO Oracle DB (oasis_er) Dev-Test" --json

As a library:
    from keepass_lookup import get_secret
    pat = get_secret("DevOps/FDA Jira PAT (sde.fda.gov)")

Rules:
  - `list` / `find` / `doctor` never print a secret value.
  - `get` prints exactly one field to stdout with no trailing decoration, so it
    is safe to capture:  TOKEN=$(python keepass_lookup.py get ... --field password)
  - Never echo the result into a log, a commit, or a task file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from pykeepass import PyKeePass
except ImportError:  # pragma: no cover - dependency guidance
    sys.stderr.write(
        "pykeepass is not installed. Run:  pip install -r "
        + str(Path(__file__).with_name("requirements.txt"))
        + "\n"
    )
    raise SystemExit(3)


DB_CANDIDATES = [
    os.environ.get("KEEPASS_DB"),
    str(Path.home() / "keys" / "automation-keys.kdbx"),
    r"C:\keys\automation-keys.kdbx",
    r"G:\My Drive\Areas\Keys\automation-keys.kdbx",
]

KEY_CANDIDATES = [
    os.environ.get("KEEPASS_KEY"),
    None,  # placeholder: <db folder>/automation-keys.keyfile, filled in below
    str(Path.home() / ".keepass" / "automation-keys.keyfile"),
    r"C:\keys\automation-keys.keyfile",
]

DEFAULT_FIELD = "password"
FIELDS = ("password", "username", "url", "notes", "title", "otp")


class VaultNotFoundError(RuntimeError):
    pass


class EntryNotFoundError(RuntimeError):
    pass


def find_db() -> Path:
    for candidate in DB_CANDIDATES:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise VaultNotFoundError(
        "No automation-keys.kdbx found. Set KEEPASS_DB or place the vault at "
        "~/keys/automation-keys.kdbx (Linux/macOS) or C:\\keys\\automation-keys.kdbx (Windows)."
    )


def find_keyfile(db: Path) -> Path:
    candidates = list(KEY_CANDIDATES)
    candidates[1] = str(db.with_name("automation-keys.keyfile"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise VaultNotFoundError(
        "No automation-keys.keyfile found. Set KEEPASS_KEY or put the key file next "
        "to the vault. The key file must never be committed or synced to a cloud drive."
    )


def open_vault(db: str | None = None, keyfile: str | None = None) -> PyKeePass:
    db_path = Path(db) if db else find_db()
    if not db_path.is_file():
        raise VaultNotFoundError(f"Vault not found: {db_path}")
    key_path = Path(keyfile) if keyfile else find_keyfile(db_path)
    if not key_path.is_file():
        raise VaultNotFoundError(f"Key file not found: {key_path}")
    return PyKeePass(str(db_path), keyfile=str(key_path))


def entry_path(entry) -> str:
    """'DevOps/FDA Jira PAT (sde.fda.gov)' — group path plus title."""
    return "/".join(p for p in entry.path if p)


def _match(entry, name: str) -> bool:
    name = name.strip().lower()
    return name in (entry_path(entry).lower(), (entry.title or "").lower())


def _sample(entries, limit: int = 10) -> str:
    shown = [entry_path(e) for e in entries[:limit]]
    extra = len(entries) - len(shown)
    if extra > 0:
        shown.append(f"... and {extra} more (narrow the search or use `list --group`)")
    return "\n  ".join(shown)


def find_entry(kp: PyKeePass, name: str):
    """Exact match on full path or title first, then a unique case-insensitive substring."""
    exact = [e for e in kp.entries if _match(e, name)]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise EntryNotFoundError(
            f"'{name}' matches {len(exact)} entries. Use the full path:\n  " + _sample(exact)
        )
    partial = [e for e in kp.entries if name.lower() in entry_path(e).lower()]
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        raise EntryNotFoundError(
            f"'{name}' is ambiguous — {len(partial)} entries match. Use the full path:\n  "
            + _sample(partial)
        )
    raise EntryNotFoundError(
        f"No vault entry matches '{name}'. Run `keepass_lookup.py list` to see the titles."
    )


def get_secret(name: str, field: str = DEFAULT_FIELD, db=None, keyfile=None) -> str:
    """Library entry point. Returns one field of one entry, or raises."""
    if field not in FIELDS:
        raise ValueError(f"field must be one of {FIELDS}, got {field!r}")
    entry = find_entry(open_vault(db, keyfile), name)
    if field == "otp":
        return entry.otp or ""
    return getattr(entry, field) or ""


def _redacted(entry) -> dict:
    return {
        "path": entry_path(entry),
        "title": entry.title or "",
        "username": entry.username or "",
        "url": entry.url or "",
        "has_password": bool(entry.password),
    }


def cmd_doctor(args) -> int:
    try:
        db = Path(args.db) if args.db else find_db()
        key = Path(args.keyfile) if args.keyfile else find_keyfile(db)
    except VaultNotFoundError as exc:
        print(f"FAIL  {exc}")
        return 2
    print(f"database  {db}")
    print(f"key file  {key}")
    try:
        kp = open_vault(str(db), str(key))
    except Exception as exc:  # noqa: BLE001 - surface the real reason
        print(f"FAIL      could not unlock: {type(exc).__name__}: {exc}")
        return 2
    groups = sorted({"/".join(g.path) or "(root)" for g in kp.groups})
    print(f"OK        unlocked with key file, no master password")
    print(f"entries   {len(kp.entries)}")
    print(f"groups    {', '.join(groups)}")
    return 0


def cmd_list(args) -> int:
    kp = open_vault(args.db, args.keyfile)
    entries = [e for e in kp.entries if e.title]
    if args.group:
        prefix = args.group.lower().rstrip("/") + "/"
        entries = [e for e in entries if entry_path(e).lower().startswith(prefix)]
    entries.sort(key=entry_path)
    if args.json:
        print(json.dumps([_redacted(e) for e in entries], indent=2))
        return 0
    for entry in entries:
        user = f"  [{entry.username}]" if entry.username else ""
        print(f"{entry_path(entry)}{user}")
    return 0


def cmd_find(args) -> int:
    kp = open_vault(args.db, args.keyfile)
    needle = args.query.lower()
    hits = [
        e
        for e in kp.entries
        if e.title
        and (
            needle in entry_path(e).lower()
            or needle in (e.username or "").lower()
            or needle in (e.url or "").lower()
        )
    ]
    hits.sort(key=entry_path)
    if args.json:
        print(json.dumps([_redacted(e) for e in hits], indent=2))
        return 0
    if not hits:
        print(f"no entry matches '{args.query}'")
        return 1
    for entry in hits:
        print(f"{entry_path(entry)}")
        if entry.username:
            print(f"    user  {entry.username}")
        if entry.url:
            print(f"    url   {entry.url}")
    return 0


def cmd_get(args) -> int:
    kp = open_vault(args.db, args.keyfile)
    entry = find_entry(kp, args.name)
    if args.json:
        # Deliberately includes the password — only use when you need the whole record.
        payload = _redacted(entry)
        payload["password"] = entry.password or ""
        payload["notes"] = entry.notes or ""
        print(json.dumps(payload, indent=2))
        return 0
    if args.field == "otp":
        value = entry.otp or ""
    else:
        value = getattr(entry, args.field) or ""
    if not value:
        sys.stderr.write(f"entry '{entry_path(entry)}' has no {args.field}\n")
        return 1
    sys.stdout.write(value + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="keepass_lookup",
        description="Read credentials from the automation KeePass vault (key file, no password).",
    )
    parser.add_argument("--db", help="override the vault path (else $KEEPASS_DB / discovery order)")
    parser.add_argument("--keyfile", help="override the key file path (else $KEEPASS_KEY / discovery order)")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="show which vault/key file is in use and unlock it")
    doctor.set_defaults(func=cmd_doctor)

    listing = sub.add_parser("list", help="list entry paths (never prints secrets)")
    listing.add_argument("--group", help="only entries under this group, e.g. DevOps")
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(func=cmd_list)

    finder = sub.add_parser("find", help="search titles, usernames and urls (never prints secrets)")
    finder.add_argument("query")
    finder.add_argument("--json", action="store_true")
    finder.set_defaults(func=cmd_find)

    getter = sub.add_parser("get", help="print one field of one entry")
    getter.add_argument("name", help="full path ('DevOps/FDA Jira PAT (sde.fda.gov)') or a unique title")
    getter.add_argument("--field", choices=FIELDS, default=DEFAULT_FIELD)
    getter.add_argument("--json", action="store_true", help="print the whole record, password included")
    getter.set_defaults(func=cmd_get)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (VaultNotFoundError, EntryNotFoundError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
