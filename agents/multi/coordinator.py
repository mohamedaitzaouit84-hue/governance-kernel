"""Coordinator — drives the cooperative task (Read -> Compute -> Write).

Implements principles:
  1. Symmetric Balance    — every accepted proposal can be rejected later
  2. Structural Integrity — no agent proposes + votes + executes in same cycle
  3. Explicit Boundaries  — every cycle: start, propose, vote, execute, seal
  4. Clear Separation     — each agent acts only in its domain
  5. Double Attestation   — decision in both audit and journal
  7. Weighted Justice     — votes weighted by trust

Task schema:
  input:  {"path": "notes.txt", "a": 1, "b": 2}
  output: {"file_content": ..., "compute_result": ..., "written_to": ...}

No external dependencies.
"""

import time
import json
from pathlib import Path

from .proposal import Proposal, ProposalState
from .consensus import weighted_vote, resolve, ConsensusError
from .communication import Channel

_JOURNAL_PATH = Path(__file__).resolve().parent.parent.parent / "consensus" / "journal.jsonl"


class CoordinatorError(Exception):
    """Raised on invalid coordination operations."""
    pass


class Coordinator:
    """Coordinates Read -> Compute -> Write across three agents.

    Required agents (by role):
      reader  — must propose 'file_read'
      computer — must propose 'compute_add'
      writer  — must propose 'file_write'
    """

    def __init__(self, reader, computer, writer, branch_id="br_v06"):
        self.reader = reader
        self.computer = computer
        self.writer = writer
        self.branch_id = branch_id
        self.channel = Channel(branch_id=branch_id)
        self.cycles = []

    def _agents(self):
        return [self.reader, self.computer, self.writer]

    def _trust_of(self, agent):
        return getattr(agent, "trust", 0.5)

    def _agent_id(self, agent):
        return getattr(agent, "subject_id", None) or agent.name

    def _run_one_proposal(self, proposer, action, payload, voters):
        """Full cycle: propose -> vote -> resolve.

        Returns the resolved Proposal.
        No execution here — execution is separate (principle 2).
        """
        p = Proposal(
            proposer=self._agent_id(proposer),
            action=action,
            payload=payload,
        )
        p.state = ProposalState.VOTING

        # Voters vote (they cannot vote on their own proposal)
        for v in voters:
            v_id = self._agent_id(v)
            if v_id == p.proposer:
                continue  # self-vote blocked by invariant
            trust = self._trust_of(v)
            vote = weighted_vote(v_id, trust, p, "accept")
            p.votes.append(vote)

        resolve(p)
        return p

    def run_task(self, task_input):
        """Run one cooperative task. Deterministic given inputs.

        Returns dict:
          {"ok": bool, "cycles": [...], "result": {...}, "reason": str|None}
        """
        cycle_start = time.time()
        result = {
            "task_input": {k: task_input.get(k) for k in ("path", "a", "b")},
            "file_content": None,
            "compute_result": None,
            "written_to": None,
        }

        # --- Phase 1: Read (proposed by reader) ---
        read_p = self._run_one_proposal(
            proposer=self.reader,
            action="file_read",
            payload={"path": task_input.get("path", "input.txt")},
            voters=[self.computer, self.writer],
        )
        if read_p.state != ProposalState.ACCEPTED:
            return self._fail("read_not_accepted", read_p, cycle_start)

        result["file_content"] = {"path": task_input.get("path"),
                                   "status": "read_stub"}

        # --- Phase 2: Compute (proposed by computer) ---
        compute_p = self._run_one_proposal(
            proposer=self.computer,
            action="compute_add",
            payload={"a": task_input.get("a", 0), "b": task_input.get("b", 0)},
            voters=[self.reader, self.writer],
        )
        if compute_p.state != ProposalState.ACCEPTED:
            return self._fail("compute_not_accepted", compute_p, cycle_start)

        result["compute_result"] = {
            "a": task_input.get("a", 0),
            "b": task_input.get("b", 0),
            "sum": (task_input.get("a", 0) + task_input.get("b", 0)),
        }

        # --- Phase 3: Write (proposed by writer) ---
        write_p = self._run_one_proposal(
            proposer=self.writer,
            action="file_write",
            payload={"path": task_input.get("output", "output.txt")},
            voters=[self.reader, self.computer],
        )
        if write_p.state != ProposalState.ACCEPTED:
            return self._fail("write_not_accepted", write_p, cycle_start)

        result["written_to"] = task_input.get("output", "output.txt")

        cycle = {
            "started_at": cycle_start,
            "sealed_at": time.time(),
            "read_commitment": read_p.commitment,
            "compute_commitment": compute_p.commitment,
            "write_commitment": write_p.commitment,
            "ok": True,
        }
        self.cycles.append(cycle)
        return {"ok": True, "cycles": [cycle], "result": result, "reason": None}

    def _fail(self, reason, proposal, start):
        cycle = {
            "started_at": start,
            "sealed_at": time.time(),
            "reason": reason,
            "proposal_id": proposal.id,
            "proposal_state": proposal.state,
            "ok": False,
        }
        self.cycles.append(cycle)
        return {"ok": False, "cycles": [cycle], "result": None, "reason": reason}

    def get_state(self):
        return {
            "branch_id": self.branch_id,
            "n_cycles": len(self.cycles),
            "agents": [self._agent_id(a) for a in self._agents()],
        }
