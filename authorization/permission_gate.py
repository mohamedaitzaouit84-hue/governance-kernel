"""authorization/permission_gate.py — البوابة الإلزامية."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "audit"))
import policy_engine
import append_only_log as audit


class PermissionGate:
    def __init__(self):
        self.engine = policy_engine.PolicyEngine()

    def check(self, request):
        decision = self.engine.evaluate(request)
        audit_record = {
            "subject": request.get("subject"),
            "role": request.get("role"),
            "trust": request.get("trust"),
            "action": request.get("action"),
            "decision": "allow" if decision["allow"] else "deny",
            "reason": decision.get("reason"),
        }
        audit.append("gate_decision", audit_record)
        return decision

    def reload_policy(self):
        import policy_store
        self.engine = policy_engine.PolicyEngine(policy_store.load())


if __name__ == "__main__":
    gate = PermissionGate()
    tests = [
        {"subject": "owner", "role": "owner", "trust": 1.0, "action": "tool:python"},
        {"subject": "low_1", "role": "agent_low", "trust": 0.3, "action": "tool:python"},
        {"subject": "high_1", "role": "agent_high", "trust": 0.9, "action": "tool:python"},
        {"subject": "mid_1", "role": "agent_mid", "trust": 0.6, "action": "tool:python"},
        {"subject": "unknown_1", "role": "ghost", "trust": 1.0, "action": "tool:python"},
        {"subject": "high_2", "role": "agent_high", "trust": 0.3, "action": "tool:file_read"},
    ]
    for t in tests:
        d = gate.check(t)
        print(f"{t['subject']:12s} | {t['action']:18s} | "
              f"{'ALLOW' if d['allow'] else 'DENY ':5s} | {d.get('reason')}")
