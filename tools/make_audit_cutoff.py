"""tools/make_audit_cutoff.py — create logs/.audit_cutoff.json.

One-time migration script (V0.7.19, Sprint 1.5).

Purpose: mark the boundary between legacy unsigned records
and strict signed records for the audit log. Records with
seq <= cutoff_seq and no "sig" are accepted as
LEGACY_UNVERIFIED by verify_chain().

This script must be run MANUALLY and ONCE per repo. It is
NOT called by bootstrap.py, because the decision "this is
the cutoff" is a conscious security choice, not an
automatic one.

The cutoff file is signed by the owner key:
  signature = Ed25519 over f"{cutoff_seq}|{cutoff_hash}"

Usage:
  python3 tools/make_audit_cutoff.py          # interactive
  python3 tools/make_audit_cutoff.py --yes    # non-interactive
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "seed"))
import root

LOG_PATH = REPO / "logs" / "audit.jsonl"
CUTOFF_PATH = REPO / "logs" / ".audit_cutoff.json"


def _read_last():
    if not LOG_PATH.exists() or LOG_PATH.stat().st_size == 0:
        return None
    last = None
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last = json.loads(line)
    return last


def main():
    if CUTOFF_PATH.exists():
        print(f"  [STOP] {CUTOFF_PATH} already exists.")
        print(f"         Delete it manually if you really want to")
        print(f"         recreate the cutoff.")
        return 1

    last = _read_last()
    if last is None:
        print("  [STOP] No audit log or empty log. Nothing to mark.")
        print("         Run bootstrap.py and some activity first.")
        return 1

    seq = last["seq"]
    hash_hex = last["hash"]

    print(f"  Current audit log head:")
    print(f"    seq  = {seq}")
    print(f"    hash = {hash_hex}")
    print()
    print(f"  Records 0..{seq} will be LEGACY_UNVERIFIED.")
    print(f"  Records >{seq} must be signed (strict).")
    print()

    if "--yes" not in sys.argv:
        ans = input("  Proceed? [y/N] ").strip().lower()
        if ans != "y":
            print("  Aborted.")
            return 1

    msg = f"{seq}|{hash_hex}".encode("utf-8")
    sig_hex = root.sign(msg).hex()

    cutoff = {
        "cutoff_seq": seq,
        "cutoff_hash": hash_hex,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "signature": sig_hex,
    }
    CUTOFF_PATH.write_text(
        json.dumps(cutoff, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  [OK] Wrote {CUTOFF_PATH}")
    print(f"  [OK] cutoff_seq = {seq}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
