"""InfoModel — abstract interface for Architecture.

Architecture controls ONLY: from where information comes.
Concrete classes: CentralInfoModel, HierarchicalInfoModel, DistributedInfoModel.
"""
from abc import ABC, abstractmethod


class InfoModel(ABC):
    """Abstract architecture.

    A Node holds one InfoModel. It does NOT know which concrete
    class it is. It only calls `gather()`.
    """

    @abstractmethod
    def gather(self, node, env, clock):
        """Return an InformationSet for this node.

        Args:
            node: the calling Node
            env:  the Environment (single source of truth)
            clock: simulation clock

        Returns:
            InformationSet
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name (for logs only, not for branching)."""
        raise NotImplementedError


class InformationSet:
    """Container for what a node knows at a given step.

    Fields are only populated for the relevant architecture:
    - local:      info from own cluster (hierarchical)
    - neighbors:  list of (source_id, value) (distributed)
    - global_:    global state (centralized)
    """

    def __init__(self, local=None, neighbors=None, global_=None):
        self.local = local
        self.neighbors = list(neighbors) if neighbors else []
        self.global_ = global_

    def all_observations(self):
        """Flatten to list of (source, value) for policies to consume."""
        out = []
        if self.global_ is not None:
            out.append(("global", self.global_))
        if self.local is not None:
            out.append(("local", self.local))
        out.extend(self.neighbors)
        return out

    def size(self) -> int:
        return len(self.all_observations())

    def __repr__(self):
        return (f"InformationSet(global_={self.global_}, "
                f"local={self.local}, "
                f"neighbors={len(self.neighbors)})")
