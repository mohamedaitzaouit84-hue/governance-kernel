"""authorization/branch_registry.py — سجل الفروع. لا فرع يعمل دون تسجيل."""
import json, hashlib, sys, uuid
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "seed"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "audit"))
import root
import append_only_log as audit

KERNEL_DIR = Path.home() / "governance_kernel"
REGISTRY = KERNEL_DIR / "branches" / "registry.jsonl"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _read_all():
    if not REGISTRY.exists():
        return []
    out = []
    with open(REGISTRY, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def commitment(name, kind, requested_permissions):
    payload = json.dumps({
        "name": name, "kind": kind,
        "requested_permissions": sorted(set(requested_permissions)),
    }, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).digest()


def register(name, kind, requested_permissions, owner_signature_hex=None):
    if not name or not kind:
        return {"ok": False, "reason": "name and kind required"}
    if not isinstance(requested_permissions, list):
        return {"ok": False, "reason": "permissions must be list"}
    if owner_signature_hex is None:
        return {"ok": False, "reason": "owner signature required"}
    try:
        sig = bytes.fromhex(owner_signature_hex)
    except ValueError:
        return {"ok": False, "reason": "bad signature hex"}
    msg = commitment(name, kind, requested_permissions)
    if not root.verify(msg, sig):
        audit.append("branch_registration_refused",
                     {"name": name, "reason": "signature invalid"})
        return {"ok": False, "reason": "signature invalid"}
    branch_id = f"br_{uuid.uuid4().hex[:12]}"
    record = {
        "branch_id": branch_id,
        "name": name,
        "kind": kind,
        "requested_permissions": sorted(set(requested_permissions)),
        "created_at": _now(),
        "owner_signature": owner_signature_hex,
    }
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False,
                           separators=(",", ":")) + "\n")
    audit.append("branch_registered", {
        "branch_id": branch_id, "name": name, "kind": kind,
        "requested_permissions": record["requested_permissions"],
    })
    return {"ok": True, "branch_id": branch_id, "record": record}


def is_registered(branch_id):
    return any(r.get("branch_id") == branch_id for r in _read_all())


def list_branches():
    return _read_all()


def get(branch_id):
    for r in _read_all():
        if r.get("branch_id") == branch_id:
            return r
    return None
