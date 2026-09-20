"""Benchmark harness for V0.7.2.

Measurement only. Uses time.perf_counter().
Does NOT modify V0.6 files.

Public functions:
  measure_cycle_time(n, agent_trusts)
  measure_consensus_time(n)
  measure_throughput(n_runs, batch_size)
  measure_memory(n_cycles)

All functions return a dict with: samples, median, min, max, std.
"""

import time
import statistics
import gc

from agents.multi.proposal import Proposal, ProposalState
from agents.multi.consensus import weighted_vote, resolve


def _stats(samples):
    if not samples:
        return {"n": 0, "median": 0, "min": 0, "max": 0, "std": 0}
    return {
        "n": len(samples),
        "median": statistics.median(samples),
        "min": min(samples),
        "max": max(samples),
        "std": statistics.pstdev(samples) if len(samples) > 1 else 0.0,
    }


def _one_cycle(trusts):
    """Run one Read -> Compute -> Write cycle (decision only).

    Simulates what coordinator does but without real agents.
    Returns True on success.
    """
    phases = [
        ("read", "proposer_a"),
        ("compute", "proposer_b"),
        ("write", "proposer_c"),
    ]
    for action, proposer in phases:
        p = Proposal(proposer=proposer, action=action, payload={"t": 1})
        p.state = ProposalState.VOTING
        # 2 voters, not the proposer
        voters = [t for t in trusts if t != proposer][:2]
        if len(voters) < 2:
            voters = trusts[:2]
        for voter in voters:
            trust = trusts[voter]
            try:
                p.votes.append(weighted_vote(voter, trust, p, "accept"))
            except Exception:
                pass
        resolve(p)
    return True


def measure_cycle_time(n, trusts):
    """Measure full cycle time (3 phases) in seconds.

    Returns dict with samples (seconds), median, min, max, std.
    """
    # Warm-up
    for _ in range(3):
        _one_cycle(trusts)
    gc.collect()

    samples = []
    for _ in range(n):
        t0 = time.perf_counter()
        _one_cycle(trusts)
        t1 = time.perf_counter()
        samples.append(t1 - t0)
    return _stats(samples)


def measure_consensus_time(n):
    """Measure single resolve() call in seconds."""
    # Warm-up
    for _ in range(3):
        p = Proposal(proposer="a", action="x", payload={})
        p.state = ProposalState.VOTING
        p.votes = [
            weighted_vote("b", 0.5, p, "accept"),
            weighted_vote("c", 0.5, p, "accept"),
        ]
        resolve(p)
    gc.collect()

    samples = []
    for _ in range(n):
        p = Proposal(proposer="a", action="x", payload={})
        p.state = ProposalState.VOTING
        p.votes = [
            weighted_vote("b", 0.5, p, "accept"),
            weighted_vote("c", 0.5, p, "accept"),
        ]
        t0 = time.perf_counter()
        resolve(p)
        t1 = time.perf_counter()
        samples.append(t1 - t0)
    return _stats(samples)


def measure_throughput(n_runs, batch_size, trusts):
    """Measure decisions per second over n_runs of batch_size decisions."""
    # Warm-up
    for _ in range(2):
        for _ in range(batch_size):
            _one_cycle(trusts)
    gc.collect()

    rates = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        for _ in range(batch_size):
            _one_cycle(trusts)
        t1 = time.perf_counter()
        elapsed = t1 - t0
        rate = batch_size / elapsed if elapsed > 0 else 0.0
        rates.append(rate)
    return _stats(rates)


def measure_memory(n_cycles, trusts):
    """Measure RSS delta after n_cycles.

    On Android/Termux, /proc/self/status is readable.
    Returns dict with rss_before_kb, rss_after_kb, delta_kb.
    """
    def _read_rss_kb():
        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        return int(parts[1])
        except Exception:
            return -1
        return -1

    gc.collect()
    rss_before = _read_rss_kb()

    for _ in range(n_cycles):
        _one_cycle(trusts)

    gc.collect()
    rss_after = _read_rss_kb()

    return {
        "n_cycles": n_cycles,
        "rss_before_kb": rss_before,
        "rss_after_kb": rss_after,
        "delta_kb": rss_after - rss_before if rss_before > 0 and rss_after > 0 else -1,
    }


# Default trusts for benchmark
DEFAULT_TRUSTS = {
    "proposer_a": 0.5,
    "proposer_b": 0.5,
    "proposer_c": 0.5,
    "voter_d": 0.5,
    "voter_e": 0.5,
}
