"""HierarchicalInfoModel — architecture H."""
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)

from info_model import InfoModel, InformationSet


class HierarchicalInfoModel(InfoModel):
    """H: node sees cluster state + limited inter-cluster."""

    def __init__(self, n_clusters=2):
        self.n_clusters = n_clusters

    def gather(self, node, env, clock):
        cluster_id = env.cluster_of.get(self._node_idx(node), 0)
        local = env.get_cluster_state(cluster_id)
        return InformationSet(local=local)

    @staticmethod
    def _node_idx(node):
        # node_id is like "n_3"
        try:
            return int(node.node_id.split("_")[-1])
        except (ValueError, IndexError):
            return 0

    @property
    def name(self):
        return "Hierarchical"
