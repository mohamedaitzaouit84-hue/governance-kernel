"""policy/policy_engine.py — تقييم الطلبات مقابل السياسة."""
import fnmatch, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "authorization"))
import policy_store
import subject_registry


class PolicyEngine:
    def __init__(self, policy=None):
        self.policy = policy if policy is not None else policy_store.load()

    def _match(self, action, patterns):
        for p in patterns:
            if p == "*":
                return True
            if fnmatch.fnmatch(action, p):
                return True
        return False

    def evaluate(self, request):
        subject_id = request.get("subject")
        action = request.get("action", "")
        roles = self.policy.get("roles", {})

        # V0.4.1: ignore any role/trust in the request.
        # Look them up from the trusted registry.
        entry = subject_registry.lookup(subject_id)
        if entry is None:
            return {"allow": False,
                    "reason": f"unregistered subject: {subject_id}",
                    "matched": None}

        role_name = entry["role"]
        trust = entry["trust"]

        if role_name not in roles:
            return {"allow": False, "reason": f"unknown role: {role_name}",
                    "matched": None}

        role = roles[role_name]
        if trust < role.get("trust_min", 0.0):
            return {"allow": False,
                    "reason": f"trust {trust:.2f} < min {role['trust_min']}",
                    "matched": None}

        if self._match(action, role.get("permissions", [])):
            return {"allow": True, "reason": "matched",
                    "matched": action, "role": role_name}

        if self.policy.get("default_decision") == "allow":
            return {"allow": True, "reason": "default allow", "matched": None}
        return {"allow": False, "reason": f"denied: {action}",
                "matched": None, "role": role_name}
