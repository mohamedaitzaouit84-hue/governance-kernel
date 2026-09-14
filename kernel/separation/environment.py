"""Environment — single source of truth for V0.3 tests.

Three scenarios:
- fixed: constant signal (control — should give kappa=1.0)
- drift: sinusoidal signal (varies over time)
- noise: gaussian noise around 0

Also: 20% of nodes are "noisy" and give inverted values.
"""
import math
import random


class Environment:
    def __init__(self, n_nodes=6, n_clusters=2, seed=42, scenario="drift"):
        self.rng = random.Random(seed)
        self.n_nodes = n_nodes
        self.n_clusters = n_clusters
        self.scenario = scenario

        # linear topology
        self.neighbors = {i: [(i - 1) % n_nodes, (i + 1) % n_nodes]
                          for i in range(n_nodes)}
        self.cluster_of = {i: i % n_clusters for i in range(n_nodes)}

        # 20% of nodes are noisy (give inverted value)
        n_noisy = max(1, int(0.2 * n_nodes))
        self.noisy_nodes = set(self.rng.sample(range(n_nodes), n_noisy))

    def _signal(self, clock):
        t = clock if clock is not None else 0
        if self.scenario == "fixed":
            return 1.0
        elif self.scenario == "drift":
            return math.sin(t * 0.15)
        elif self.scenario == "noise":
            return self.rng.gauss(0, 0.5)
        else:
            return 1.0

    def get_global_state(self, clock=None, delayed=False):
        return self._signal(clock)

    def get_cluster_state(self, cluster_id, clock=None):
        return self._signal(clock) + 0.05 * cluster_id

    def get_neighbors(self, node_id, clock=None):
        out = []
        for n in self.neighbors[node_id]:
            base = self._signal(clock)
            if n in self.noisy_nodes:
                val = -base  # noisy node gives inverted value
            else:
                val = base + self.rng.gauss(0, 0.05)
            out.append((f"node_{n}", val))
        return out
