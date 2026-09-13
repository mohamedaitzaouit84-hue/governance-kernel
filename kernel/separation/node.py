"""Node — architecture-agnostic and policy-agnostic.

FREEZE_v0.3 rule: Node MUST NOT branch on architecture or policy type.
It receives two objects and orchestrates them via step().
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    node_id: str
    info_model: object       # InfoModel instance (not typed at runtime)
    policy: object           # DecisionPolicy instance
    state: float = 0.0
    last_decision: Optional[object] = None
    steps_taken: int = 0

    def step(self, env, clock):
        """One step of the node.

        1. Gather information via info_model (Architecture).
        2. Decide via policy (Policy).
        3. Update state via policy.
        """
        info = self.info_model.gather(self, env, clock)
        decision = self.policy.decide(info, self.state)
        self.last_decision = decision
        self.state = self.policy.update_state(decision, info)
        self.steps_taken += 1
        return decision

    @property
    def architecture_name(self) -> str:
        """For logs. Must NOT be used for branching anywhere."""
        return self.info_model.name

    @property
    def policy_name(self) -> str:
        """For logs. Must NOT be used for branching anywhere."""
        return self.policy.name
