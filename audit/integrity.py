"""audit/integrity.py — التحقق من سلامة السجل."""
import json, hashlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "seed"))
import root

KERNEL_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = KERNEL_DIR / "logs" / "audit.jsonl"
CKPT_PATH = KERNEL_DIR / "logs" / "checkpoints.jsonl"


def _hash_record(seq, ts, prev_hash, kind, data):
    payload = json.dumps(
        {"seq": seq, "ts": ts, "prev_hash": prev_hash, "kind": kind, "data": data},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_chain(cutoff_seq=None):
    """V0.7.19 (J-0.8.50): signature-aware chain verification.

    Per-record states:
      STRICT_VALID      : "sig" present AND root.verify() passes
      STRICT_INVALID    : "sig" present AND root.verify() fails  -> FAIL
      STRICT_MISSING    : no "sig" AND (cutoff is None or seq > cutoff) -> FAIL
      LEGACY_UNVERIFIED : no "sig" AND seq <= cutoff_seq

    cutoff_seq=None means strict mode.
    """
    if not LOG_PATH.exists():
        return {"ok": False, "reason": "no log file"}
    records = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                return {"ok": False, "reason": f"JSON error line {i}: {e}"}
    if not records:
        return {"ok": False, "reason": "empty log"}

    strict_valid = 0
    legacy_unverified = 0
    expected_prev = "0" * 64

    for rec in records:
        if rec["prev_hash"] != expected_prev:
            return {"ok": False, "reason": f"chain broken at seq {rec['seq']}"}
        expected = _hash_record(rec["seq"], rec["ts"], rec["prev_hash"],
                                rec["kind"], rec["data"])
        if expected != rec["hash"]:
            return {"ok": False, "reason": f"hash mismatch at seq {rec['seq']}"}

        if "sig" in rec:
            msg = f"{rec['seq']}|{rec['hash']}".encode("utf-8")
            try:
                sig = bytes.fromhex(rec["sig"])
            except ValueError:
                return {"ok": False, "reason": f"bad sig hex at seq {rec['seq']}"}
            if not root.verify(msg, sig):
                return {"ok": False, "reason": f"sig invalid at seq {rec['seq']}"}
            strict_valid += 1
        else:
            if cutoff_seq is None or rec["seq"] > cutoff_seq:
                return {"ok": False,
                        "reason": f"missing sig at seq {rec['seq']} "
                                  f"(strict mode: cutoff_seq={cutoff_seq})"}
            legacy_unverified += 1

        expected_prev = rec["hash"]

    return {
        "ok": True,
        "n_records": len(records),
        "strict_valid": strict_valid,
        "legacy_unverified": legacy_unverified,
        "cutoff_seq": cutoff_seq,
        "head_hash": records[-1]["hash"],
    }


def verify_checkpoints():
    if not CKPT_PATH.exists():
        return {"ok": True, "n_checkpoints": 0}
    checkpoints = []
    with open(CKPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                checkpoints.append(json.loads(line))
    for ckpt in checkpoints:
        msg = f"{ckpt['seq']}|{ckpt['head_hash']}".encode("utf-8")
        try:
            sig = bytes.fromhex(ckpt["signature"])
        except ValueError:
            return {"ok": False, "reason": f"bad signature hex at seq {ckpt['seq']}"}
        if not root.verify(msg, sig):
            return {"ok": False, "reason": f"signature invalid at seq {ckpt['seq']}"}
    return {"ok": True, "n_checkpoints": len(checkpoints)}


def _load_cutoff():
    """Read cutoff_seq from logs/.audit_cutoff.json if present.

    V0.7.19 (J-0.8.50): records with seq <= cutoff_seq and no
    "sig" are LEGACY_UNVERIFIED. If missing, cutoff is None
    (strict mode).
    """
    cutoff_path = KERNEL_DIR / "logs" / ".audit_cutoff.json"
    if not cutoff_path.exists():
        return None
    try:
        data = json.loads(cutoff_path.read_text(encoding="utf-8"))
        return data.get("cutoff_seq")
    except (json.JSONDecodeError, OSError):
        return None


def full_verify():
    cutoff = _load_cutoff()
    chain = verify_chain(cutoff_seq=cutoff)
    if not chain.get("ok"):
        return {"ok": False, "chain": chain}
    ckpts = verify_checkpoints()
    if not ckpts.get("ok"):
        return {"ok": False, "checkpoints": ckpts}
    return {"ok": True, "chain": chain, "checkpoints": ckpts}


if __name__ == "__main__":
    result = full_verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)
