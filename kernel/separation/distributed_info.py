"""DistributedInfoModel — architecture D."""
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)

from info_model import InfoModel, InformationSet


class DistributedInfoModel(InfoModel):
    """D: node sees only its neighbors."""

    def gather(self, node, env, clock):
        idx = self._node_idx(node)
        nbrs = env.get_neighbors(idx, clock=clock)
        return InformationSet(neighbors=nbrs)

    @staticmethod
    def _node_idx(node):
        try:
            return int(node.node_id.split("_")[-1])
        except (ValueError, IndexError):
            return 0

    @property
    def name(self):
        return "Distributed"
