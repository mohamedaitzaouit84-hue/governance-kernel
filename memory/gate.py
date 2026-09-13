"""memory/gate.py — البوابة الإلزامية لكل عملية ذاكرة.

كل استدعاء داخل memory يمر من هنا.
لا استدعاء مباشر بين مكونات memory من الخارج.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_kernel = _here.parent

sys.path.insert(0, str(_kernel / "seed"))
sys.path.insert(0, str(_kernel / "audit"))
sys.path.insert(0, str(_kernel / "authorization"))
sys.path.insert(0, str(_kernel / "control"))
sys.path.insert(0, str(_kernel / "policy"))

import kill_switch
import governed_action
import append_only_log as audit
import branch_registry as br

MEMORY_BRANCH_NAME = "memory"
_MEMORY_BRANCH_ID = None

# Whitelist — بوابة الذاكرة تقبل فقط هذه الأفعال.
# أي شيء آخر يُرفض، حتى لو كان الدور يملكه عالمياً.
ALLOWED_ACTIONS = frozenset({
    "memory:read",
    "memory:write",
    "memory:graph_traverse",
    "memory:trail_reinforce",
    "memory:swarm_query",
})


def _resolve_branch_id():
    """يبحث عن branch_id لفرع الذاكرة من السجل."""
    global _MEMORY_BRANCH_ID
    if _MEMORY_BRANCH_ID is not None:
        return _MEMORY_BRANCH_ID
    branches = br.list_branches()
    for b in branches:
        if b.get("name") == MEMORY_BRANCH_NAME:
            _MEMORY_BRANCH_ID = b["branch_id"]
            return _MEMORY_BRANCH_ID
    raise RuntimeError(
        f"فرع '{MEMORY_BRANCH_NAME}' غير مسجّل. "
        f"شغّل: python memory/register_branch.py"
    )


def branch_id():
    return _resolve_branch_id()


class MemoryGateError(Exception):
    """خطأ بوابة الذاكرة."""
    pass


def _pre_check(action, resource=None, amount=1, subject=None, role=None, trust=None):
    """فحص قبل التنفيذ — يعيد dict الاستدعاء."""
    if action not in ALLOWED_ACTIONS:
        audit.append("memory_gate_denied", {
            "action": action,
            "reason": f"not in memory whitelist",
        })
        raise MemoryGateError(
            f"action '{action}' غير مسموح داخل بوابة الذاكرة"
        )

    if kill_switch.is_active():
        audit.append("memory_gate_denied", {
            "action": action,
            "reason": "kill switch active",
        })
        raise MemoryGateError("kill switch active")

    bid = _resolve_branch_id()

    subj = subject or "memory_system"
    rol = role or "agent_high"
    trs = trust if trust is not None else 0.9

    return {
        "subject": subj,
        "role": rol,
        "trust": trs,
        "branch_id": bid,
        "action": action,
        "resource": resource,
        "amount": amount,
    }


def execute(action, payload=None, resource=None, amount=1,
            subject=None, role=None, trust=None):
    """تنفيذ عملية ذاكرة عبر البوابة الإلزامية.

    action: مثل "memory:read", "memory:write", "memory:graph_traverse"
    payload: dict بيانات العملية (تُسجَّل مفاتيحها فقط)
    resource: المورد لـ resource_governor (مثلاً "memory_ops")
    """
    call = _pre_check(action, resource=resource, amount=amount,
                      subject=subject, role=role, trust=trust)
    try:
        result = governed_action.execute(
            subject=call["subject"],
            role=call["role"],
            trust=call["trust"],
            branch_id=call["branch_id"],
            action=call["action"],
            resource=call["resource"],
            amount=call["amount"],
            payload=payload,
        )
        return result
    except governed_action.ActionDenied as e:
        audit.append("memory_gate_denied", {
            "action": action,
            "reason": str(e),
            "branch_id": call["branch_id"],
        })
        raise MemoryGateError(str(e)) from e


def status():
    """حالة بوابة الذاكرة."""
    active = kill_switch.is_active()
    try:
        bid = _resolve_branch_id()
        registered = True
    except RuntimeError:
        bid = None
        registered = False
    return {
        "kill_switch_active": active,
        "branch_registered": registered,
        "branch_id": bid,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2, ensure_ascii=False))
