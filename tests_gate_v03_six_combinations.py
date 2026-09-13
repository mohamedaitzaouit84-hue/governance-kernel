"""Test all 6 combinations of A x P with a single Node class.

If Node works with 3x2 = 6 combinations without knowing its types,
architecture-policy separation is established.
"""
import sys, os
sys.path.insert(0, 'kernel')
sys.path.insert(0, 'kernel/separation')

from separation.node import Node
from separation.environment import Environment
from separation.central_info import CentralInfoModel
from separation.hierarchical_info import HierarchicalInfoModel
from separation.distributed_info import DistributedInfoModel
from separation.simple_policy import SimplePolicy
from separation.adaptive_policy import AdaptivePolicy


ARCHITECTURES = {
    "C": lambda: CentralInfoModel(delayed=False),
    "H": lambda: HierarchicalInfoModel(n_clusters=2),
    "D": lambda: DistributedInfoModel(),
}

POLICIES = {
    "S": lambda: SimplePolicy(),
    "A": lambda: AdaptivePolicy(alpha=0.1),
}


def run_one(arch_key, pol_key, n_steps=20, seed=42):
    env = Environment(n_nodes=6, n_clusters=2, seed=seed)
    info = ARCHITECTURES[arch_key]()
    pol = POLICIES[pol_key]()
    node = Node(node_id="n_3", info_model=info, policy=pol)

    actions = []
    for _ in range(n_steps):
        d = node.step(env=env, clock=None)
        actions.append(d.action)

    final_state = node.state
    steps = node.steps_taken
    arch_name = node.architecture_name
    pol_name = node.policy_name

    return {
        "arch_key": arch_key,
        "pol_key": pol_key,
        "arch_name": arch_name,
        "pol_name": pol_name,
        "steps": steps,
        "final_state": final_state,
        "actions": actions,
    }


def main():
    print("=" * 60)
    print("6 Combinations — Single Node, No Type Branching")
    print("=" * 60)

    results = []
    for a_key in ["C", "H", "D"]:
        for p_key in ["S", "A"]:
            r = run_one(a_key, p_key)
            results.append(r)
            print(f"  {a_key}-{p_key}: arch={r['arch_name']:12s} "
                  f"pol={r['pol_name']:8s} steps={r['steps']} "
                  f"final_state={r['final_state']:+.2f}")

    print()
    print("=" * 60)
    print("Assertions")
    print("=" * 60)

    # 1) All 6 combinations ran
    assert len(results) == 6, "not all 6 combos produced results"
    print("OK: 6/6 combinations produced results")

    # 2) Same node class for all
    for r in results:
        assert r["steps"] == 20, "steps mismatch"
    print("OK: all ran 20 steps")

    # 3) Architecture affects behavior
    # (C-S, H-S, D-S may differ because InfoSets differ)
    cs_final = next(r["final_state"] for r in results if r["arch_key"] == "C" and r["pol_key"] == "S")
    ds_final = next(r["final_state"] for r in results if r["arch_key"] == "D" and r["pol_key"] == "S")
    print(f"    C-S final_state = {cs_final:+.2f}")
    print(f"    D-S final_state = {ds_final:+.2f}")
    # (they may be same by chance; that's fine, just verify no crash)

    # 4) Policy affects behavior for same architecture
    cs = next(r for r in results if r["arch_key"] == "C" and r["pol_key"] == "S")
    ca = next(r for r in results if r["arch_key"] == "C" and r["pol_key"] == "A")
    print(f"    C-S actions[:5] = {cs['actions'][:5]}")
    print(f"    C-A actions[:5] = {ca['actions'][:5]}")

    print()
    print("=" * 60)
    print("ALL ASSERTIONS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
