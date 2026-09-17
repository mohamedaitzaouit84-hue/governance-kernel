"""Multi-agent governance package (V0.6).

Implements cooperative task execution with trust-weighted consensus.
See docs/FREEZE_v0.6.md for scope, hypotheses, and thresholds.

No external dependencies. Python stdlib only.
"""

from .proposal import Proposal, Rejection, ProposalState
from .consensus import ConsensusError, weighted_vote, resolve

__all__ = [
    "Proposal",
    "Rejection",
    "ProposalState",
    "ConsensusError",
    "weighted_vote",
    "resolve",
]
