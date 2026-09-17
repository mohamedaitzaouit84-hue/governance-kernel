"""Trust-Weighted Consensus — P-Q12.

Implements principles:
  2. Structural Integrity  — no self-vote, no double vote
  5. Double Attestation    — every decision logged in 2 places
  6. Invariant Laws        — quorum, weight cap, no self-vote (constants)
  7. Weighted Justice      — weight = trust, capped at 2.0
  8. Prior Estimation      — all constants from FREEZE_v0.6

Constants (frozen, from FREEZE_v0.6 section 5):
  MAX_WEIGHT_PER_AGENT = 2.0
  MIN_QUORUM = 2
  NO_SELF_VOTE = True

No external dependencies.
"""

import time
import json
from pathlib import Path

from .proposal import ProposalState, ProposalError, Rejection


# Constants — frozen in FREEZE_v0.6
MAX_WEIGHT_PER_AGENT = 2.0
MIN_QUORUM = 2
NO_SELF_VOTE = True
OWNER_ID = "owner"

# Second attestation ledger
_JOURNAL_PATH = Path(__file__).resolve().parent.parent.parent / "consensus" / "journal.jsonl"


class ConsensusError(Exception):
    """Raised on invalid consensus operations."""
    pass


def weighted_vote(agent_id, trust, proposal, choice):
    """Compute a single vote's weight.

    Rules:
      - weight = min(trust, MAX_WEIGHT_PER_AGENT)
      - no self-vote (proposer cannot vote on own proposal)
      - choice must be 'accept' or 'reject'

    Returns a vote dict. Raises ConsensusError on violation.
    """
    if choice not in ("accept", "reject"):
        raise ConsensusError("choice must be 'accept' or 'reject'")

    if NO_SELF_VOTE and agent_id == proposal.proposer:
        raise ConsensusError("self-vote forbidden: " + agent_id)

    if trust < 0:
        raise ConsensusError("trust must be non-negative")

    weight = min(float(trust), MAX_WEIGHT_PER_AGENT)

    return {
        "agent_id": agent_id,
        "choice": choice,
        "trust_at_vote": round(float(trust), 4),
        "weight": round(weight, 4),
        "at": time.time(),
    }


def _attest(proposal, decision, weights, reason):
    """Write the decision to the second attestation ledger."""
    record = {
        "proposal_id": proposal.id,
        "commitment": proposal.commitment,
        "decision": decision,
        "reason": reason,
        "n_votes": len(proposal.votes),
        "accept_weight": round(weights["accept"], 4),
        "reject_weight": round(weights["reject"], 4),
        "sealed_at": time.time(),
    }
    _JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    return record


def resolve(proposal, owner_signature=None):
    """Resolve a proposal given its votes.

    Rules:
      1. Requires MIN_QUORUM votes.
      2. Weighted sum decides.
      3. Ties broken by owner signature (if provided).
      4. No accept AND reject weights equal without signature.

    Mutates proposal.state, sets sealed_at, records rejection if rejected.
    Returns the attestation record.
    """
    if proposal.state != ProposalState.PENDING and proposal.state != ProposalState.VOTING:
        raise ConsensusError(
            "proposal not votable: state=" + proposal.state
        )

    if len(proposal.votes) < MIN_QUORUM:
        proposal.state = ProposalState.REJECTED
        proposal.sealed_at = time.time()
        proposal.rejection = Rejection(
            proposal_id=proposal.id,
            reason="insufficient quorum: " + str(len(proposal.votes)) + "/" + str(MIN_QUORUM),
        )
        return _attest(proposal, "REJECTED", {"accept": 0.0, "reject": 0.0}, "quorum")

    accept_w = 0.0
    reject_w = 0.0
    for v in proposal.votes:
        if v["choice"] == "accept":
            accept_w += v["weight"]
        else:
            reject_w += v["weight"]

    weights = {"accept": accept_w, "reject": reject_w}

    if accept_w > reject_w:
        proposal.state = ProposalState.ACCEPTED
        proposal.sealed_at = time.time()
        return _attest(proposal, "ACCEPTED", weights, "weighted_majority")

    if reject_w > accept_w:
        proposal.state = ProposalState.REJECTED
        proposal.sealed_at = time.time()
        proposal.rejection = Rejection(
            proposal_id=proposal.id,
            reason="weighted rejection: " + str(round(reject_w, 4)),
        )
        return _attest(proposal, "REJECTED", weights, "weighted_majority")

    # Tie
    if owner_signature:
        proposal.state = ProposalState.ACCEPTED
        proposal.sealed_at = time.time()
        return _attest(proposal, "ACCEPTED", weights, "owner_tiebreak")

    proposal.state = ProposalState.REJECTED
    proposal.sealed_at = time.time()
    proposal.rejection = Rejection(
        proposal_id=proposal.id,
        reason="tie without owner signature",
    )
    return _attest(proposal, "REJECTED", weights, "tie_no_owner")
