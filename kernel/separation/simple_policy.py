"""SimplePolicy — S: majority vote with fixed weights."""
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)

from decision_policy import DecisionPolicy, Decision


class SimplePolicy(DecisionPolicy):
    """Fixed weights. No learning. No history."""

    def decide(self, info, current_state):
        obs = info.all_observations()
        if not obs:
            return Decision(action=0.0, confidence=1.0)
        total = sum(v for _, v in obs)
        action = 1.0 if total >= 0 else -1.0
        return Decision(action=action, confidence=1.0)

    def update_state(self, decision, info):
        return decision.action

    @property
    def name(self):
        return "Simple"
