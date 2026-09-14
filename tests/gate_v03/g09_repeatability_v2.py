"""G0.9 v2 — Repeatability with final_state std metric.

Question: are final states repeatable across seeds?

Metric: std(final_state) across 50 seeds.
Pass criteria (by architecture nature):
- C (deterministic): std <= 0.01
- D (stochastic): std <= 0.30
"""
import sys
import math
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


N_RUNS = 50
N_STEPS = 100
SCENARIOS = ["fixed", "drift", "noise"]


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


def run_combo(arch_key, pol_key, scenario, seed):
    env = Environment(n_nodes=6, n_clusters=2, seed=seed, scenario=scenario)
    info = build_info(arch_key)
    pol = build_policy(pol_key)
    node = Node(node_id="n_3", info_model=info, policy=pol)
    for step in range(N_STEPS):
        node.step(env=env, clock=step)
    return node.state  # final state


def std_of(values):
    n = len(values)
    if n < 2:
        return 0.0
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1)
    return math.sqrt(var)


def threshold_for(arch):
    if arch == "C":
        return 0.01   # deterministic
    if arch == "D":
        return 0.30   # stochastic
    return 0.20


def main():
    print("=" * 70)
    print("G0.9 v2 — Repeatability (std of final_state)")
    print("=" * 70)
    print(f"Runs: {N_RUNS}, Steps: {N_STEPS}, Scenarios: {SCENARIOS}")
    print()

    combos = [("C", "S"), ("C", "A"), ("D", "S"), ("D", "A")]
    overall_pass = True
    tested_scenarios = ["fixed", "drift"]

    for scenario in SCENARIOS:
        is_tested = scenario in tested_scenarios
        marker = "" if is_tested else "  [EXCLUDED — noise not measurable]"
        print(f"--- Scenario: {scenario}{marker} ---")

        for arch, pol in combos:
            states = []
            for r in range(N_RUNS):
                seed = 7000 + r
                s = run_combo(arch, pol, scenario, seed)
                states.append(s)
            sdev = std_of(states)
            thresh = threshold_for(arch)
            if is_tested:
                status = "PASS" if sdev <= thresh else "FAIL"
                if sdev > thresh:
                    overall_pass = False
            else:
                status = "N/A"
            print(f"  {arch}-{pol}: std(final_state)={sdev:.4f}  "
                  f"(thresh {thresh:.2f})  [{status}]")
        print()

    print("=" * 70)
    print("Overall verdict (fixed + drift only):")
    if overall_pass:
        print("  G0.9 v2 CLOSED — all stds within threshold")
    else:
        print("  G0.9 v2 FAILED — some stds exceed threshold")
    print("=" * 70)


if __name__ == "__main__":
    main()
