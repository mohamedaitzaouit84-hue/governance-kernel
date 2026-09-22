"""Coordinator V2 — drives the cooperative task with REAL V0.5 agents.

Implements V0.7.3 hypothesis H23:
  V0.5 agents can be coordinated by V0.6 protocol
  without modification.

Differs from coordinator.py (V0.6):
  - Uses real V0.5 agents instead of FakeAgent
  - Executes actions only after proposal is ACCEPTED
  - Real trust values from agent.trust
  - Real subject_ids from agent.subject_id

Task schema:
  input:  {"path": str, "a": int, "b": int, "output": str}
  output: {"file_content": ..., "compute_result": ...,
           "written_to": ...}

Read-only. Does NOT modify any V0.5 or V0.6 file.
"""

import time

from .proposal import Proposal, ProposalState
from .consensus import weighted_vote, resolve
from .communication import Channel


class CoordinatorV2Error(Exception):
    """Raised on invalid V0.7.3 coordination operations."""
    pass


class CoordinatorV2:
    """Coordinates real V0.5 agents through V0.6 consensus.

    Required agents:
      reader   — a real FileAgent
      computer — a real ComputeAgent
      writer   — a real QueryAgent

    The protocol runs first. The action runs only if ACCEPTED.
    """

    def __init__(self, reader, computer, writer, branch_id="br_v073"):
        # Verify real V0.5 agents (have .act, .trust, .subject_id)
        for role, agent in (
            ("reader", reader),
            ("computer", computer),
            ("writer", writer),
        ):
            for attr in ("act", "trust", "subject_id", "name"):
                if not hasattr(agent, attr):
                    raise CoordinatorV2Error(
                        "{} missing attribute: {}".format(role, attr)
                    )

        self.reader = reader
        self.computer = computer
        self.writer = writer
        self.branch_id = branch_id
        self.channel = Channel(branch_id=branch_id)
        self.cycles = []

    def _agents(self):
        return [self.reader, self.computer, self.writer]

    def _agent_id(self, agent):
        return agent.subject_id if agent.subject_id else agent.name

    def _trust_of(self, agent):
        return float(agent.trust)

    def _run_proposal(self, proposer, action, payload, voters):
        """Run a full proposal: create, vote, resolve.

        Does NOT execute. Execution is separate.
        Returns the resolved Proposal.
        """
        p = Proposal(
            proposer=self._agent_id(proposer),
            action=action,
            payload=payload,
        )
        p.state = ProposalState.VOTING

        for v in voters:
            v_id = self._agent_id(v)
            if v_id == p.proposer:
                continue  # self-vote blocked
            try:
                vote = weighted_vote(v_id, self._trust_of(v), p, "accept")
                p.votes.append(vote)
            except Exception:
                # Voter failed to vote (e.g. same id twice). Skip.
                continue

        resolve(p)
        return p

    def _execute(self, agent, action, payload):
        """Execute the action through the real V0.5 agent.

        Returns dict: {"ok": bool, "result": ..., "error": str|None}
        """
        try:
            result = agent.act(action, payload=payload)
            return {"ok": True, "result": result, "error": None}
        except Exception as e:
            return {
                "ok": False,
                "result": None,
                "error": "{}: {}".format(type(e).__name__, str(e)),
            }

    def run_task(self, task_input):
        """Run one cooperative task with real V0.5 agents.

        Phases:
          1. Read:    FileAgent proposes file_read
          2. Compute: ComputeAgent proposes compute_add
          3. Write:   QueryAgent proposes query_lookup

        Each phase:
          - Runs V0.6 proposal + weighted vote + resolve
          - Executes via agent.act() ONLY if ACCEPTED
          - Logs the decision and the execution result

        Returns dict:
          {"ok": bool, "cycles": [...], "result": {...}, "reason": str|None}
        """
        cycle_start = time.time()
        result = {
            "task_input": {
                k: task_input.get(k) for k in ("path", "a", "b", "output")
            },
            "file_content": None,
            "compute_result": None,
            "written_to": None,
        }

        # --- Phase 1: Read (FileAgent proposes file_read) ---
        read_p = self._run_proposal(
            proposer=self.reader,
            action="file_read",
            payload={"path": task_input.get("path", "input.txt")},
            voters=[self.computer, self.writer],
        )
        if read_p.state != ProposalState.ACCEPTED:
            return self._fail("read_not_accepted", read_p, cycle_start)

        read_exec = self._execute(
            self.reader,
            "file_read",
            {"path": task_input.get("path", "input.txt")},
        )
        if not read_exec["ok"]:
            return self._fail_exec("read_exec_failed", read_exec, cycle_start)
        result["file_content"] = read_exec["result"]

        # --- Phase 2: Compute (ComputeAgent proposes compute_add) ---
        compute_p = self._run_proposal(
            proposer=self.computer,
            action="compute_add",
            payload={"a": task_input.get("a", 0), "b": task_input.get("b", 0)},
            voters=[self.reader, self.writer],
        )
        if compute_p.state != ProposalState.ACCEPTED:
            return self._fail("compute_not_accepted", compute_p, cycle_start)

        compute_exec = self._execute(
            self.computer,
            "compute_add",
            {"a": task_input.get("a", 0), "b": task_input.get("b", 0)},
        )
        if not compute_exec["ok"]:
            return self._fail_exec("compute_exec_failed", compute_exec, cycle_start)
        result["compute_result"] = compute_exec["result"]

        # --- Phase 3: Write (QueryAgent proposes query_lookup) ---
        # QueryAgent is read-only, so we use query_lookup as its action.
        write_p = self._run_proposal(
            proposer=self.writer,
            action="query_lookup",
            payload={"key": task_input.get("output", "output.txt")},
            voters=[self.reader, self.computer],
        )
        if write_p.state != ProposalState.ACCEPTED:
            return self._fail("write_not_accepted", write_p, cycle_start)

        write_exec = self._execute(
            self.writer,
            "query_lookup",
            {"key": task_input.get("output", "output.txt")},
        )
        if not write_exec["ok"]:
            return self._fail_exec("write_exec_failed", write_exec, cycle_start)
        result["written_to"] = write_exec["result"]

        cycle = {
            "started_at": cycle_start,
            "sealed_at": time.time(),
            "read_commitment": read_p.commitment,
            "compute_commitment": compute_p.commitment,
            "write_commitment": write_p.commitment,
            "read_exec": read_exec,
            "compute_exec": compute_exec,
            "write_exec": write_exec,
            "ok": True,
        }
        self.cycles.append(cycle)
        return {"ok": True, "cycles": [cycle], "result": result, "reason": None}

    def _fail(self, reason, proposal, start):
        """Fail at proposal stage (not accepted)."""
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

    def _fail_exec(self, reason, exec_result, start):
        """Fail at execution stage (act() raised)."""
        cycle = {
            "started_at": start,
            "sealed_at": time.time(),
            "reason": reason,
            "exec_error": exec_result["error"],
            "ok": False,
        }
        self.cycles.append(cycle)
        return {"ok": False, "cycles": [cycle], "result": None, "reason": reason}

    def get_state(self):
        """Return coordination state (for introspection)."""
        return {
            "branch_id": self.branch_id,
            "n_cycles": len(self.cycles),
            "agents": [self._agent_id(a) for a in self._agents()],
            "trusts": [round(self._trust_of(a), 4) for a in self._agents()],
        }
