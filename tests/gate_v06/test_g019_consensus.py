"""G0.19 — Weighted Consensus Prevents Single-Agent Control (H21).

Criterion: 20/20 single-agent control attempts are blocked.

Attack scenarios (each must end REJECTED or raise ConsensusError):
  1. Self-vote: proposer tries to vote on own proposal
  2. Lone vote: single agent tries to bypass quorum
  3. Duplicate vote: same agent votes twice
  4. Tie without owner: 0.5 vs 0.5, no owner signature
  5. Trust inflation: trust=5.0 must be capped at 2.0

After J-0.6.1 fix:
  - scenario 3 (duplicate) now correctly raises ConsensusError
  - scenario 5 uses cap to demonstrate trust bound

No external dependencies.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.proposal import Proposal, ProposalState
from agents.multi.consensus import (
    weighted_vote, resolve, ConsensusError, MAX_WEIGHT_PER_AGENT,
)


N_ATTACKS = 20


def _attempt(i):
    """Return True if single-agent control was correctly blocked."""
    p = Proposal(
        proposer="file_agent_1",
        action="file_read",
        payload={"path": "x_{}.txt".format(i)},
    )
    p.state = ProposalState.VOTING
    scenario = i % 5

    if scenario == 0:
        # Self-vote must be rejected by weighted_vote
        try:
            weighted_vote("file_agent_1", 0.85, p, "accept")
            return False  # not blocked — fail
        except ConsensusError:
            return True

    if scenario == 1:
        # Lone vote cannot satisfy quorum
        p.votes = [weighted_vote("compute_agent_1", 0.85, p, "accept")]
        resolve(p)
        return p.state == ProposalState.REJECTED

    if scenario == 2:
        # Duplicate vote by same agent must raise ConsensusError
        p.votes = [
            weighted_vote("compute_agent_1", 0.5, p, "accept"),
            weighted_vote("compute_agent_1", 0.5, p, "accept"),
        ]
        try:
            resolve(p)
            return False  # not blocked — fail
        except ConsensusError:
            return True

    if scenario == 3:
        # Tie without owner signature must be REJECTED
        p.votes = [
            weighted_vote("compute_agent_1", 0.5, p, "accept"),
            weighted_vote("query_agent_1", 0.5, p, "reject"),
        ]
        resolve(p)
        return p.state == ProposalState.REJECTED

    if scenario == 4:
        # Trust inflation is capped at MAX_WEIGHT_PER_AGENT
        v = weighted_vote("compute_agent_1", 5.0, p, "accept")
        return v["weight"] == MAX_WEIGHT_PER_AGENT

    return False


def main():
    results = [(i, _attempt(i)) for i in range(N_ATTACKS)]
    passed = sum(1 for _, ok in results if ok)
    failed = [i for i, ok in results if not ok]

    print("  Attempts: {}".format(N_ATTACKS))
    print("  Blocked:  {}/{}".format(passed, N_ATTACKS))
    if failed:
        print("  Not blocked: {}".format(failed))

    if passed == N_ATTACKS:
        print("G0.19: CLOSED ({}/{})".format(passed, N_ATTACKS))
        return 0
    else:
        print("G0.19: FAILED ({}/{})".format(passed, N_ATTACKS))
        return 1


if __name__ == "__main__":
    sys.exit(main())
