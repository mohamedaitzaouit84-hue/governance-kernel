"""governed_action_v05.py — governed action for V0.5 agents.

Same contract as authorization/governed_action.py:execute() but
uses V05PermissionGate (layered policy P-Q11) instead of the
legacy PermissionGate.

The legacy module stays untouched.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent
sys.path.insert(0, str(_repo / "authorization"))
sys.path.insert(0, str(_repo / "control"))
sys.path.insert(0, str(_repo / "audit"))

import kill_switch
import v05_gate
import resource_governor
import append_only_log as audit


class ActionDenied(Exception):
    """Raised when the V0.5 gate denies an action."""
    pass


# --- Gate singleton (built once, reused) ---
_GATE = None


def _get_gate():
    global _GATE
    if _GATE is None:
        _GATE = v05_gate.V05PermissionGate()
    return _GATE


def execute(subject, role, trust, branch_id, action,
            resource=None, amount=1, payload=None):
    """Execute an action via the layered V0.5 gate.

    Order:
      1. Kill Switch
      2. V05PermissionGate (base + v0.5_agents)
      3. Resource Governor (if resource given)
      4. Audit log entry on success
    """
    # 1. Kill Switch
    if kill_switch.is_active():
        audit.append("action_denied_v05", {
            "subject": subject,
            "action": action,
            "branch_id": branch_id,
            "reason": "kill switch active",
        })
        raise ActionDenied("kill switch active")

    # 2. Layered permission gate
    decision = _get_gate().check({
        "subject": subject,
        "role": role,
        "trust": trust,
        "branch_id": branch_id,
        "action": action,
    })
    if not decision.get("allow"):
        raise ActionDenied(decision.get("reason", "denied"))

    # 3. Resource governor
    if resource is not None:
        r = resource_governor.consume(branch_id, resource, amount=amount)
        if not r.get("allowed"):
            raise ActionDenied(r.get("reason", "resource denied"))

    # 4. Success
    audit.append("action_executed_v05", {
        "subject": subject,
        "role": role,
        "branch_id": branch_id,
        "action": action,
        "resource": resource,
        "amount": amount,
        "payload_keys": list((payload or {}).keys()),
    })
    return {"ok": True, "action": action, "branch_id": branch_id}
