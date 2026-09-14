"""G0.9 — Statistical Repeatability.

Question: Are results stable across different random seeds?

Method:
- For each (arch, pol, scenario): run 50 times with seeds 1..50.
- Per run: extract the dominant sign of the action sequence.
- Agreement Rate = fraction of runs sharing the majority sign.
- Pass: agreement_rate >= 0.90 in non-trivial scenarios.
"""
import sys
from collections import Counter
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


def dominant_sign(actions):
    """Return the majority sign of the action sequence."""
    pos = sum(1 for a in actions if a > 0)
    neg = sum(1 for a in actions if a < 0)
    if pos > neg:
        return "+"
    elif neg > pos:
        return "-"
    else:
        return "="


def run_combo(arch_key, pol_key, scenario, seed):
    env = Environment(n_nodes=6, n_clusters=2, seed=seed, scenario=scenario)
    info = build_info(arch_key)
    pol = build_policy(pol_key)
    node = Node(node_id="n_3", info_model=info, policy=pol)
    actions = []
    for step in range(N_STEPS):
        d = node.step(env=env, clock=step)
        actions.append(d.action)
    return actions


def agreement_rate(signs):
    """Fraction of runs sharing the majority sign (excluding '=' ties)."""
    non_ties = [s for s in signs if s != "="]
    if not non_ties:
        return 1.0, "=", 0
    counts = Counter(non_ties)
    majority = counts.most_common(1)[0][0]
    rate = counts[majority] / len(signs)
    return rate, majority, len(non_ties)


def main():
    print("=" * 70)
    print("G0.9 — Statistical Repeatability")
    print("=" * 70)
    print(f"Runs: {N_RUNS}, Steps: {N_STEPS}, Scenarios: {SCENARIOS}")
    print()

    combos = [("C", "S"), ("C", "A"), ("D", "S"), ("D", "A")]

    overall_pass = True
    for scenario in SCENARIOS:
        print(f"--- Scenario: {scenario} ---")
        for arch, pol in combos:
            signs = []
            for r in range(N_RUNS):
                seed = 5000 + r  # different seed family from G0.7
                actions = run_combo(arch, pol, scenario, seed)
                signs.append(dominant_sign(actions))
            rate, maj, n_nonties = agreement_rate(signs)
            status = "PASS" if rate >= 0.90 else "FAIL"
            print(f"  {arch}-{pol}: agreement = {rate:.2f}  "
                  f"majority = {maj}  ties = {N_RUNS - n_nonties}  [{status}]")
            if scenario != "fixed" and rate < 0.90:
                overall_pass = False
        print()

    print("=" * 70)
    print("Overall verdict (non-trivial scenarios only):")
    if overall_pass:
        print("  G0.9 CLOSED — all combos pass agreement >= 0.90")
    else:
        print("  G0.9 FAILED — some combos below 0.90")
    print("=" * 70)


if __name__ == "__main__":
    main()
