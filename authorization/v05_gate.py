"""v05_gate.py — Permission gate for V0.5 agents.

Uses layered policy (P-Q11): signed base + v0.5_agents extension.
The V0.1-V0.4 PermissionGate is unchanged and still used by
governed_action.py for legacy subjects.

This gate is only used by V0.5 agents via governed_action_v05.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent
sys.path.insert(0, str(_here))
sys.path.insert(0, str(_repo / "policy"))
sys.path.insert(0, str(_repo / "audit"))

import policy_engine
import policy_extension
import append_only_log as audit


class V05PermissionGate:
    """Gate using base (signed) + v0.5_agents extension."""

    EXTENSION = "v0.5_agents.yaml"

    def __init__(self):
        merged = policy_extension.load_extended(self.EXTENSION)
        self.policy = merged
        self.engine = policy_engine.PolicyEngine(policy=merged)

    def check(self, request):
        """Evaluate a request. Logs decision to audit chain."""
        decision = self.engine.evaluate(request)
        audit.append("v05_gate_decision", {
            "subject": request.get("subject"),
            "action": request.get("action"),
            "decision": "allow" if decision.get("allow") else "deny",
            "reason": decision.get("reason"),
            "matched": decision.get("matched"),
            "role": decision.get("role"),
        })
        return decision


def reload():
    """Return a fresh gate (bypasses PolicyEngine internal cache)."""
    return V05PermissionGate()
