"""AdaptivePolicy — A: weighted vote with dynamic weights.

w_ij(t+1) = f(w_ij(t), e_j(t))
Here: simple multiplicative update with pre-defined alpha.
NO architecture awareness. NO environment awareness.
"""
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)

from decision_policy import DecisionPolicy, Decision


class AdaptivePolicy(DecisionPolicy):
    def __init__(self, alpha=0.1):
        self.alpha = alpha
        self.weights = {}         # source -> weight
        self.errors = {}          # source -> last error

    def decide(self, info, current_state):
        obs = info.all_observations()
        if not obs:
            return Decision(action=0.0, confidence=1.0)

        weighted_sum = 0.0
        for source, value in obs:
            w = self.weights.get(source, 1.0)
            weighted_sum += w * value

        action = 1.0 if weighted_sum >= 0 else -1.0
        conf = min(1.0, abs(weighted_sum) / max(1, len(obs)))
        # remember for update_state
        self._last_obs = obs
        return Decision(action=action, confidence=conf)

    def update_state(self, decision, info):
        obs = info.all_observations()
        for source, value in obs:
            pred_sign = 1.0 if value >= 0 else -1.0
            err = 0.0 if pred_sign == decision.action else 1.0
            w = self.weights.get(source, 1.0)
            # if agent agreed with majority, strengthen; else weaken
            self.weights[source] = w + self.alpha * (1.0 - 2.0 * err)
            self.weights[source] = max(0.1, min(2.0, self.weights[source]))
            self.errors[source] = err
        return decision.action

    @property
    def name(self):
        return "Adaptive"
