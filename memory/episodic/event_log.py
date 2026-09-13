"""memory/episodic/event_log.py — ذاكرة الأحداث.

كل حدث يُسجَّل مع:
- event_id (فريد)
- timestamp
- event_type
- data (المحتوى)
- context (السياق)
- hash (للسلامة)

الحد الأقصى: 10,000 حدث. عند التجاوز: حذف الأقدم.
"""
import json
import hashlib
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from collections import OrderedDict

_here = Path(__file__).resolve().parent
_memory = _here.parent
_kernel = _memory.parent

sys.path.insert(0, str(_memory))
sys.path.insert(0, str(_kernel / "audit"))

import gate
import append_only_log as audit

KERNEL_DIR = _kernel
EVENTS_PATH = KERNEL_DIR / "memory" / "data" / "events.jsonl"
INDEX_PATH = KERNEL_DIR / "memory" / "data" / "events_index.json"
MAX_EVENTS = 10000

# كاش في الذاكرة للأداء
_EVENTS = None
_INDEX = None


def _ensure_dirs():
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _compute_hash(event_id, ts, event_type, data, context):
    payload = json.dumps(
        {"id": event_id, "ts": ts, "type": event_type,
         "data": data, "context": context},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_all():
    global _EVENTS, _INDEX
    if _EVENTS is not None:
        return _EVENTS
    _EVENTS = []
    _INDEX = {}
    if not EVENTS_PATH.exists():
        return _EVENTS
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                _EVENTS.append(ev)
                _INDEX.setdefault(ev["type"], []).append(ev["id"])
            except json.JSONDecodeError:
                continue
    return _EVENTS


def _save_all():
    _ensure_dirs()
    with open(EVENTS_PATH, "w", encoding="utf-8") as f:
        for ev in _EVENTS:
            f.write(json.dumps(ev, ensure_ascii=False,
                               separators=(",", ":")) + "\n")
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(_INDEX, f, ensure_ascii=False, indent=2)


def _count():
    return len(_load_all())


def _enforce_limit():
    """يحذف الأقدم إذا تجاوز MAX_EVENTS."""
    events = _load_all()
    if len(events) <= MAX_EVENTS:
        return 0
    excess = len(events) - MAX_EVENTS
    removed = events[:excess]
    del events[:excess]
    for ev in removed:
        ids = _INDEX.get(ev["type"], [])
        if ev["id"] in ids:
            ids.remove(ev["id"])
    audit.append("memory_event_limit_enforced", {
        "removed": excess,
        "current": len(events),
        "max": MAX_EVENTS,
    })
    _save_all()
    return excess


def append(event_type, data=None, context=None,
           subject=None, role=None, trust=None):
    """إضافة حدث جديد. يمر عبر gate."""
    if not isinstance(event_type, str) or not event_type:
        raise ValueError("event_type must be non-empty string")
    if data is not None and not isinstance(data, dict):
        raise ValueError("data must be dict or None")
    if context is not None and not isinstance(context, dict):
        raise ValueError("context must be dict or None")

    # كل حدث يمر عبر بوابة الذاكرة
    gate.execute("memory:write", payload={"op": "event_append",
                                          "type": event_type},
                 subject=subject, role=role, trust=trust)

    event_id = "ev_" + uuid.uuid4().hex[:16]
    ts = _now()
    data = data or {}
    context = context or {}
    h = _compute_hash(event_id, ts, event_type, data, context)

    event = {
        "id": event_id,
        "ts": ts,
        "type": event_type,
        "data": data,
        "context": context,
        "hash": h,
    }

    _load_all()
    _EVENTS.append(event)
    _INDEX.setdefault(event_type, []).append(event_id)
    _ensure_dirs()

    with open(EVENTS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False,
                           separators=(",", ":")) + "\n")

    _enforce_limit()
    return event_id


def get(event_id):
    """استرجاع حدث بـ id."""
    gate.execute("memory:read", payload={"op": "event_get",
                                          "id": event_id})
    for ev in _load_all():
        if ev["id"] == event_id:
            return ev
    return None


def query(event_type=None, limit=None, since=None):
    """استرجاع أحداث بفلاتر."""
    gate.execute("memory:read", payload={"op": "event_query",
                                          "type": event_type})
    events = _load_all()
    result = events
    if event_type is not None:
        result = [e for e in result if e["type"] == event_type]
    if since is not None:
        result = [e for e in result if e["ts"] >= since]
    if limit is not None:
        result = result[-limit:]
    return list(result)


def verify_event(event):
    """يتحقق أن hash الحدث مطابق."""
    expected = _compute_hash(
        event["id"], event["ts"], event["type"],
        event["data"], event["context"],
    )
    return expected == event["hash"]


def verify_all():
    """يتحقق من سلامة كل الأحداث."""
    events = _load_all()
    bad = []
    for ev in events:
        if not verify_event(ev):
            bad.append(ev["id"])
    return {
        "total": len(events),
        "valid": len(events) - len(bad),
        "invalid": bad,
        "ok": len(bad) == 0,
    }


def stats():
    """إحصائيات الذاكرة العرضية."""
    events = _load_all()
    counts = {}
    for ev in events:
        counts[ev["type"]] = counts.get(ev["type"], 0) + 1
    return {
        "total": len(events),
        "max": MAX_EVENTS,
        "by_type": counts,
    }


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1 and _sys.argv[1] == "stats":
        print(json.dumps(stats(), indent=2, ensure_ascii=False))
    elif len(_sys.argv) > 1 and _sys.argv[1] == "verify":
        print(json.dumps(verify_all(), indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m memory.episodic.event_log [stats|verify]")
