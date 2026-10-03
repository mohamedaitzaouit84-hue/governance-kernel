"""control/kill_switch.py — إيقاف فوري لكل النظام."""
import os, sys, json
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "seed"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "audit"))
import root
import append_only_log as audit

KERNEL_DIR = Path(__file__).resolve().parent.parent


def _resolve_path(env_key, default):
    """V0.7.19 (J-0.8.61): allow env to redirect the control dir.

    GK_CONTROL_DIR -> control/ (kill.flag)

    Testing convenience, not a security feature.
    """
    v = os.environ.get(env_key)
    return Path(v) if v else default


FLAG = _resolve_path("GK_CONTROL_DIR", KERNEL_DIR / "control") / "kill.flag"


class KillSwitchActive(Exception):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat()


def trigger(reason, by="system"):
    FLAG.parent.mkdir(parents=True, exist_ok=True)
    if FLAG.exists():
        return False
    payload = {"triggered_at": _now(), "reason": reason, "by": by}
    FLAG.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    audit.append("kill_switch_triggered", payload)
    return True


def clear(signature_hex, message):
    if not FLAG.exists():
        return False
    try:
        sig = bytes.fromhex(signature_hex)
    except ValueError:
        return False
    if not root.verify(message.encode("utf-8"), sig):
        audit.append("kill_switch_clear_attempt",
                     {"success": False, "reason": "bad signature"})
        return False
    FLAG.unlink()
    audit.append("kill_switch_cleared", {"message": message})
    return True


def is_active():
    return FLAG.exists()


def status():
    if not is_active():
        return {"active": False}
    return {"active": True, "payload": json.loads(FLAG.read_text(encoding="utf-8"))}


def check():
    if is_active():
        raise KillSwitchActive("Kill switch ACTIVE — all operations halted.")
