"""G0.20 — Double Attestation (principle 5).

Criterion: 100% of decisions are recorded in consensus/journal.jsonl.

Principle 5 (Double Attestation): every sealed proposal produces
exactly one record in the secondary ledger (consensus/journal.jsonl).
The primary ledger is the audit chain (untouched by V0.6).

This test counts decisions made and journal entries written.
Any mismatch fails.

No external dependencies.
"""
import sys
import json
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.proposal import Proposal, ProposalState
from agents.multi.consensus import weighted_vote, resolve

# Path to the secondary ledger
JOURNAL_PATH = _repo / "consensus" / "journal.jsonl"


def _count_journal_lines():
    if not JOURNAL_PATH.exists():
        return 0
    with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
        return sum(1 for _ in f if _.strip())


N_DECISIONS = 30


def main():
    start_count = _count_journal_lines()

    # Produce N decisions, each sealed by resolve()
    decisions_made = 0
    for i in range(N_DECISIONS):
        p = Proposal(
            proposer="file_agent_1",
            action="file_read",
            payload={"path": "g20_{}.txt".format(i)},
        )
        p.state = ProposalState.VOTING

        # Alternate outcomes to cover both accept and reject
        if i % 3 == 0:
            # ACCEPTED via 2 accepts
            p.votes = [
                weighted_vote("compute_agent_1", 0.6, p, "accept"),
                weighted_vote("query_agent_1", 0.6, p, "accept"),
            ]
        elif i % 3 == 1:
            # REJECTED via 2 rejects
            p.votes = [
                weighted_vote("compute_agent_1", 0.6, p, "reject"),
                weighted_vote("query_agent_1", 0.6, p, "reject"),
            ]
        else:
            # REJECTED via quorum failure (only 1 vote)
            p.votes = [
                weighted_vote("compute_agent_1", 0.6, p, "accept"),
            ]

        resolve(p)
        decisions_made += 1

    end_count = _count_journal_lines()
    new_entries = end_count - start_count

    print("  Decisions made: {}".format(decisions_made))
    print("  Journal entries written: {}".format(new_entries))
    print("  Match: {}".format(new_entries == decisions_made))

    if new_entries == decisions_made:
        print("G0.20: CLOSED ({}/{})".format(new_entries, decisions_made))
        return 0
    else:
        print("G0.20: FAILED (mismatch)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
