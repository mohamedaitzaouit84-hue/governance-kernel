"""Proposal — a proposed action in the multi-agent system.

Implements principles:
  1. Symmetric Balance   — every Proposal has a Rejection record
  2. Structural Integrity — state transitions are explicit
  3. Explicit Boundaries — has created_at and (eventually) sealed_at
  8. Prior Estimation    — all constants from FREEZE_v0.6

No external dependencies.
"""

import time
import uuid
import hashlib
import json


class ProposalState:
    """Allowed states of a proposal. Explicit, closed set."""
    PENDING  = "PENDING"
    VOTING   = "VOTING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    ALL = {PENDING, VOTING, ACCEPTED, REJECTED, EXECUTED}


class ProposalError(Exception):
    """Raised on invalid proposal operations."""
    pass


class Rejection:
    """Symmetric counterpart to a Proposal (principle 1)."""

    def __init__(self, proposal_id, reason, by_agent=None):
        self.proposal_id = proposal_id
        self.reason = reason
        self.by_agent = by_agent
        self.at = time.time()

    def to_dict(self):
        return {
            "proposal_id": self.proposal_id,
            "reason": self.reason,
            "by_agent": self.by_agent,
            "at": self.at,
        }


class Proposal:
    """A proposal to execute an action.

    Fields:
      id            unique proposal identifier
      proposer      agent that proposed
      action        the action string (e.g. "file_read")
      payload       action-specific data
      state         one of ProposalState.ALL
      created_at    unix timestamp
      sealed_at     None until decided
      votes         list of Vote dicts
      rejection     None or Rejection
    """

    def __init__(self, proposer, action, payload=None):
        if not proposer or not action:
            raise ProposalError("proposer and action are required")

        self.id = "prop_" + uuid.uuid4().hex[:12]
        self.proposer = proposer
        self.action = action
        self.payload = payload or {}
        self.state = ProposalState.PENDING
        self.created_at = time.time()
        self.sealed_at = None
        self.votes = []
        self.rejection = None
        self._commitment = self._compute_commitment()

    def _compute_commitment(self):
        """Deterministic hash of the proposal content."""
        body = json.dumps({
            "id": self.id,
            "proposer": self.proposer,
            "action": self.action,
            "payload_keys": sorted(self.payload.keys()),
            "created_at": self.created_at,
        }, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(body).hexdigest()

    @property
    def commitment(self):
        """Immutable content hash. Used for double attestation."""
        return self._commitment

    def is_final(self):
        return self.state in {
            ProposalState.ACCEPTED,
            ProposalState.REJECTED,
            ProposalState.EXECUTED,
        }

    def to_dict(self):
        return {
            "id": self.id,
            "proposer": self.proposer,
            "action": self.action,
            "payload_keys": sorted(self.payload.keys()),
            "state": self.state,
            "created_at": self.created_at,
            "sealed_at": self.sealed_at,
            "commitment": self.commitment,
            "votes": list(self.votes),
            "rejection": self.rejection.to_dict() if self.rejection else None,
        }
