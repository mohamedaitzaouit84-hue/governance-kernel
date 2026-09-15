"""BaseAgent — governed deterministic agent (V0.5).

Rules:
- Every action goes through governed_action.execute.
- Trust dynamics: alpha=0.05 on success, beta=0.10 on failure.
- Trust bounds: [0.00, 0.85]. Never 1.0.
- Invariants are hard. Violation -> isolation + trust reset.

Patterns applied:
- P-L1 Dynamic Trust Score
- P-Q9 Base Invariants
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent
sys.path.insert(0, str(_repo / "authorization"))
sys.path.insert(0, str(_repo / "control"))
sys.path.insert(0, str(_repo / "audit"))

import governed_action
import kill_switch
import append_only_log as audit


# Trust dynamics constants (frozen in FREEZE_v0.5.md section 4)
TRUST_ALPHA = 0.05
TRUST_BETA = 0.10
TRUST_MIN = 0.00
TRUST_MAX = 0.85
TRUST_INITIAL = 0.10


class InvariantViolation(Exception):
    """Raised when an agent attempts an action that violates its invariants."""
    pass


class BaseAgent:
    """Deterministic governed agent.

    Subclasses must define:
        NAME (str)
        ROLE (str)
        CAPABILITIES (list of str)
        INVARIANTS (list of callables: fn(action, payload) -> str|None)
    """

    NAME = "BaseAgent"
    ROLE = "base"
    CAPABILITIES = []          # tier_1 (always active)
    TIER_2_CAPABILITIES = []   # unlocked at trust >= 0.30
    TIER_3_CAPABILITIES = []   # unlocked at trust >= 0.60
    INVARIANTS = []

    def __init__(self, branch_id):
        self.name = self.NAME
        self.role = self.ROLE
        self.branch_id = branch_id
        self.capabilities = list(self.CAPABILITIES)
        self.invariants = list(self.INVARIANTS)
        self.trust = TRUST_INITIAL
        self.isolated = False
        self.actions_executed = 0
        self.actions_denied = 0
        self.invariants_blocked = 0

    # --- Trust dynamics (P-L1) ---

    def _apply_trust_delta(self, delta):
        new = self.trust + delta
        if new < TRUST_MIN:
            new = TRUST_MIN
        if new > TRUST_MAX:
            new = TRUST_MAX
        old = self.trust
        self.trust = new
        audit.append("trust_update", {
            "agent": self.name,
            "old": round(old, 4),
            "new": round(new, 4),
            "delta": delta,
        })

    # --- Invariant enforcement (P-Q9) ---

    def _check_invariants(self, action, payload):
        """Returns None if all pass. Otherwise returns violation message."""
        for inv in self.invariants:
            result = inv(action, payload)
            if result is not None:
                return result
        return None

    def isolate(self, reason):
        """Isolate agent: mark isolated, reset trust to min, log it."""
        self.isolated = True
        old = self.trust
        self.trust = TRUST_MIN
        audit.append("agent_isolated", {
            "agent": self.name,
            "reason": reason,
            "trust_before": round(old, 4),
            "trust_after": TRUST_MIN,
        })

    # --- Governed action (P-L1 execution path) ---

    def act(self, action, resource=None, amount=1, payload=None):
        """Execute an action through the Governance Kernel.

        Returns dict on success. Raises ActionDenied / InvariantViolation.
        """
        if self.isolated:
            raise InvariantViolation(
                "agent {} is isolated".format(self.name)
            )

        # 1. Invariant pre-check
        violation = self._check_invariants(action, payload)
        if violation is not None:
            self.invariants_blocked += 1
            audit.append("invariant_blocked", {
                "agent": self.name,
                "action": action,
                "reason": violation,
            })
            self.isolate("invariant violation: " + violation)
            raise InvariantViolation(violation)

        # 2. Capability pre-check
        if action not in self.current_capabilities():
            self.actions_denied += 1
            audit.append("capability_denied", {
                "agent": self.name,
                "action": action,
                "capabilities": self.capabilities,
            })
            raise governed_action.ActionDenied(
                "action not in capabilities: " + action
            )

        # 3. Governed execution
        try:
            result = governed_action.execute(
                subject=self.name,
                role=self.role,
                trust=self.trust,
                branch_id=self.branch_id,
                action=action,
                resource=resource,
                amount=amount,
                payload=payload,
            )
        except governed_action.ActionDenied:
            self.actions_denied += 1
            self._apply_trust_delta(-TRUST_BETA)
            raise

        # 4. Success
        self.actions_executed += 1
        self._apply_trust_delta(TRUST_ALPHA)
        return result

    # --- Introspection ---

    def get_state(self):
        return {
            "name": self.name,
            "role": self.role,
            "branch_id": self.branch_id,
            "trust": round(self.trust, 4),
            "isolated": self.isolated,
            "actions_executed": self.actions_executed,
            "actions_denied": self.actions_denied,
            "invariants_blocked": self.invariants_blocked,
            "capabilities": self.current_capabilities(),
        }

    def current_capabilities(self):
        """Return capabilities active at the current trust level (P-Q8).

        This is the entry point for hypothesis H13 (Progressive Capability).
        Tier 1 is always active. Tier 2 unlocks at trust >= 0.30.
        Tier 3 unlocks at trust >= 0.60.
        """
        from . import trust_manager
        return trust_manager.unlocked_capabilities(
            self.CAPABILITIES,
            self.TIER_2_CAPABILITIES,
            self.TIER_3_CAPABILITIES,
            self.trust,
        )
