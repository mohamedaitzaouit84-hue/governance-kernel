"""audit/append_only_log.py — سجل hash-chained قابل للإضافة فقط."""
import json, hashlib, sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "seed"))
import root

KERNEL_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = KERNEL_DIR / "logs" / "audit.jsonl"
CKPT_PATH = KERNEL_DIR / "logs" / "checkpoints.jsonl"
GENESIS_HASH = "0" * 64
CHECKPOINT_EVERY = 50


def _now():
    return datetime.now(timezone.utc).isoformat()


def _hash_record(seq, ts, prev_hash, kind, data):
    payload = json.dumps(
        {"seq": seq, "ts": ts, "prev_hash": prev_hash, "kind": kind, "data": data},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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


def _write_record(rec):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")


def _maybe_checkpoint(rec):
    if rec["seq"] % CHECKPOINT_EVERY != 0:
        return
    msg = f"{rec['seq']}|{rec['hash']}".encode("utf-8")
    sig_hex = root.sign(msg).hex()
    ckpt = {"seq": rec["seq"], "head_hash": rec["hash"],
            "signature": sig_hex, "ts": _now()}
    with open(CKPT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ckpt, ensure_ascii=False, separators=(",", ":")) + "\n")


def open_log():
    last = _read_last()
    if last is None:
        ts = _now()
        data = {"kernel_version": "0.1.0", "note": "genesis audit record"}
        h = _hash_record(0, ts, GENESIS_HASH, "genesis", data)
        rec = {"seq": 0, "ts": ts, "prev_hash": GENESIS_HASH,
               "kind": "genesis", "data": data, "hash": h}
        _write_record(rec)
        return rec
    return last


def append(kind, data):
    if not LOG_PATH.exists():
        open_log()
    last = _read_last()
    seq = last["seq"] + 1
    prev_hash = last["hash"]
    ts = _now()
    h = _hash_record(seq, ts, prev_hash, kind, data)
    rec = {"seq": seq, "ts": ts, "prev_hash": prev_hash,
           "kind": kind, "data": data, "hash": h}
    _write_record(rec)
    _maybe_checkpoint(rec)
    return rec


def read_all():
    if not LOG_PATH.exists():
        return []
    out = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out
