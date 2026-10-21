#!/usr/bin/env python3
"""tools/make_commitment.py — produce an OP-1 external commitment.

Usage:
  python3 tools/make_commitment.py             # print to stdout
  python3 tools/make_commitment.py --append    # also append to
                                               # logs/commitments.jsonl

Output: one-line JSON commitment.

Signature: Ed25519 over the canonical JSON of all fields except
`sig`:
    json.dumps(obj_without_sig, sort_keys=True,
               separators=(",", ":"))
"""
import base64
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "seed"))
sys.path.insert(0, str(REPO / "audit"))
import root
import append_only_log as aol

from cryptography.hazmat.primitives import serialization


def _read_last(path):
    if not path.exists() or path.stat().st_size == 0:
        return None
    last = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last = json.loads(line)
    return last


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _public_key_b64():
    pub = serialization.load_pem_public_key(
        (REPO / "identity" / "owner_key.pub").read_bytes()
    )
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode("ascii")


def _last_commitment_hash():
    path = REPO / "logs" / "commitments.jsonl"
    if not path.exists() or path.stat().st_size == 0:
        return None
    last = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last = json.loads(line)
    if last is None:
        return None
    without_sig = {k: v for k, v in last.items() if k != "sig"}
    return hashlib.sha256(_canonical(without_sig).encode("utf-8")).hexdigest()


def main():
    append = "--append" in sys.argv

    last = _read_last(aol.LOG_PATH)
    if last is None:
        print("ERROR: no records in audit log", file=sys.stderr)
        return 1

    commitment = {
        "gk_cmt": 1,
        "prev": _last_commitment_hash(),
        "seq": last["seq"],
        "hash": last["hash"],
        "pk": _public_key_b64(),
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    canonical = _canonical(commitment).encode("utf-8")
    commitment["sig"] = root.sign(canonical).hex()

    line = json.dumps(commitment, sort_keys=True, separators=(",", ":"))

    if append:
        path = REPO / "logs" / "commitments.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
