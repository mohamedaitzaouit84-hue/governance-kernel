"""Environment — single source of truth for V0.3 tests.

Minimal implementation. Not for production.
Only provides: global state, cluster state, neighbors, sensor readings.
"""
import random


class Environment:
    def __init__(self, n_nodes=6, n_clusters=2, seed=42):
        self.rng = random.Random(seed)
        self.n_nodes = n_nodes
        self.n_clusters = n_clusters
        # simple linear topology
        self.neighbors = {i: [(i - 1) % n_nodes, (i + 1) % n_nodes]
                          for i in range(n_nodes)}
        # cluster assignment
        self.cluster_of = {i: i % n_clusters for i in range(n_nodes)}
        self.true_signal = 1.0

    def get_global_state(self, delayed=False):
        # delayed: return previous step's value (for G0.4 style tests)
        if delayed:
            return self.true_signal * 0.9
        return self.true_signal

    def get_cluster_state(self, cluster_id):
        return self.true_signal + 0.05 * cluster_id

    def get_neighbors(self, node_id):
        out = []
        for n in self.neighbors[node_id]:
            noise = self.rng.gauss(0, 0.05)
            out.append((f"node_{n}", self.true_signal + noise))
        return out

    def sensor_reading(self, node_id):
        noise = self.rng.gauss(0, 0.1)
        return self.true_signal + noise
