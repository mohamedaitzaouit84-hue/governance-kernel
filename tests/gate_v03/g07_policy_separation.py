"""G0.7 — Policy Separation test via Cohen's Kappa.

Question: Can we change Architecture without changing Policy, and vice versa?

Method:
- Run 6 combinations (C,H,D) x (S,A) under 3 scenarios.
- Each run: 100 steps, 30 runs per (scenario, combo).
- Compute Cohen's Kappa per run, average across runs.

Interpretation:
- Kappa(C-S, C-A) = Policy effect under Architecture C
- Kappa(D-S, D-A) = Policy effect under Architecture D
- If these two are SIMILAR → Policy is Architecture-independent
- If they DIFFER a lot → Policy is coupled to Architecture (separation fails)

Pass criterion (from FREEZE_v0.3): |Kappa_C - Kappa_D| < 0.2
Documented as CLOSED / FAILED / OPEN with SE reported.
"""
import sys
import math
from collections import Counter
from pathlib import Path

_here = Path(__file__).resolve().parent
_kernel = _here.parent.parent

sys.path.insert(0, str(_kernel / "kernel"))
sys.path.insert(0, str(_kernel / "kernel" / "separation"))

from separation.node import Node
from separation.environment import Environment
from separation.central_info import CentralInfoModel
from separation.hierarchical_info import HierarchicalInfoModel
from separation.distributed_info import DistributedInfoModel
from separation.simple_policy import SimplePolicy
from separation.adaptive_policy import AdaptivePolicy


N_RUNS = 30
N_STEPS = 100
SCENARIOS = ["fixed", "drift", "noise"]


def cohens_kappa(seq1, seq2):
    n = len(seq1)
    if n == 0 or n != len(seq2):
        return None
    p_o = sum(1 for a, b in zip(seq1, seq2) if a == b) / n
    c1 = Counter(seq1)
    c2 = Counter(seq2)
    cats = set(c1) | set(c2)
    p_e = sum((c1[k] / n) * (c2[k] / n) for k in cats)
    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1 - p_e)


def build_info(arch_key):
    if arch_key == "C":
        return CentralInfoModel()
    if arch_key == "H":
        return HierarchicalInfoModel(n_clusters=2)
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
    actions = []
    for step in range(N_STEPS):
        d = node.step(env=env, clock=step)
        actions.append(d.action)
    return actions


def mean_se(values):
    n = len(values)
    if n == 0:
        return None, None
    m = sum(values) / n
    if n == 1:
        return m, 0.0
    var = sum((v - m) ** 2 for v in values) / (n - 1)
    return m, math.sqrt(var / n)


def main():
    print("=" * 70)
    print("G0.7 — Policy Separation (Cohen's Kappa)")
    print("=" * 70)
    print(f"Runs: {N_RUNS}, Steps: {N_STEPS}, Scenarios: {SCENARIOS}")
    print()

    combos = [("C", "S"), ("C", "A"),
              ("H", "S"), ("H", "A"),
              ("D", "S"), ("D", "A")]

    all_results = {}

    for scenario in SCENARIOS:
        print(f"--- Scenario: {scenario} ---")

        results = {}
        for combo in combos:
            results[combo] = []
            for r in range(N_RUNS):
                seed = 1000 + r
                seq = run_combo(combo[0], combo[1], scenario, seed)
                results[combo].append(seq)

        comparisons = [
            (("C", "S"), ("C", "A"), "Policy effect | Architecture = C"),
            (("D", "S"), ("D", "A"), "Policy effect | Architecture = D"),
            (("H", "S"), ("H", "A"), "Policy effect | Architecture = H"),
            (("C", "S"), ("D", "S"), "Architecture effect | Policy = S"),
            (("C", "A"), ("D", "A"), "Architecture effect | Policy = A"),
        ]

        scenario_results = {}
        for c1, c2, label in comparisons:
            kappas = []
            for r in range(N_RUNS):
                k = cohens_kappa(results[c1][r], results[c2][r])
                if k is not None:
                    kappas.append(k)
            m, se = mean_se(kappas)
            scenario_results[(c1, c2)] = (m, se)
            print(f"  {label:35s}: kappa = {m:+.3f} ± {se:.3f}")

        # Separation check: Policy effect under C vs under D
        kC, seC = scenario_results[(("C","S"), ("C","A"))]
        kD, seD = scenario_results[(("D","S"), ("D","A"))]
        diff = abs(kC - kD)
        threshold = 0.2

        print()
        print(f"  |kappa_C - kappa_D| = {diff:.3f}   (threshold: {threshold})")
        if diff < threshold:
            print(f"  --> SEPARATION HOLDS (Policy is Architecture-independent)")
        else:
            print(f"  --> SEPARATION MAY FAIL (Policy effect differs by Architecture)")
        print()

        all_results[scenario] = scenario_results

    print("=" * 70)
    print("Overall verdict (based on non-trivial scenarios only):")
    non_trivial = ["drift", "noise"]
    for scen in non_trivial:
        sr = all_results[scen]
        kC, _ = sr[(("C","S"), ("C","A"))]
        kD, _ = sr[(("D","S"), ("D","A"))]
        diff = abs(kC - kD)
        status = "HOLDS" if diff < 0.2 else "MAY FAIL"
        print(f"  {scen:8s}: |kC - kD| = {diff:.3f}  --> {status}")
    print("=" * 70)


if __name__ == "__main__":
    main()
