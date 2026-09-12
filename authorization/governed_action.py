"""authorization/governed_action.py — نقطة الدخول الموحدة لكل فعل."""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here.parent / "control"))
sys.path.insert(0, str(_here.parent / "audit"))
sys.path.insert(0, str(_here))
import kill_switch
import permission_gate
import resource_governor
import append_only_log as audit


class ActionDenied(Exception):
    pass


def execute(subject, role, trust, branch_id, action,
            resource=None, amount=1, payload=None):
    if kill_switch.is_active():
        audit.append("action_denied", {
            "subject": subject, "action": action,
            "branch_id": branch_id, "reason": "kill switch active",
        })
        raise ActionDenied("kill switch active")
    gate = permission_gate.PermissionGate()
    decision = gate.check({
        "subject": subject, "role": role, "trust": trust, "action": action,
    })
    if not decision["allow"]:
        raise ActionDenied(decision.get("reason", "denied"))
    if resource is not None:
        r = resource_governor.consume(branch_id, resource, amount=amount)
        if not r["allowed"]:
            raise ActionDenied(r["reason"])
    audit.append("action_executed", {
        "subject": subject, "role": role, "branch_id": branch_id,
        "action": action, "resource": resource, "amount": amount,
        "payload_keys": list((payload or {}).keys()),
    })
    return {"ok": True, "action": action, "branch_id": branch_id}
