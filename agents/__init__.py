"""Governance Kernel — Agents package (V0.5).

Deterministic agents governed by the existing Kernel.
No new governance primitives. Only application of patterns P-L1, P-Q8, P-Q9.
"""

from .base_agent import BaseAgent, InvariantViolation

__all__ = ["BaseAgent", "InvariantViolation"]
