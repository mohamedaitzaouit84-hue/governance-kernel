"""control/resource_governor.py — حدود الموارد لكل فرع."""
import json, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "audit"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))
import append_only_log as audit
import policy_store

KERNEL_DIR = Path(__file__).resolve().parent.parent
STATE = KERNEL_DIR / "control" / "resource_state.json"
WINDOW = 60.0


def _load():
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                     encoding="utf-8")


def _prune(events, now):
    return [t for t in events if now - t < WINDOW]


def limits():
    return policy_store.load().get("limits", {})


def consume(branch_id, resource, amount=1):
    cap = limits().get(f"{resource}_per_minute")
    if cap is None:
        return {"allowed": True, "reason": "no limit defined"}
    now = time.time()
    state = _load()
    bucket = state.setdefault(branch_id, {}).setdefault(resource, [])
    bucket[:] = _prune(bucket, now)
    if len(bucket) + amount > cap:
        audit.append("resource_limit_exceeded", {
            "branch_id": branch_id, "resource": resource,
            "cap": cap, "current": len(bucket), "requested": amount,
        })
        return {"allowed": False,
                "reason": f"limit {cap}/min exceeded for {resource}",
                "current": len(bucket), "cap": cap}
    bucket.extend([now] * amount)
    _save(state)
    return {"allowed": True, "current": len(bucket), "cap": cap}


def usage(branch_id=None):
    s = _load()
    return s if branch_id is None else s.get(branch_id, {})


def reset():
    if STATE.exists():
        STATE.unlink()
