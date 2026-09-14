"""G0.11 — Counterfactual Information Test.

Question: is the performance difference caused ONLY by information access?

Method:
1. For each (scenario, seed): run C, H, D under the SAME policy.
2. Record for each: info_size (observations count) and final_state.
3. Compute Pearson correlation between info_size and final_state.
4. Repeat across seeds.

Interpretation:
- If |corr| is small -> decisions do NOT depend on information access
  (architecture changes info, but not outcome). This is "counterfactual
  independence".
- If |corr| is large -> decisions ARE driven by information access.

Pass criterion: |corr| < 0.30 in drift/noise.
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
from separation.hierarchical_info import HierarchicalInfoModel
from separation.distributed_info import DistributedInfoModel
from separation.simple_policy import SimplePolicy
from separation.adaptive_policy import AdaptivePolicy


N_SEEDS = 30
N_STEPS = 50
SCENARIOS = ["drift", "noise"]


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


def run_and_measure(arch_key, pol_key, scenario, seed):
    """Return (mean_info_size, final_state)."""
    env = Environment(n_nodes=6, n_clusters=2, seed=seed, scenario=scenario)
    info = build_info(arch_key)
    pol = build_policy(pol_key)
    node = Node(node_id="n_3", info_model=info, policy=pol)

    info_sizes = []
    for step in range(N_STEPS):
        # capture info size BEFORE stepping
        iset = node.info_model.gather(node, env, step)
        info_sizes.append(iset.size())
        node.step(env=env, clock=step)

    mean_info = sum(info_sizes) / len(info_sizes)
    return mean_info, node.state


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx < 1e-12 or dy < 1e-12:
        return 0.0
    return num / (dx * dy)


def main():
    print("=" * 70)
    print("G0.11 — Counterfactual Information Test")
    print("=" * 70)
    print(f"Seeds: {N_SEEDS}, Steps: {N_STEPS}, Scenarios: {SCENARIOS}")
    print()

    overall_pass = True
    for scenario in SCENARIOS:
        print(f"--- Scenario: {scenario} ---")
        for pol_key in ["S", "A"]:
            infos = []
            states = []
            for i in range(N_SEEDS):
                seed = 11000 + i
                # cycle through architectures to vary info_size
                arch = ["C", "H", "D"][i % 3]
                mi, fs = run_and_measure(arch, pol_key, scenario, seed)
                infos.append(mi)
                states.append(fs)

            corr = pearson(infos, states)
            status = "PASS" if abs(corr) < 0.30 else "FAIL"
            if abs(corr) >= 0.30:
                overall_pass = False

            # summary stats
            mi_min = min(infos)
            mi_max = max(infos)
            print(f"  Policy={pol_key}: info_size range [{mi_min:.2f}, {mi_max:.2f}]  "
                  f"corr(info, state)={corr:+.3f}  [{status}]")
        print()

    print("=" * 70)
    print("Overall verdict:")
    if overall_pass:
        print("  G0.11 CLOSED — info access does not determine outcome")
    else:
        print("  G0.11 FAILED — outcome is coupled to info access")
    print("=" * 70)


if __name__ == "__main__":
    main()
