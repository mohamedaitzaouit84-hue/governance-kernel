#!/usr/bin/env python3
"""tools/verify_commitment.py — verify an OP-1 external commitment.

Usage:
  python3 tools/verify_commitment.py --commitment <path> \
      [--log <path>] [--prev <path>]

Checks:
  (a) Commitment parses; all required fields present.
  (b) gk_cmt == 1.
  (c) Ed25519 signature over canonical JSON (without sig)
      verifies against pk.
  (d) Log has at least seq+1 records.
  (e) Record at position seq has chain hash == commitment.hash.
  (f) Chain integrity from seq+1 to end.
  (g) If --prev provided: sha256 of prev canonical ==
      commitment.prev.

Exit codes:
  0 = all checks pass
  1 = any check fails
"""
import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _hash_record(seq, ts, prev_hash, kind, data):
    payload = json.dumps(
        {"seq": seq, "ts": ts, "prev_hash": prev_hash,
         "kind": kind, "data": data},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_log(path):
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def verify(commitment_path, log_path, prev_path=None):
    errors = []

    try:
        raw = Path(commitment_path).read_text(encoding="utf-8").strip()
        c = json.loads(raw)
    except Exception as e:
        return [f"(a) cannot parse commitment: {e}"]

    required = {"gk_cmt", "prev", "seq", "hash", "pk", "ts", "sig"}
    missing = required - set(c.keys())
    if missing:
        return [f"(a) missing fields: {sorted(missing)}"]

    if c["gk_cmt"] != 1:
        errors.append(f"(b) unexpected gk_cmt: {c['gk_cmt']}")

    try:
        pk_raw = base64.b64decode(c["pk"])
        pub = Ed25519PublicKey.from_public_bytes(pk_raw)
    except Exception as e:
        return [f"(c) bad pk: {e}"]

    without_sig = {k: v for k, v in c.items() if k != "sig"}
    canonical = _canonical(without_sig).encode("utf-8")
    try:
        sig_bytes = bytes.fromhex(c["sig"])
        pub.verify(sig_bytes, canonical)
    except Exception as e:
        errors.append(f"(c) signature does not verify: {e}")

    try:
        records = _read_log(log_path)
    except Exception as e:
        return [f"(d) cannot read log: {e}"]

    if not records:
        return ["(d) log is empty"]

    # (d) locate committed record by its seq field (not by index)
    target = None
    for r in records:
        if r.get("seq") == c["seq"]:
            target = r
            break
    if target is None:
        errors.append(
            f"(d) no record with seq={c['seq']} "
            f"(log has seq {records[0].get('seq')}.."
            f"{records[-1].get('seq')}, n={len(records)})"
        )
        return errors

    # (e)+(f) full chain from the first record
    expected_prev = records[0]["prev_hash"]
    expected_seq = records[0]["seq"]
    for r in records:
        if r["seq"] != expected_seq:
            errors.append(f"(f) seq gap/reorder at seq={r['seq']} "
                          f"(expected {expected_seq})")
            break
        if r["prev_hash"] != expected_prev:
            errors.append(f"(f) chain broken at seq={r['seq']}")
            break
        rc = _hash_record(r["seq"], r["ts"], r["prev_hash"],
                          r["kind"], r["data"])
        if rc != r["hash"]:
            errors.append(f"(f) record hash mismatch at seq={r['seq']}")
            break
        expected_prev = r["hash"]
        expected_seq += 1

    if target["hash"] != c["hash"]:
        errors.append(
            f"(e) chain hash at seq={c['seq']} mismatch: "
            f"log={target['hash'][:16]}.. commitment={c['hash'][:16]}.."
        )

    if prev_path:
        try:
            prev_c = json.loads(
                Path(prev_path).read_text(encoding="utf-8").strip()
            )
        except Exception as e:
            errors.append(f"(g) cannot parse prev: {e}")
        else:
            prev_wo = {k: v for k, v in prev_c.items() if k != "sig"}
            prev_h = hashlib.sha256(
                _canonical(prev_wo).encode("utf-8")
            ).hexdigest()
            if c["prev"] != prev_h:
                errors.append(
                    f"(g) prev mismatch: "
                    f"commitment.prev="
                    f"{(c['prev'][:16] + '..') if c['prev'] else 'null'} "
                    f"recomputed={prev_h[:16]}.."
                )

    return errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--commitment", required=True)
    p.add_argument("--log", default="logs/audit.jsonl")
    p.add_argument("--prev", default=None)
    args = p.parse_args()

    errs = verify(args.commitment, args.log, args.prev)
    if errs:
        print("VERIFY FAILED:")
        for e in errs:
            print("  " + e)
        return 1
    print("VERIFY OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
