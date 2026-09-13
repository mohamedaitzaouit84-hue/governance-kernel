"""Smoke test: Node must not branch on architecture or policy type."""
import sys
sys.path.insert(0, 'kernel')

from separation.info_model import InfoModel, InformationSet
from separation.decision_policy import DecisionPolicy, Decision
from separation.node import Node


# --- Stub implementations for the smoke test only ---

class StubInfo(InfoModel):
    def __init__(self, value):
        self.value = value
    def gather(self, node, env, clock):
        return InformationSet(global_=self.value)
    @property
    def name(self):
        return "StubInfo"


class StubPolicy(DecisionPolicy):
    def __init__(self, sign):
        self.sign = sign
    def decide(self, info, current_state):
        obs = info.all_observations()
        total = sum(v for _, v in obs)
        action = self.sign * (1.0 if total >= 0 else -1.0)
        return Decision(action=action, confidence=0.5)
    def update_state(self, decision, info):
        return decision.action
    @property
    def name(self):
        return f"StubPolicy({self.sign:+d})"


def run():
    print("=== Test: Node with different Info but same Policy ===")
    for v in [0.5, -0.5]:
        node = Node(node_id=f"n_{v}", info_model=StubInfo(v),
                    policy=StubPolicy(+1))
        d = node.step(env=None, clock=None)
        print(f"  info={v:+.2f} -> action={d.action:+.1f}, state={node.state:+.1f}")

    print()
    print("=== Test: Node with same Info but different Policy ===")
    for s in [+1, -1]:
        node = Node(node_id=f"n_{s}", info_model=StubInfo(+0.5),
                    policy=StubPolicy(s))
        d = node.step(env=None, clock=None)
        print(f"  policy_sign={s:+d} -> action={d.action:+.1f}, state={node.state:+.1f}")

    print()
    print("=== Assertion: Node does NOT know its own types ===")
    n = Node(node_id="x", info_model=StubInfo(0.0), policy=StubPolicy(+1))
    forbidden = ['arch', 'architecture', 'policy_type', 'arch_type']
    attrs = dir(n)
    found = [f for f in forbidden if f in attrs]
    assert not found, f"Node exposes forbidden attributes: {found}"
    print("OK: Node has no architecture/policy type attributes")


if __name__ == "__main__":
    run()
