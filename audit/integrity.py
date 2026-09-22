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


def verify_chain():
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
    expected_prev = "0" * 64
    for rec in records:
        if rec["prev_hash"] != expected_prev:
            return {"ok": False, "reason": f"chain broken at seq {rec['seq']}"}
        expected = _hash_record(rec["seq"], rec["ts"], rec["prev_hash"],
                                rec["kind"], rec["data"])
        if expected != rec["hash"]:
            return {"ok": False, "reason": f"hash mismatch at seq {rec['seq']}"}
        expected_prev = rec["hash"]
    return {"ok": True, "n_records": len(records), "head_hash": records[-1]["hash"]}


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


def full_verify():
    chain = verify_chain()
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
