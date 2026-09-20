"""G0.24 — Collusion Handling (H26).

Criterion: 4/4 colluding-agent scenarios are handled correctly
(blocked, neutrally weighted, or producing correct outcomes).

Scenarios:
  C1: 2 agents always vote same way (bloc) — decision weighted,
      no bypass. Test that a 2-bloc cannot exceed weight cap.
  C2: 3 agents bypass proposer self-vote rule — self-vote still
      blocked even with coordinated voters.
  C3: Trust inflation before vote — weight still capped at 2.0.
  C4: Colluding voters exceed quorum safely — decisions still
      respect weighted majority, not headcount.

This test checks that collusion does NOT give disproportionate
influence. It does NOT detect collusion itself (that is out of
scope for P-Q12).

Read-only. No changes to V0.6 files.
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


def _proposal(i):
    p = Proposal(proposer="proposer_agent", action="x", payload={"i": i})
    p.state = ProposalState.VOTING
    return p


def c1_two_bloc_no_bypass():
    """C1: 2 colluding agents vote same. Verify total weight is
    bounded by 2*MAX_WEIGHT_PER_AGENT, not by count."""
    p = _proposal(1)
    # Two colluders with moderate trust
    v1 = weighted_vote("colluder_a", 0.5, p, "accept")
    v2 = weighted_vote("colluder_b", 0.5, p, "accept")
    p.votes = [v1, v2]
    total_accept = v1["weight"] + v2["weight"]
    # Bound check: 2 * MAX_WEIGHT_PER_AGENT
    bound = 2 * MAX_WEIGHT_PER_AGENT
    # The bloc cannot exceed this, regardless of trust inflation
    return total_accept <= bound


def c2_self_vote_blocked_with_colluders():
    """C2: Proposer tries self-vote while 2 colluders help.
    Self-vote must still be blocked."""
    p = _proposal(2)
    try:
        # Proposer self-vote must raise
        weighted_vote(p.proposer, 0.9, p, "accept")
        return False  # not blocked -> fail
    except ConsensusError:
        # Now add 2 colluders normally
        p.votes = [
            weighted_vote("colluder_a", 0.5, p, "accept"),
            weighted_vote("colluder_b", 0.5, p, "accept"),
        ]
        resolve(p)
        # Colluders alone = 1.0 accept, quorum satisfied,
        # outcome ACCEPTED. That's a valid decision.
        # Pass = self-vote was blocked.
        return p.state == ProposalState.ACCEPTED


def c3_trust_inflation_in_bloc():
    """C3: Colluders inflate their own trust. Must cap at 2.0."""
    p = _proposal(3)
    v1 = weighted_vote("colluder_a", 10.0, p, "accept")
    v2 = weighted_vote("colluder_b", 10.0, p, "accept")
    p.votes = [v1, v2]
    resolve(p)
    total = v1["weight"] + v2["weight"]
    expected_bound = 2 * MAX_WEIGHT_PER_AGENT
    return (total == expected_bound and
            p.state == ProposalState.ACCEPTED)


def c4_colluders_vs_honest():
    """C4: 2 colluders accept vs 2 honest reject, equal weight.
    Must result in tie -> REJECTED without owner."""
    p = _proposal(4)
    p.votes = [
        weighted_vote("colluder_a", 0.5, p, "accept"),
        weighted_vote("colluder_b", 0.5, p, "accept"),
        weighted_vote("honest_a", 0.5, p, "reject"),
        weighted_vote("honest_b", 0.5, p, "reject"),
    ]
    resolve(p)
    # 1.0 accept vs 1.0 reject -> tie -> REJECTED (no owner)
    return p.state == ProposalState.REJECTED


def main():
    attacks = [
        ("C1 two bloc no bypass", c1_two_bloc_no_bypass),
        ("C2 self-vote blocked", c2_self_vote_blocked_with_colluders),
        ("C3 trust inflation in bloc", c3_trust_inflation_in_bloc),
        ("C4 colluders vs honest", c4_colluders_vs_honest),
    ]

    passed = 0
    failed = []
    for name, fn in attacks:
        try:
            ok = bool(fn())
        except Exception as e:
            ok = False
            print("  {}: EXCEPTION {}".format(name, e))
        if ok:
            passed += 1
        else:
            failed.append(name)

    print("  Collusion scenarios: {}/{} handled".format(
        passed, len(attacks)))
    if failed:
        print("  NOT handled: {}".format(failed))

    if passed == len(attacks):
        print("G0.24: CLOSED ({}/{})".format(passed, len(attacks)))
        return 0
    else:
        print("G0.24: FAILED ({}/{})".format(passed, len(attacks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
