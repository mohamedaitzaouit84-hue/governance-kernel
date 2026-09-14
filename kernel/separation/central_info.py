"""CentralInfoModel — architecture C."""
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)

from info_model import InfoModel, InformationSet


class CentralInfoModel(InfoModel):
    """C: node sees global state (with optional delay)."""

    def __init__(self, delayed=False):
        self.delayed = delayed

    def gather(self, node, env, clock):
        return InformationSet(global_=env.get_global_state(clock=clock, delayed=self.delayed))

    @property
    def name(self):
        return "Central"
