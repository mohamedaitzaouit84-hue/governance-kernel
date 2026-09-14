"""G0.9 v3 — Same-seed repeatability.

Correct definition of repeatability:
- For each (combo, scenario, seed): run TWICE with the SAME seed.
- If both runs give identical final_state → that triple is repeatable.
- Overall: fraction of repeatable triples.

Threshold: 100% (perfection required — code is deterministic per seed).
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_kernel = _here.parent.parent

sys.path.insert(0, str(_kernel / "kernel"))
sys.path.insert(0, str(_kernel / "kernel" / "separation"))

from separation.node import Node
from separation.environment import Environment
from separation.central_info import CentralInfoModel
from separation.distributed_info import DistributedInfoModel
from separation.simple_policy import SimplePolicy
from separation.adaptive_policy import AdaptivePolicy


N_SEEDS = 20       # number of distinct seeds
N_STEPS = 100
SCENARIOS = ["fixed", "drift", "noise"]
EPS = 1e-9


def build_info(arch_key):
    if arch_key == "C":
        return CentralInfoModel()
    if arch_key == "D":
        return DistributedInfoModel()
    raise ValueError(arch_key)


def build_policy(pol_key):
    if pol_key == "S":
        return SimplePolicy()
    if pol_key == "A":
        return AdaptivePolicy(alpha=0.1)
    raise ValueError(pol_key)


def run_once(arch_key, pol_key, scenario, seed):
    env = Environment(n_nodes=6, n_clusters=2, seed=seed, scenario=scenario)
    info = build_info(arch_key)
    pol = build_policy(pol_key)
    node = Node(node_id="n_3", info_model=info, policy=pol)
    for step in range(N_STEPS):
        node.step(env=env, clock=step)
    return node.state


def main():
    print("=" * 70)
    print("G0.9 v3 — Same-seed Repeatability")
    print("=" * 70)
    print(f"Seeds: {N_SEEDS}, Steps: {N_STEPS}, Scenarios: {SCENARIOS}")
    print()

    combos = [("C", "S"), ("C", "A"), ("D", "S"), ("D", "A")]
    overall_pass = True

    for scenario in SCENARIOS:
        print(f"--- Scenario: {scenario} ---")
        for arch, pol in combos:
            matches = 0
            for i in range(N_SEEDS):
                seed = 9000 + i
                s1 = run_once(arch, pol, scenario, seed)
                s2 = run_once(arch, pol, scenario, seed)  # SAME seed
                if abs(s1 - s2) < EPS:
                    matches += 1
            rate = matches / N_SEEDS
            status = "PASS" if rate == 1.0 else "FAIL"
            if status == "FAIL":
                overall_pass = False
            print(f"  {arch}-{pol}: repeatability = {rate:.2f} ({matches}/{N_SEEDS})  [{status}]")
        print()

    print("=" * 70)
    print("Overall verdict:")
    if overall_pass:
        print("  G0.9 v3 CLOSED — 100% same-seed repeatability across all combos")
    else:
        print("  G0.9 v3 FAILED — some combos are not repeatable")
    print("=" * 70)


if __name__ == "__main__":
    main()
